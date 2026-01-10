// WebRTC Call Management - Group Video/Audio Calls with Screen Sharing and Recording
let currentCall = null;
let localStream = null;
let screenShareStream = null;
let processedLocalStream = null; // Stream with background effects
let peerConnections = {}; // {userId: RTCPeerConnection}
let remoteStreams = {}; // {userId: MediaStream}
let currentCallType = null; // 'video' or 'audio'
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;
window.isRecordingCall = false; // Global flag for call recording state
let isScreenSharing = false;
let backgroundEffect = 'none'; // 'none', 'blur', 'image'
let backgroundImage = null;
let backgroundCanvas = null;
let backgroundContext = null;
let backgroundVideo = null;
let recordingCanvas = null;
let recordingContext = null;
let recordingAnimationFrame = null;
let recordingStartTime = null;
let recordingTimerInterval = null;
let isCallModalMinimized = false;
let remoteAudioElements = {}; // {userId: HTMLAudioElement}

const STUN_SERVERS = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
    ]
};

function initCalls() {
    if (!socket) {
        console.error('Socket not initialized');
        return;
    }
    
    // Listen for call events
    socket.on('incoming_call', handleIncomingCall);
    socket.on('call_accepted', handleCallAccepted);
    socket.on('call_rejected', handleCallRejected);
    socket.on('call_ended', handleCallEnded);
    socket.on('call_offer', handleCallOffer);
    socket.on('call_answer', handleCallAnswer);
    socket.on('call_ice_candidate', handleIceCandidate);
    socket.on('call_error', handleCallError);
    socket.on('participant_joined', handleParticipantJoined);
    socket.on('participant_left', handleParticipantLeft);
}

function initiateCall(userId, userName, type = 'video') {
    if (currentCall) {
        // If already in a call, add participant to existing call
        addParticipantToCall(userId);
        return;
    }
    
    currentCallType = type;
    currentCall = {
        callId: null,
        participants: [{
            id: CURRENT_USER_ID,
            name: 'You',
            isLocal: true
        }, {
            id: userId,
            name: userName,
            isLocal: false
        }],
        type: type,
        isGroup: false
    };
    
    // Show calling UI
    showCallModal('outgoing', userName, type);
    
    // Request media
    getLocalMedia(type).then(() => {
        // Emit initiate call
        socket.emit('initiate_call', {
            callee_id: userId,
            type: type
        }, (response) => {
            if (response && response.call_id) {
                currentCall.callId = response.call_id;
                // Don't create peer connection yet - wait for callee to accept
                updateCallUI();
            }
        });
    }).catch(err => {
        console.error('Error getting local media:', err);
        hideCallModal();
        alert('Error accessing camera/microphone: ' + err.message);
        currentCall = null;
    });
}

function addParticipantToCall(userId) {
    if (!currentCall || !currentCall.callId) return;
    
    socket.emit('add_participant', {
        call_id: currentCall.callId,
        user_id: userId
    });
}

function handleIncomingCall(data) {
    const { call_id, caller_id, caller_name, type, participants } = data;
    
    currentCall = {
        callId: call_id,
        participants: participants || [{
            id: caller_id,
            name: caller_name,
            isLocal: false
        }, {
            id: CURRENT_USER_ID,
            name: 'You',
            isLocal: true
        }],
        type: type,
        isGroup: (participants && participants.length > 2) || false
    };
    currentCallType = type;
    
    // Show incoming call UI
    showCallModal('incoming', caller_name, type);
    playRingtone();
}

function acceptCall() {
    if (!currentCall || !currentCall.callId) {
        return;
    }
    
    const type = currentCall.type;
    
    // Get local media
    getLocalMedia(type).then(() => {
        // Accept call
        socket.emit('accept_call', {
            call_id: currentCall.callId
        });
        
        // Update UI
        updateCallModal('active', null, type);
        updateCallUI();
        stopRingtone();
        
        // Don't create peer connection here - wait for caller's offer
        // The caller will create peer connection and send offer after receiving call_accepted
    }).catch(err => {
        console.error('Error getting local media:', err);
        rejectCall();
        alert('Error accessing camera/microphone: ' + err.message);
    });
}

function rejectCall() {
    if (!currentCall || !currentCall.callId) {
        return;
    }
    
    socket.emit('reject_call', {
        call_id: currentCall.callId
    });
    
    cleanupCall();
}

function endCall() {
    if (!currentCall || !currentCall.callId) {
        return;
    }
    
    socket.emit('end_call', {
        call_id: currentCall.callId
    });
    
    cleanupCall();
}

function handleCallAccepted(data) {
    if (!currentCall) return;
    
    const { call_id, callee_id, callee_name } = data;
    
    // Add participant to call
    if (!currentCall.participants.find(p => p.id === callee_id)) {
        currentCall.participants.push({
            id: callee_id,
            name: callee_name,
            isLocal: false
        });
    }
    
    // Create peer connection with callee and send offer (caller side)
    if (!peerConnections[callee_id]) {
        createPeerConnection(callee_id, true);
    }
    
    updateCallModal('active', null, currentCallType);
    updateCallUI();
}

function handleCallRejected(data) {
    cleanupCall();
    alert('Call was rejected');
}

function handleCallEnded(data) {
    cleanupCall();
}

function handleParticipantJoined(data) {
    if (!currentCall) return;
    
    const { user_id, user_name } = data;
    
    // Add participant to call
    if (!currentCall.participants.find(p => p.id === user_id)) {
        currentCall.participants.push({
            id: user_id,
            name: user_name,
            isLocal: false
        });
        currentCall.isGroup = currentCall.participants.length > 2;
        
        // Create peer connection and send offer to new participant
        if (!peerConnections[user_id]) {
            createPeerConnection(user_id, true);
        }
        
        updateCallUI();
    }
}

function handleParticipantLeft(data) {
    if (!currentCall) return;
    
    const { user_id } = data;
    
    // Remove participant
    currentCall.participants = currentCall.participants.filter(p => p.id !== user_id);
    
    // Close peer connection
    if (peerConnections[user_id]) {
        peerConnections[user_id].close();
        delete peerConnections[user_id];
    }
    
    // Remove remote stream
    if (remoteStreams[user_id]) {
        delete remoteStreams[user_id];
    }
    
    updateCallUI();
    
    // If no other participants, end call
    if (currentCall.participants.length === 1) {
        endCall();
    }
}

function handleCallOffer(data) {
    if (!currentCall) return;
    
    const { offer, from_user_id } = data;
    
    // Create peer connection if it doesn't exist
    if (!peerConnections[from_user_id]) {
        createPeerConnection(from_user_id, false);
    }
    
    const pc = peerConnections[from_user_id];
    
    // Set remote description and create answer
    pc.setRemoteDescription(new RTCSessionDescription(offer))
        .then(() => {
            return pc.createAnswer();
        })
        .then(answer => {
            return pc.setLocalDescription(answer);
        })
        .then(() => {
            socket.emit('call_answer', {
                call_id: currentCall.callId,
                to_user_id: from_user_id,
                answer: pc.localDescription
            });
        })
        .catch(err => {
            console.error('Error handling offer:', err);
        });
}

function handleCallAnswer(data) {
    const { answer, from_user_id } = data;
    
    if (!peerConnections[from_user_id]) {
        console.warn('Received answer but no peer connection for', from_user_id);
        return;
    }
    
    const pc = peerConnections[from_user_id];
    pc.setRemoteDescription(new RTCSessionDescription(answer))
        .catch(err => {
            console.error('Error setting remote description:', err);
        });
}

function handleIceCandidate(data) {
    const { candidate, from_user_id } = data;
    
    if (!peerConnections[from_user_id]) return;
    
    const pc = peerConnections[from_user_id];
    if (candidate) {
        pc.addIceCandidate(new RTCIceCandidate(candidate))
            .catch(err => {
                console.error('Error adding ICE candidate:', err);
            });
    }
}

function handleCallError(data) {
    cleanupCall();
    alert(data.message || 'Call error occurred');
}

async function getLocalMedia(type) {
    const constraints = {
        audio: true,
        video: type === 'video' ? {
            width: { ideal: 1280 },
            height: { ideal: 720 }
        } : false
    };
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        localStream = stream;
        
        // Process stream for background effects if video
        if (type === 'video') {
            await processLocalStream();
        } else {
            processedLocalStream = stream;
        }
        
        updateLocalVideo();
        return stream;
    } catch (err) {
        console.error('Error getting local media:', err);
        throw err;
    }
}

async function processLocalStream() {
    if (!localStream) return;
    
    if (backgroundEffect === 'none') {
        processedLocalStream = localStream;
        updateLocalVideo();
        updatePeerConnectionsTracks();
        return;
    }
    
    // For blur or background image, we'll use a simplified approach
    // Note: Full background removal requires ML models or external libraries
    // This is a placeholder that can be enhanced with libraries like BodyPix or MediaPipe
    
    if (backgroundEffect === 'blur') {
        // Use CSS filter for blur (simplified approach)
        // For real-time video blur, you'd need Canvas + filter or a WebGL shader
        processedLocalStream = localStream;
    } else if (backgroundEffect === 'image') {
        // Virtual background with image
        processedLocalStream = localStream;
    }
    
    updateLocalVideo();
    updatePeerConnectionsTracks();
}

function updatePeerConnectionsTracks() {
    if (!processedLocalStream) return;
    
    Object.keys(peerConnections).forEach(userId => {
        const pc = peerConnections[userId];
        processedLocalStream.getTracks().forEach(track => {
            const sender = pc.getSenders().find(s => 
                s.track && s.track.kind === track.kind
            );
            if (sender) {
                sender.replaceTrack(track);
            } else {
                pc.addTrack(track, processedLocalStream);
            }
        });
    });
}

function createPeerConnection(userId, isCaller) {
    // Don't create duplicate connections
    if (peerConnections[userId]) {
        console.log('Peer connection already exists for', userId);
        return peerConnections[userId];
    }
    
    console.log('Creating peer connection with', userId, 'isCaller:', isCaller);
    const pc = new RTCPeerConnection(STUN_SERVERS);
    peerConnections[userId] = pc;
    
    // Add local stream tracks
    const streamToUse = processedLocalStream || localStream;
    if (streamToUse) {
        streamToUse.getTracks().forEach(track => {
            console.log('Adding local track:', track.kind, 'to peer connection with', userId);
            pc.addTrack(track, streamToUse);
        });
    } else {
        console.warn('No local stream available when creating peer connection');
    }
    
    // Add screen share stream if active
    if (screenShareStream) {
        screenShareStream.getTracks().forEach(track => {
            pc.addTrack(track, screenShareStream);
        });
    }
    
    // Handle remote stream
    pc.ontrack = (event) => {
        console.log('✅ Received track from', userId, event);
        const stream = event.streams[0] || event.stream;
        if (stream) {
            remoteStreams[userId] = stream;
            console.log('Remote stream set for', userId, 'tracks:', stream.getTracks().length);
            
            // Update UI immediately
            updateCallUI();
            
            // Also try to update video element if it exists
            setTimeout(() => {
                updateRemoteVideo(userId, stream);
            }, 100);
        }
    };
    
    // Handle ICE candidates
    pc.onicecandidate = (event) => {
        if (event.candidate && currentCall && currentCall.callId) {
            socket.emit('call_ice_candidate', {
                call_id: currentCall.callId,
                to_user_id: userId,
                candidate: event.candidate
            });
        }
    };
    
    // Handle connection state changes
    pc.onconnectionstatechange = () => {
        console.log(`Connection state with ${userId}:`, pc.connectionState);
        if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
            console.warn(`Connection with ${userId} failed or disconnected`);
        }
    };
    
    // Handle ICE connection state
    pc.oniceconnectionstatechange = () => {
        console.log(`ICE connection state with ${userId}:`, pc.iceConnectionState);
    };
    
    // Create offer if caller
    if (isCaller) {
        pc.createOffer({
            offerToReceiveAudio: true,
            offerToReceiveVideo: currentCallType === 'video'
        })
            .then(offer => {
                console.log('Created offer for', userId);
                return pc.setLocalDescription(offer);
            })
            .then(() => {
                socket.emit('call_offer', {
                    call_id: currentCall.callId,
                    to_user_id: userId,
                    offer: pc.localDescription
                });
                console.log('Sent offer to', userId);
            })
            .catch(err => {
                console.error('Error creating offer:', err);
            });
    }
    
    return pc;
}

async function startScreenShare() {
    try {
        screenShareStream = await navigator.mediaDevices.getDisplayMedia({
            video: true,
            audio: true
        });
        
        isScreenSharing = true;
        
        // Replace video tracks in all peer connections
        Object.keys(peerConnections).forEach(userId => {
            const pc = peerConnections[userId];
            screenShareStream.getVideoTracks().forEach(track => {
                const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
                if (sender) {
                    sender.replaceTrack(track);
                }
            });
        });
        
        // Update UI
        updateScreenShareButton(true);
        updateLocalVideo();
        
        // Handle screen share end
        screenShareStream.getVideoTracks()[0].onended = () => {
            stopScreenShare();
        };
    } catch (err) {
        console.error('Error starting screen share:', err);
        alert('Error starting screen share: ' + err.message);
    }
}

function stopScreenShare() {
    if (!screenShareStream) return;
    
    screenShareStream.getTracks().forEach(track => track.stop());
    screenShareStream = null;
    isScreenSharing = false;
    
    // Switch back to camera
    const streamToUse = processedLocalStream || localStream;
    if (streamToUse) {
        const videoTrack = streamToUse.getVideoTracks()[0];
        if (videoTrack) {
            Object.keys(peerConnections).forEach(userId => {
                const pc = peerConnections[userId];
                const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
                if (sender) {
                    sender.replaceTrack(videoTrack);
                }
            });
        }
    }
    
    updateScreenShareButton(false);
    updateLocalVideo();
    
    // Ensure modal is not minimized after stopping screen share
    if (isCallModalMinimized) {
        toggleCallModalMinimize(); // Restore to full size
    }
}

function startCallRecording() {
    if (!localStream || isRecording) return;
    
    console.log('Starting recording...');
    
    // Get or create a container for recording video elements
    // Note: Container must be in viewport (even if tiny) for canvas capture to work in some browsers
    let recordingContainer = document.getElementById('recordingVideoContainer');
    if (!recordingContainer) {
        recordingContainer = document.createElement('div');
        recordingContainer.id = 'recordingVideoContainer';
        // Position in viewport but make it tiny and clip it - required for canvas capture
        recordingContainer.style.cssText = 'position: fixed; top: 0; left: 0; width: 1280px; height: 720px; z-index: -9999; opacity: 1; pointer-events: none; background: #000; visibility: visible; clip-path: inset(100% 100% 0 0); overflow: hidden;';
        document.body.appendChild(recordingContainer);
    } else {
        // Make sure container is in viewport but clipped
        recordingContainer.style.top = '0';
        recordingContainer.style.left = '0';
        recordingContainer.style.opacity = '1';
        recordingContainer.style.visibility = 'visible';
        recordingContainer.style.zIndex = '-9999';
        recordingContainer.style.clipPath = 'inset(100% 100% 0 0)';
        recordingContainer.style.overflow = 'hidden';
    }
    
    // Create canvas for compositing all streams
    recordingCanvas = document.createElement('canvas');
    recordingCanvas.width = 1280;
    recordingCanvas.height = 720;
    recordingContext = recordingCanvas.getContext('2d');
    recordingCanvas.style.cssText = 'position: absolute; top: 0; left: 0;';
    recordingContainer.appendChild(recordingCanvas);
    
    const videoElements = {};
    const createdVideoElements = [];
    
    // Get local stream
    const localStreamToUse = isScreenSharing ? screenShareStream : (processedLocalStream || localStream);
    if (!localStreamToUse) {
        console.error('No local stream available for recording');
        alert('Cannot start recording: No video stream available');
        return;
    }
    
    // Create local video element for recording
    const localVideo = document.createElement('video');
    localVideo.srcObject = localStreamToUse;
    localVideo.muted = true; // Mute local video to avoid echo
    localVideo.autoplay = true;
    localVideo.playsInline = true;
    localVideo.setAttribute('playsinline', 'true');
    localVideo.width = 640;
    localVideo.height = 480;
    localVideo.style.cssText = 'position: absolute; top: 0; left: 0; width: 640px; height: 480px; object-fit: cover; background: #000;';
    recordingContainer.appendChild(localVideo);
    videoElements.local = localVideo;
    createdVideoElements.push(localVideo);
    
    // Create remote video elements
    Object.keys(remoteStreams).forEach(userId => {
        const remoteVideo = document.createElement('video');
        remoteVideo.srcObject = remoteStreams[userId];
        remoteVideo.muted = false;
        remoteVideo.autoplay = true;
        remoteVideo.playsInline = true;
        remoteVideo.setAttribute('playsinline', 'true');
        remoteVideo.width = 640;
        remoteVideo.height = 480;
        
        // Position based on number of streams
        const remoteIndex = Object.keys(videoElements).length;
        const totalStreams = Object.keys(remoteStreams).length + 1; // +1 for local
        
        if (totalStreams === 1) {
            remoteVideo.style.cssText = 'position: absolute; top: 0; left: 0; width: 1280px; height: 720px; object-fit: cover; background: #000;';
        } else if (totalStreams === 2) {
            remoteVideo.style.cssText = `position: absolute; top: 0; left: ${remoteIndex === 1 ? '640px' : '0'}; width: 640px; height: 720px; object-fit: cover; background: #000;`;
        } else {
            const cols = Math.ceil(Math.sqrt(totalStreams));
            const col = remoteIndex % cols;
            const row = Math.floor(remoteIndex / cols);
            const cellWidth = 1280 / cols;
            const cellHeight = 720 / Math.ceil(totalStreams / cols);
            remoteVideo.style.cssText = `position: absolute; top: ${row * cellHeight}px; left: ${col * cellWidth}px; width: ${cellWidth}px; height: ${cellHeight}px; object-fit: cover; background: #000;`;
        }
        
        recordingContainer.appendChild(remoteVideo);
        videoElements[userId] = remoteVideo;
        createdVideoElements.push(remoteVideo);
    });
    
    console.log('Created', Object.keys(videoElements).length, 'video elements for recording');
    
    // Position local video based on total count
    const totalStreams = Object.keys(videoElements).length;
    if (totalStreams === 1) {
        localVideo.style.cssText = 'position: absolute; top: 0; left: 0; width: 1280px; height: 720px;';
    } else if (totalStreams === 2) {
        localVideo.style.cssText = 'position: absolute; top: 0; left: 0; width: 640px; height: 720px;';
    } else {
        const cols = Math.ceil(Math.sqrt(totalStreams));
        const cellWidth = 1280 / cols;
        const cellHeight = 720 / Math.ceil(totalStreams / cols);
        localVideo.style.cssText = `position: absolute; top: 0; left: 0; width: ${cellWidth}px; height: ${cellHeight}px;`;
    }
    
    // Wait for all videos to be ready and playing
    const videoPromises = Object.entries(videoElements).map(([key, video]) => {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error(`Timeout waiting for video: ${key}`));
            }, 5000);
            
            const checkReady = () => {
                if (video.readyState >= 2 && video.videoWidth > 0 && video.videoHeight > 0) {
                    clearTimeout(timeout);
                    console.log(`Video ready for recording: ${key}`, video.videoWidth, 'x', video.videoHeight);
                    resolve();
                } else {
                    requestAnimationFrame(checkReady);
                }
            };
            
            video.addEventListener('loadedmetadata', () => {
                video.play().then(() => {
                    setTimeout(checkReady, 100);
                }).catch(err => {
                    console.warn('Error playing video for recording:', key, err);
                    setTimeout(checkReady, 100);
                });
            }, { once: true });
            
            // If already has metadata, check immediately
            if (video.readyState >= 1) {
                video.play().then(() => {
                    setTimeout(checkReady, 100);
                }).catch(err => {
                    console.warn('Error playing video for recording:', key, err);
                    setTimeout(checkReady, 100);
                });
            }
        });
    });
    
    Promise.all(videoPromises).then(() => {
        console.log('All videos ready, starting canvas drawing and MediaRecorder');
        
        // Start drawing loop
        function drawFrame() {
            if (!isRecording) return;
            
            // Clear canvas
            recordingContext.fillStyle = '#000';
            recordingContext.fillRect(0, 0, recordingCanvas.width, recordingCanvas.height);
            
            const streamKeys = Object.keys(videoElements);
            const count = streamKeys.length;
            
            if (count === 1) {
                // Single stream - full screen
                const video = videoElements[streamKeys[0]];
                if (video && video.readyState >= 2 && video.videoWidth > 0 && video.videoHeight > 0) {
                    try {
                        recordingContext.drawImage(video, 0, 0, recordingCanvas.width, recordingCanvas.height);
                    } catch (e) {
                        console.warn('Error drawing video:', e);
                    }
                }
            } else if (count === 2) {
                // Two streams - side by side
                const video1 = videoElements[streamKeys[0]];
                const video2 = videoElements[streamKeys[1]];
                if (video1 && video1.readyState >= 2 && video1.videoWidth > 0 && video1.videoHeight > 0) {
                    try {
                        recordingContext.drawImage(video1, 0, 0, recordingCanvas.width / 2, recordingCanvas.height);
                    } catch (e) {
                        console.warn('Error drawing video1:', e);
                    }
                }
                if (video2 && video2.readyState >= 2 && video2.videoWidth > 0 && video2.videoHeight > 0) {
                    try {
                        recordingContext.drawImage(video2, recordingCanvas.width / 2, 0, recordingCanvas.width / 2, recordingCanvas.height);
                    } catch (e) {
                        console.warn('Error drawing video2:', e);
                    }
                }
            } else {
                // Multiple streams - grid layout
                const cols = Math.ceil(Math.sqrt(count));
                const rows = Math.ceil(count / cols);
                const cellWidth = recordingCanvas.width / cols;
                const cellHeight = recordingCanvas.height / rows;
                
                streamKeys.forEach((key, index) => {
                    const video = videoElements[key];
                    if (video && video.readyState >= 2 && video.videoWidth > 0 && video.videoHeight > 0) {
                        try {
                            const col = index % cols;
                            const row = Math.floor(index / cols);
                            recordingContext.drawImage(video, col * cellWidth, row * cellHeight, cellWidth, cellHeight);
                        } catch (e) {
                            console.warn('Error drawing video:', key, e);
                        }
                    }
                });
            }
            
            recordingAnimationFrame = requestAnimationFrame(drawFrame);
        }
        
        // Start drawing loop
        drawFrame();
        
        // Create canvas stream
        const combinedStream = recordingCanvas.captureStream(30);
        
        // Combine audio from all streams using AudioContext
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const destination = audioContext.createMediaStreamDestination();
        
        // Add local audio
        if (localStreamToUse && localStreamToUse.getAudioTracks().length > 0) {
            const localAudioSource = audioContext.createMediaStreamSource(localStreamToUse);
            localAudioSource.connect(destination);
        }
        
        // Add remote audios
        Object.values(remoteStreams).forEach(stream => {
            if (stream && stream.getAudioTracks().length > 0) {
                const remoteAudioSource = audioContext.createMediaStreamSource(stream);
                remoteAudioSource.connect(destination);
            }
        });
        
        // Add combined audio to canvas stream
        destination.stream.getAudioTracks().forEach(track => {
            combinedStream.addTrack(track);
        });
        
        // Start recording
        recordedChunks = [];
        const options = {
            mimeType: 'video/webm;codecs=vp9,opus',
            videoBitsPerSecond: 2500000
        };
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = 'video/webm;codecs=vp8,opus';
        }
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = 'video/webm';
        }
        
        mediaRecorder = new MediaRecorder(combinedStream, options);
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = async () => {
            console.log('Recording stopped');
            // Stop drawing
            if (recordingAnimationFrame) {
                cancelAnimationFrame(recordingAnimationFrame);
            }
            
            // Clean up video elements
            createdVideoElements.forEach(video => {
                video.srcObject = null;
                video.remove();
            });
            
            // Clean up canvas and container
            if (recordingCanvas) {
                recordingCanvas.remove();
                recordingCanvas = null;
                recordingContext = null;
            }
            
            // Clean up recording container (keep it for next recording but clip it)
            const recordingContainer = document.getElementById('recordingVideoContainer');
            if (recordingContainer) {
                recordingContainer.style.clipPath = 'inset(100% 100% 0 0)';
                recordingContainer.style.opacity = '0';
            }
            
            // Close audio context
            if (audioContext) {
                audioContext.close().catch(console.error);
            }
            
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            await downloadRecordingAsZip(blob);
        };
        
        mediaRecorder.start(1000);
        isRecording = true;
        window.isRecordingCall = true;
        recordingStartTime = Date.now();
        updateRecordButton(true);
        updateRecordingTimer();
        showRecordingTimer();
        console.log('Recording started with', count, 'streams');
    }).catch(err => {
        console.error('Error preparing recording:', err);
        alert('Error starting recording: ' + err.message);
        // Clean up on error
        createdVideoElements.forEach(video => video.remove());
        if (recordingCanvas) recordingCanvas.remove();
        recordingCanvas = null;
        recordingContext = null;
        updateRecordButton(false);
    });
}

function stopCallRecording() {
    if (!mediaRecorder || !isRecording) return;
    
    mediaRecorder.stop();
    isRecording = false;
    window.isRecordingCall = false;
    recordingStartTime = null;
    updateRecordButton(false);
    hideRecordingTimer();
    
    // Stop recording timer
    if (recordingTimerInterval) {
        clearInterval(recordingTimerInterval);
        recordingTimerInterval = null;
    }
    
    // Stop drawing loop
    if (recordingAnimationFrame) {
        cancelAnimationFrame(recordingAnimationFrame);
        recordingAnimationFrame = null;
    }
    
    recordingCanvas = null;
    recordingContext = null;
}

function updateRecordingTimer() {
    if (!isRecording || !recordingStartTime) {
        hideRecordingTimer();
        return;
    }
    
    const elapsed = Date.now() - recordingStartTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    const timerElement = document.getElementById('callRecordingTime');
    if (timerElement) {
        timerElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
    
    // Start interval if not already running
    if (!recordingTimerInterval) {
        recordingTimerInterval = setInterval(updateRecordingTimer, 1000);
    }
}

function showRecordingTimer() {
    const timerContainer = document.getElementById('callRecordingTimer');
    if (timerContainer) {
        timerContainer.classList.remove('hidden');
    }
}

function hideRecordingTimer() {
    const timerContainer = document.getElementById('callRecordingTimer');
    if (timerContainer) {
        timerContainer.classList.add('hidden');
    }
    const timerElement = document.getElementById('callRecordingTime');
    if (timerElement) {
        timerElement.textContent = '00:00';
    }
}

async function downloadRecordingAsZip(videoBlob) {
    try {
        if (typeof JSZip === 'undefined') {
            // Fallback to direct download if JSZip is not available
            console.warn('JSZip not available, downloading video directly');
            const url = URL.createObjectURL(videoBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `call-recording-${Date.now()}.webm`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            return;
        }
        
        const zip = new JSZip();
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0] + '_' + Date.now();
        const folderName = `call-recording-${timestamp}`;
        
        // Add video file to zip (using .webm extension - VLC supports WebM)
        const videoFileName = `${folderName}.webm`;
        zip.file(videoFileName, videoBlob);
        
        // Create info file with recording details
        const recordingDuration = recordingStartTime ? Math.floor((Date.now() - recordingStartTime) / 1000) : 0;
        const minutes = Math.floor(recordingDuration / 60);
        const seconds = recordingDuration % 60;
        const participants = currentCall ? currentCall.participants.map(p => p.name).join(', ') : 'Unknown';
        const callType = currentCallType || 'video';
        const hasScreenShare = isScreenSharing ? 'Yes' : 'No';
        
        const infoContent = `Call Recording Information
============================
Date: ${new Date().toLocaleString()}
Duration: ${minutes}:${String(seconds).padStart(2, '0')}
Call Type: ${callType}
Screen Share: ${hasScreenShare}
Participants: ${participants}
Total Participants: ${currentCall ? currentCall.participants.length : 0}

Video File: ${videoFileName}
Format: WebM (VP9/VP8 + Opus)
Compatible with: VLC Media Player, Chrome, Firefox, Edge, and most modern video players
`;
        
        zip.file('RECORDING_INFO.txt', infoContent);
        
        // Generate zip file
        const zipBlob = await zip.generateAsync({ type: 'blob' });
        const zipUrl = URL.createObjectURL(zipBlob);
        
        // Download zip file
        const a = document.createElement('a');
        a.href = zipUrl;
        a.download = `${folderName}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Clean up
        URL.revokeObjectURL(zipUrl);
        
        console.log('Recording downloaded as ZIP file');
    } catch (error) {
        console.error('Error creating ZIP file:', error);
        // Fallback to direct download
        const url = URL.createObjectURL(videoBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `call-recording-${Date.now()}.webm`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

function downloadRecording(url) {
    const a = document.createElement('a');
    a.href = url;
    a.download = `call-recording-${Date.now()}.webm`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function cleanupCall() {
    // Stop recording if active
    if (isRecording) {
        stopCallRecording();
    }
    
    // Clear recording timer
    if (recordingTimerInterval) {
        clearInterval(recordingTimerInterval);
        recordingTimerInterval = null;
    }
    recordingStartTime = null;
    hideRecordingTimer();
    
    // Stop screen share if active
    if (isScreenSharing) {
        stopScreenShare();
    }
    
    // Clean up audio elements
    Object.values(remoteAudioElements).forEach(audio => {
        audio.srcObject = null;
        audio.remove();
    });
    remoteAudioElements = {};
    
    // Reset minimized state
    isCallModalMinimized = false;
    
    // Stop local stream
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    
    if (processedLocalStream && processedLocalStream !== localStream) {
        processedLocalStream.getTracks().forEach(track => track.stop());
        processedLocalStream = null;
    }
    
    // Cleanup background canvas
    if (backgroundCanvas) {
        backgroundCanvas = null;
        backgroundContext = null;
        backgroundVideo = null;
    }
    
    // Close all peer connections
    Object.values(peerConnections).forEach(pc => pc.close());
    peerConnections = {};
    
    // Clear remote streams
    remoteStreams = {};
    
    // Clear call state
    currentCall = null;
    currentCallType = null;
    backgroundEffect = 'none';
    backgroundImage = null;
    
    // Hide modal
    hideCallModal();
    stopRingtone();
}

function updateCallUI() {
    if (!currentCall) return;
    
    // Update participants list
    const participantsDiv = document.getElementById('callParticipants');
    if (participantsDiv) {
        participantsDiv.innerHTML = '';
        currentCall.participants.forEach(participant => {
            const div = document.createElement('div');
            div.className = 'text-white text-sm';
            div.textContent = participant.name;
            participantsDiv.appendChild(div);
        });
    }
    
    // Update video/audio grid
    if (currentCall.type === 'video') {
        updateVideoGrid();
    } else {
        updateAudioCallUI();
    }
}

function updateVideoGrid() {
    const videoGrid = document.getElementById('videoGrid');
    if (!videoGrid) return;
    
    videoGrid.innerHTML = '';
    
    // Add local video
    const localVideoDiv = document.createElement('div');
    localVideoDiv.className = 'relative bg-black rounded-lg overflow-hidden';
    localVideoDiv.style.minHeight = '300px';
    localVideoDiv.innerHTML = `
        <video id="localVideo" autoplay muted playsinline class="w-full h-full object-cover"></video>
        <div class="absolute bottom-2 left-2 bg-black/50 text-white px-2 py-1 rounded text-xs">You</div>
    `;
    videoGrid.appendChild(localVideoDiv);
    updateLocalVideo();
    
    // Add remote videos
    Object.keys(remoteStreams).forEach(userId => {
        const participant = currentCall.participants.find(p => p.id == userId);
        if (participant) {
            const remoteVideoDiv = document.createElement('div');
            remoteVideoDiv.className = 'relative bg-black rounded-lg overflow-hidden';
            remoteVideoDiv.id = `remoteVideo-${userId}`;
            remoteVideoDiv.style.minHeight = '300px';
            remoteVideoDiv.innerHTML = `
                <video id="remoteVideoStream-${userId}" autoplay playsinline class="w-full h-full object-cover"></video>
                <div class="absolute bottom-2 left-2 bg-black/50 text-white px-2 py-1 rounded text-xs">${participant.name}</div>
            `;
            videoGrid.appendChild(remoteVideoDiv);
            updateRemoteVideo(userId, remoteStreams[userId]);
        }
    });
    
    // Update grid layout based on number of participants
    const totalVideos = 1 + Object.keys(remoteStreams).length;
    if (totalVideos === 1) {
        videoGrid.className = 'grid grid-cols-1 gap-4';
    } else if (totalVideos === 2) {
        videoGrid.className = 'grid grid-cols-2 gap-4';
    } else {
        videoGrid.className = 'grid grid-cols-2 gap-4';
    }
}

function updateAudioCallUI() {
    const videoGrid = document.getElementById('videoGrid');
    if (!videoGrid) return;
    
    videoGrid.innerHTML = `
        <div class="col-span-2 flex flex-col items-center justify-center space-y-4 py-8">
            <div class="w-32 h-32 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-4xl font-bold">
                ${currentCall.participants.find(p => !p.isLocal)?.name?.[0] || '?'}
            </div>
            <div class="text-white text-xl font-semibold">
                ${currentCall.participants.find(p => !p.isLocal)?.name || 'Participant'}
            </div>
            <div class="text-white/70 text-sm">Audio Call</div>
        </div>
    `;
    videoGrid.className = 'grid grid-cols-1 gap-4';
    
    // Create/update audio elements for remote streams
    Object.keys(remoteStreams).forEach(userId => {
        if (!remoteAudioElements[userId]) {
            const audio = document.createElement('audio');
            audio.autoplay = true;
            audio.playsInline = true;
            audio.id = `remoteAudio-${userId}`;
            audio.style.display = 'none';
            document.body.appendChild(audio);
            remoteAudioElements[userId] = audio;
        }
        
        const audio = remoteAudioElements[userId];
        audio.srcObject = remoteStreams[userId];
        audio.play().catch(err => {
            console.error('Error playing remote audio:', err);
        });
    });
    
    // Remove audio elements for users who left
    Object.keys(remoteAudioElements).forEach(userId => {
        if (!remoteStreams[userId]) {
            const audio = remoteAudioElements[userId];
            audio.srcObject = null;
            audio.remove();
            delete remoteAudioElements[userId];
        }
    });
}

function updateLocalVideo() {
    const localVideo = document.getElementById('localVideo');
    if (localVideo) {
        const streamToShow = isScreenSharing ? screenShareStream : (processedLocalStream || localStream);
        if (streamToShow) {
            localVideo.srcObject = streamToShow;
            
            // Apply blur effect if enabled (CSS-based, limited)
            if (backgroundEffect === 'blur' && !isScreenSharing) {
                localVideo.style.filter = 'blur(10px)';
            } else {
                localVideo.style.filter = '';
            }
        }
    }
}

function updateRemoteVideo(userId, stream) {
    if (!stream) {
        console.warn('No stream provided for', userId);
        return;
    }
    
    // Handle video streams
    const remoteVideo = document.getElementById(`remoteVideoStream-${userId}`);
    if (remoteVideo) {
        remoteVideo.srcObject = stream;
        remoteVideo.onloadedmetadata = () => {
            remoteVideo.play().catch(err => {
                console.error('Error playing remote video:', err);
            });
        };
    }
    
    // Handle audio streams for audio-only calls
    if (currentCallType === 'audio') {
        if (!remoteAudioElements[userId]) {
            const audio = document.createElement('audio');
            audio.autoplay = true;
            audio.playsInline = true;
            audio.id = `remoteAudio-${userId}`;
            audio.style.display = 'none';
            document.body.appendChild(audio);
            remoteAudioElements[userId] = audio;
        }
        
        const audio = remoteAudioElements[userId];
        audio.srcObject = stream;
        audio.play().catch(err => {
            console.error('Error playing remote audio:', err);
        });
    }
}

function showCallModal(state, userName, type) {
    const modal = document.getElementById('callModal');
    if (!modal) return;
    
    modal.classList.remove('hidden');
    
    const title = document.getElementById('callTitle');
    const status = document.getElementById('callStatus');
    
    if (title) {
        title.textContent = userName || 'Call';
    }
    
    if (state === 'incoming') {
        if (status) status.textContent = `Incoming ${type} call`;
    } else if (state === 'outgoing') {
        if (status) status.textContent = `Calling...`;
    } else if (state === 'active') {
        if (status) status.textContent = `${type} call in progress`;
    }
    
    updateCallButtons(state);
    updateCallUI();
}

function updateCallModal(state, userName, type) {
    showCallModal(state, userName, type);
}

function updateCallButtons(state) {
    const acceptBtn = document.getElementById('acceptCallBtn');
    const rejectBtn = document.getElementById('rejectCallBtn');
    const endCallBtn = document.getElementById('endCallBtn');
    const blurBtn = document.getElementById('blurBackgroundBtn');
    const videoBtn = document.getElementById('videoBtn');
    const screenShareBtn = document.getElementById('screenShareBtn');
    
    if (state === 'incoming') {
        if (acceptBtn) acceptBtn.classList.remove('hidden');
        if (rejectBtn) rejectBtn.classList.remove('hidden');
        if (endCallBtn) endCallBtn.classList.add('hidden');
        if (blurBtn) blurBtn.style.display = 'none';
        if (videoBtn) videoBtn.style.display = 'none';
        if (screenShareBtn) screenShareBtn.style.display = 'none';
    } else if (state === 'outgoing') {
        if (acceptBtn) acceptBtn.classList.add('hidden');
        if (rejectBtn) rejectBtn.classList.remove('hidden');
        if (endCallBtn) endCallBtn.classList.add('hidden');
        if (blurBtn) blurBtn.style.display = 'none';
        if (videoBtn) videoBtn.style.display = 'none';
        if (addParticipantBtn) addParticipantBtn.style.display = 'none';
        if (screenShareBtn) screenShareBtn.style.display = 'none';
    } else if (state === 'active') {
        if (acceptBtn) acceptBtn.classList.add('hidden');
        if (rejectBtn) rejectBtn.classList.add('hidden');
        if (endCallBtn) endCallBtn.classList.remove('hidden');
        // Show blur button only for video calls
        if (blurBtn) blurBtn.style.display = currentCallType === 'video' ? 'flex' : 'none';
        if (videoBtn) videoBtn.style.display = currentCallType === 'video' ? 'flex' : 'none';
        if (screenShareBtn) screenShareBtn.style.display = currentCallType === 'video' ? 'flex' : 'none';
        if (addParticipantBtn) addParticipantBtn.style.display = 'flex';
    }
}

function hideCallModal() {
    const modal = document.getElementById('callModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function showAddParticipantModal() {
    if (!currentCall || !currentCall.callId) return;
    
    const modal = document.getElementById('addParticipantModal');
    if (!modal) return;
    
    // Add click handlers to participant cards
    const cards = modal.querySelectorAll('.participant-card');
    cards.forEach(card => {
        card.onclick = function() {
            const userId = parseInt(this.getAttribute('data-user-id'));
            const userName = this.getAttribute('data-user-name');
            
            // Check if user is already in call
            if (currentCall.participants.find(p => p.id === userId)) {
                alert(userName + ' is already in the call');
                return;
            }
            
            // Add participant
            addParticipantToCall(userId);
            hideAddParticipantModal();
        };
    });
    
    modal.classList.remove('hidden');
}

function hideAddParticipantModal() {
    const modal = document.getElementById('addParticipantModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function toggleCallModalMinimize() {
    const modal = document.getElementById('callModal');
    const content = document.getElementById('callModalContent');
    const icon = document.getElementById('minimizeIcon');
    
    if (!modal || !content) return;
    
    isCallModalMinimized = !isCallModalMinimized;
    
    if (isCallModalMinimized) {
        // Minimize - make it a small floating window
        modal.classList.remove('items-center', 'justify-center');
        modal.style.alignItems = 'flex-end';
        modal.style.justifyContent = 'flex-end';
        modal.style.padding = '20px';
        content.style.maxWidth = '400px';
        content.style.width = 'auto';
        content.style.height = 'auto';
        content.style.maxHeight = '300px';
        content.style.overflow = 'auto';
        if (icon) icon.className = 'fas fa-window-restore text-lg';
    } else {
        // Maximize - restore to full size
        modal.classList.add('items-center', 'justify-center');
        modal.style.alignItems = '';
        modal.style.justifyContent = '';
        modal.style.padding = '';
        content.style.maxWidth = 'max-w-7xl';
        content.style.width = 'w-full';
        content.style.height = '';
        content.style.maxHeight = '';
        content.style.overflow = '';
        if (icon) icon.className = 'fas fa-window-minimize text-lg';
    }
    
    // Update UI to reflect changes
    updateCallUI();
}

function playRingtone() {
    // Optional: Add ringtone
}

function stopRingtone() {
    // Stop ringtone if playing
}

function toggleMute() {
    if (localStream) {
        const audioTracks = localStream.getAudioTracks();
        audioTracks.forEach(track => {
            track.enabled = !track.enabled;
        });
        
        const muteBtn = document.getElementById('muteBtn');
        if (muteBtn) {
            muteBtn.classList.toggle('bg-red-500', !audioTracks[0]?.enabled);
        }
    }
}

function toggleVideo() {
    if (localStream) {
        const videoTracks = localStream.getVideoTracks();
        videoTracks.forEach(track => {
            track.enabled = !track.enabled;
        });
        
        const videoBtn = document.getElementById('videoBtn');
        if (videoBtn) {
            videoBtn.classList.toggle('bg-red-500', !videoTracks[0]?.enabled);
        }
    }
}

function toggleBackgroundBlur() {
    if (currentCallType !== 'video') return;
    
    if (backgroundEffect === 'blur') {
        backgroundEffect = 'none';
    } else {
        backgroundEffect = 'blur';
    }
    
    processLocalStream();
    
    const blurBtn = document.getElementById('blurBackgroundBtn');
    if (blurBtn) {
        blurBtn.classList.toggle('bg-green-500', backgroundEffect === 'blur');
        blurBtn.classList.toggle('bg-white/20', backgroundEffect !== 'blur');
    }
}

function setBackgroundImage(file) {
    if (currentCallType !== 'video') return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        backgroundImage = e.target.result;
        backgroundEffect = 'image';
        processLocalStream();
    };
    reader.readAsDataURL(file);
}

function updateScreenShareButton(isSharing) {
    const screenShareBtn = document.getElementById('screenShareBtn');
    if (screenShareBtn) {
        screenShareBtn.classList.toggle('bg-green-500', isSharing);
        screenShareBtn.classList.toggle('bg-purple-500', !isSharing);
    }
}

function updateRecordButton(isRecordingState) {
    const recordBtn = document.getElementById('callRecordBtn');
    if (recordBtn) {
        if (isRecordingState) {
            recordBtn.classList.remove('bg-gray-500', 'hover:bg-gray-600');
            recordBtn.classList.add('bg-red-500', 'hover:bg-red-600');
            recordBtn.title = 'Stop Recording';
        } else {
            recordBtn.classList.remove('bg-red-500', 'hover:bg-red-600');
            recordBtn.classList.add('bg-gray-500', 'hover:bg-gray-600');
            recordBtn.title = 'Record Call';
        }
    }
}
