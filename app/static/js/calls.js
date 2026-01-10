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
let backgroundVideo = null;
let recordingCanvas = null;
let recordingContext = null;
let recordingAnimationFrame = null;
let recordingStartTime = null;
let recordingTimerInterval = null;
let isCallModalMinimized = false;
let remoteAudioElements = {}; // {userId: HTMLAudioElement}
let callState = null; // 'calling', 'incoming', 'active'

const STUN_SERVERS = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
    ]
};

// Initialize calls system
function initCalls() {
    console.log('Initializing calls system...');
    
    // Listen for incoming calls
    socket.on('incoming_call', handleIncomingCall);
    
    // Listen for call initiated (response from server with call_id)
    socket.on('call_initiated', (data) => {
        console.log('Call initiated, call_id:', data.call_id);
        if (currentCall) {
            currentCall.callId = data.call_id;
        }
    });
    
    // Listen for call errors
    socket.on('call_error', (data) => {
        console.error('Call error:', data.message);
        alert(data.message || 'Call error occurred');
        endCall();
    });
    
    // Listen for call accepted
    socket.on('call_accepted', (data) => {
        console.log('Call accepted by', data.user_id);
        if (currentCall && currentCall.callId === data.call_id) {
            currentCall.participants.push({ id: data.user_id, name: data.user_name || 'User', isLocal: false });
            
            // Create peer connection for the new participant
            createPeerConnection(data.user_id, true);
            
            // Get local media and create offer
            getLocalMedia(currentCallType, false).then(() => {
                createOffer(data.user_id);
            }).catch(err => {
                console.error('Error getting local media:', err);
            });
        }
    });
    
    // Listen for call rejected
    socket.on('call_rejected', (data) => {
        console.log('Call rejected by', data.user_id);
        if (currentCall && currentCall.callId === data.call_id) {
            alert(`${data.user_name || 'User'} rejected the call`);
            endCall();
        }
    });
    
    // Listen for call ended
    socket.on('call_ended', (data) => {
        console.log('Call ended', data);
        endCall();
    });
    
    // Listen for WebRTC signaling
    socket.on('call_offer', handleCallOffer);
    socket.on('call_answer', handleCallAnswer);
    socket.on('call_ice_candidate', handleIceCandidate);
    
    // Listen for participant joining
    socket.on('participant_joined', (data) => {
        console.log('Participant joined:', data);
        if (currentCall && currentCall.callId === data.call_id) {
            currentCall.participants.push({ id: data.user_id, name: data.user_name || 'User', isLocal: false });
            updateCallUI();
        }
    });
    
    // Listen for participant leaving
    socket.on('participant_left', (data) => {
        console.log('Participant left:', data);
        if (currentCall && currentCall.callId === data.call_id) {
            currentCall.participants = currentCall.participants.filter(p => p.id !== data.user_id);
            if (peerConnections[data.user_id]) {
                peerConnections[data.user_id].close();
                delete peerConnections[data.user_id];
            }
            if (remoteStreams[data.user_id]) {
                delete remoteStreams[data.user_id];
            }
            updateCallUI();
        }
    });
}

async function initiateCall(userId, userName, type) {
    if (currentCall) {
        alert('You are already in a call');
        return;
    }
    
    callState = 'calling';
    currentCallType = type;
    currentCall = {
        callId: `call_${Date.now()}_${CURRENT_USER_ID}`,
        participants: [{ id: CURRENT_USER_ID, name: 'You', isLocal: true }],
        type: type
    };
    
    // Get local media first
    try {
        await getLocalMedia(type, false);
        showCallModal('calling', userName, type);
        updateCallButtons();
        
        // Emit call initiation
        socket.emit('initiate_call', {
            callee_id: userId,
            type: type
        });
        
        // Wait for call accepted before creating peer connection
        // Peer connection will be created in 'call_accepted' handler
    } catch (err) {
        console.error('Error initiating call:', err);
        alert('Error starting call: ' + err.message);
        endCall();
    }
}

function handleIncomingCall(data) {
    console.log('Incoming call:', data);
    callState = 'incoming';
    currentCallType = data.type;
    currentCall = {
        callId: data.call_id,
        participants: [{ id: data.caller_id, name: data.caller_name || 'User', isLocal: false }],
        type: data.type
    };
    
    showCallModal('incoming', data.caller_name, data.type);
    updateCallButtons();
    playRingtone();
}

async function acceptCall() {
    if (!currentCall) return;
    
    callState = 'active';
    stopRingtone();
    
    try {
        await getLocalMedia(currentCallType, false);
        
        showCallModal('active', '', currentCallType);
        updateCallButtons();
        
        // Create peer connections for all existing participants
        currentCall.participants.forEach(participant => {
            if (!participant.isLocal) {
                createPeerConnection(participant.id, false);
            }
        });
        
        // Accept call on server
        socket.emit('accept_call', {
            call_id: currentCall.callId
        });
        
        // Create offers for all participants
        currentCall.participants.forEach(participant => {
            if (!participant.isLocal) {
                createOffer(participant.id);
            }
        });
    } catch (err) {
        console.error('Error accepting call:', err);
        alert('Error accepting call: ' + err.message);
        endCall();
    }
}

function rejectCall() {
    if (!currentCall) return;
    
    stopRingtone();
    socket.emit('reject_call', {
        call_id: currentCall.callId
    });
    
    endCall();
}

function endCall() {
    callState = null;
    if (isRecording) {
        stopCallRecording();
    }
    
    if (currentCall) {
        socket.emit('end_call', {
            call_id: currentCall.callId
        });
    }
    
    // Stop all media tracks
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    
    if (screenShareStream) {
        screenShareStream.getTracks().forEach(track => track.stop());
        screenShareStream = null;
    }
    
    if (processedLocalStream) {
        processedLocalStream.getTracks().forEach(track => track.stop());
        processedLocalStream = null;
    }
    
    // Close all peer connections
    Object.values(peerConnections).forEach(pc => pc.close());
    peerConnections = {};
    remoteStreams = {};
    
    currentCall = null;
    currentCallType = null;
    isScreenSharing = false;
    
    hideCallModal();
    stopRingtone();
    
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
}

async function getLocalMedia(type, screenShare) {
    try {
        const constraints = {
            audio: true,
            video: screenShare ? {
                mediaSource: 'screen'
            } : type === 'video' ? {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            } : false
        };
        
        let stream;
        if (screenShare) {
            stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
        } else {
            stream = await navigator.mediaDevices.getUserMedia(constraints);
        }
        
        if (!screenShare) {
            localStream = stream;
            processedLocalStream = stream; // For now, no processing
        }
        
        return stream;
    } catch (err) {
        console.error('Error getting local media:', err);
        throw err;
    }
}

function processLocalStream(stream) {
    // Apply background effects if needed
    // For now, just return the stream
    return stream;
}

function updatePeerConnectionsTracks() {
    const streamToUse = processedLocalStream || localStream;
    Object.keys(peerConnections).forEach(userId => {
        const pc = peerConnections[userId];
        streamToUse.getTracks().forEach(track => {
            const sender = pc.getSenders().find(s => s.track && s.track.kind === track.kind);
            if (sender) {
                sender.replaceTrack(track);
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
        console.log('Peer connection state changed:', userId, pc.connectionState);
        if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
            console.warn('Peer connection failed or disconnected:', userId);
        }
    };
    
    return pc;
}

async function createOffer(userId) {
    const pc = peerConnections[userId];
    if (!pc) {
        console.error('No peer connection for', userId);
        return;
    }
    
    try {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        
        socket.emit('call_offer', {
            call_id: currentCall.callId,
            to_user_id: userId,
            offer: offer
        });
    } catch (err) {
        console.error('Error creating offer:', err);
    }
}

async function handleCallOffer(data) {
    const userId = data.from_user_id;
    
    if (!peerConnections[userId]) {
        createPeerConnection(userId, false);
    }
    
    const pc = peerConnections[userId];
    try {
        await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        
        socket.emit('call_answer', {
            call_id: currentCall.callId,
            to_user_id: userId,
            answer: answer
        });
    } catch (err) {
        console.error('Error handling offer:', err);
    }
}

async function handleCallAnswer(data) {
    const userId = data.from_user_id;
    const pc = peerConnections[userId];
    
    if (!pc) {
        console.error('No peer connection for', userId);
        return;
    }
    
    try {
        await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
    } catch (err) {
        console.error('Error handling answer:', err);
    }
}

function handleIceCandidate(data) {
    const userId = data.from_user_id;
    const pc = peerConnections[userId];
    
    if (!pc) {
        console.error('No peer connection for', userId);
        return;
    }
    
    try {
        pc.addIceCandidate(new RTCIceCandidate(data.candidate));
    } catch (err) {
        console.error('Error adding ICE candidate:', err);
    }
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
        toggleCallModalMinimize();
    }
}

function startCallRecording() {
    if (!localStream || isRecording) return;
    
    console.log('Starting recording...');
    
    // Use existing video elements from the call UI - they're already visible and playing
    const videoElements = {};
    
    // Get local video element from call UI
    const localVideoEl = document.getElementById('localVideo');
    if (localVideoEl && localVideoEl.srcObject) {
        videoElements.local = localVideoEl;
        console.log('Using existing local video element');
    }
    
    // Get remote video elements from call UI
    Object.keys(remoteStreams).forEach(userId => {
        const remoteVideoEl = document.getElementById(`remoteVideoStream-${userId}`);
        if (remoteVideoEl && remoteVideoEl.srcObject) {
            videoElements[userId] = remoteVideoEl;
            console.log('Using existing remote video element for', userId);
        }
    });
    
    const videoCount = Object.keys(videoElements).length;
    if (videoCount === 0) {
        console.error('No video elements found in call UI');
        alert('Cannot start recording: No video streams available');
        return;
    }
    
    console.log('Using', videoCount, 'existing video elements for recording');
    
    // Create a small visible canvas for compositing (must be in viewport for captureStream to work)
    recordingCanvas = document.createElement('canvas');
    recordingCanvas.width = 1280;
    recordingCanvas.height = 720;
    recordingContext = recordingCanvas.getContext('2d');
    
    // Position canvas in viewport but make it very small (1x1px) and transparent
    recordingCanvas.style.cssText = 'position: fixed; top: 0; right: 0; width: 1px; height: 1px; opacity: 0.01; z-index: 999999; pointer-events: none;';
    document.body.appendChild(recordingCanvas);
    
    // Wait a moment for canvas to be in DOM
    setTimeout(() => {
        // Start drawing loop to composite videos onto canvas
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
        
        // Get local stream for audio
        const localStreamToUse = isScreenSharing ? screenShareStream : (processedLocalStream || localStream);
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
            
            // Clean up canvas
            if (recordingCanvas && recordingCanvas.parentNode) {
                recordingCanvas.parentNode.removeChild(recordingCanvas);
            }
            recordingCanvas = null;
            recordingContext = null;
            
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
        if (!recordingTimerInterval) {
            recordingTimerInterval = setInterval(updateRecordingTimer, 1000);
        }
        showRecordingTimer();
        console.log('Recording started with', videoCount, 'streams');
    }, 100);
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
        if (recordingTimerInterval) {
            clearInterval(recordingTimerInterval);
            recordingTimerInterval = null;
        }
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
}

async function downloadRecordingAsZip(videoBlob) {
    try {
        // Check if JSZip is available
        if (typeof JSZip === 'undefined') {
            // Fallback: Direct download
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
        const folderName = `call-recording-${new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)}`;
        
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
        
        // Generate and download ZIP
        const zipBlob = await zip.generateAsync({ type: 'blob' });
        const url = URL.createObjectURL(zipBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${folderName}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('Recording downloaded as ZIP');
    } catch (err) {
        console.error('Error downloading recording:', err);
        // Fallback: Direct download
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

function toggleMute() {
    if (!localStream) return;
    
    const audioTracks = localStream.getAudioTracks();
    audioTracks.forEach(track => {
        track.enabled = !track.enabled;
    });
    
    const muteBtn = document.getElementById('muteBtn');
    if (muteBtn) {
        if (audioTracks[0] && audioTracks[0].enabled) {
            muteBtn.innerHTML = '<i class="fas fa-microphone text-lg"></i>';
            muteBtn.title = 'Mute';
        } else {
            muteBtn.innerHTML = '<i class="fas fa-microphone-slash text-lg"></i>';
            muteBtn.title = 'Unmute';
        }
    }
}

function toggleVideo() {
    if (!localStream) return;
    
    const videoTracks = localStream.getVideoTracks();
    videoTracks.forEach(track => {
        track.enabled = !track.enabled;
    });
    
    const videoBtn = document.getElementById('videoBtn');
    if (videoBtn) {
        if (videoTracks[0] && videoTracks[0].enabled) {
            videoBtn.innerHTML = '<i class="fas fa-video text-lg"></i>';
            videoBtn.title = 'Turn off camera';
        } else {
            videoBtn.innerHTML = '<i class="fas fa-video-slash text-lg"></i>';
            videoBtn.title = 'Turn on camera';
        }
    }
}

function toggleScreenShare() {
    if (isScreenSharing) {
        stopScreenShare();
    } else {
        startScreenShare();
    }
}

function updateScreenShareButton(isSharing) {
    const screenShareBtn = document.getElementById('screenShareBtn');
    if (screenShareBtn) {
        if (isSharing) {
            screenShareBtn.classList.add('bg-purple-500');
            screenShareBtn.classList.remove('bg-gray-600');
            screenShareBtn.title = 'Stop sharing screen';
        } else {
            screenShareBtn.classList.remove('bg-purple-500');
            screenShareBtn.classList.add('bg-gray-600');
            screenShareBtn.title = 'Share screen';
        }
    }
}

function updateRecordButton(isRecordingState) {
    const recordBtn = document.getElementById('callRecordBtn');
    if (recordBtn) {
        if (isRecordingState) {
            recordBtn.classList.remove('bg-gray-500');
            recordBtn.classList.add('bg-red-500');
            recordBtn.title = 'Stop recording';
        } else {
            recordBtn.classList.remove('bg-red-500');
            recordBtn.classList.add('bg-gray-500');
            recordBtn.title = 'Start recording';
        }
    }
}

function toggleCallModalMinimize() {
    const modal = document.getElementById('callModal');
    const modalContent = document.getElementById('callModalContent');
    
    if (!modal || !modalContent) return;
    
    isCallModalMinimized = !isCallModalMinimized;
    
    if (isCallModalMinimized) {
        modalContent.classList.add('w-96', 'h-auto', 'max-w-none');
        modalContent.classList.remove('max-w-7xl');
        modal.style.alignItems = 'flex-end';
        modal.style.justifyContent = 'flex-end';
        modal.style.padding = '1rem';
    } else {
        modalContent.classList.remove('w-96', 'h-auto', 'max-w-none');
        modalContent.classList.add('max-w-7xl');
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.padding = '0';
    }
}

function showCallModal(state, userName, type) {
    const modal = document.getElementById('callModal');
    const title = document.getElementById('callTitle');
    const status = document.getElementById('callStatus');
    
    if (!modal) return;
    
    modal.classList.remove('hidden');
    
    if (state === 'calling') {
        callState = 'calling';
        title.textContent = `Calling ${userName}...`;
        status.textContent = 'Waiting for answer...';
    } else if (state === 'incoming') {
        callState = 'incoming';
        title.textContent = `Incoming ${type === 'video' ? 'Video' : 'Audio'} Call`;
        status.textContent = `${userName} is calling you...`;
    } else if (state === 'active') {
        callState = 'active';
        title.textContent = `${type === 'video' ? 'Video' : 'Audio'} Call`;
        status.textContent = 'Connected';
        updateCallUI();
    }
    
    updateCallButtons();
}

function hideCallModal() {
    const modal = document.getElementById('callModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function updateCallButtons() {
    const acceptBtn = document.getElementById('acceptCallBtn');
    const rejectBtn = document.getElementById('rejectCallBtn');
    const endBtn = document.getElementById('endCallBtn');
    const muteBtn = document.getElementById('muteBtn');
    const videoBtn = document.getElementById('videoBtn');
    const screenShareBtn = document.getElementById('screenShareBtn');
    const recordBtn = document.getElementById('callRecordBtn');
    const minimizeBtn = document.getElementById('minimizeCallBtn');
    const addParticipantBtn = document.getElementById('addParticipantBtn');
    
    if (!currentCall) {
        if (acceptBtn) acceptBtn.classList.add('hidden');
        if (rejectBtn) rejectBtn.classList.add('hidden');
        if (endBtn) endBtn.classList.add('hidden');
        if (muteBtn) muteBtn.classList.add('hidden');
        if (videoBtn) videoBtn.classList.add('hidden');
        if (screenShareBtn) screenShareBtn.classList.add('hidden');
        if (recordBtn) recordBtn.classList.add('hidden');
        if (minimizeBtn) minimizeBtn.classList.add('hidden');
        if (addParticipantBtn) addParticipantBtn.classList.add('hidden');
        return;
    }
    
    // Use callState to determine which buttons to show
    const isIncoming = callState === 'incoming';
    const isActive = callState === 'active';
    
    if (acceptBtn) acceptBtn.classList.toggle('hidden', !isIncoming);
    if (rejectBtn) rejectBtn.classList.toggle('hidden', !isIncoming);
    if (endBtn) endBtn.classList.toggle('hidden', !isActive);
    if (muteBtn) muteBtn.classList.toggle('hidden', !isActive || currentCallType === 'audio');
    if (videoBtn) videoBtn.classList.toggle('hidden', !isActive || currentCallType === 'audio');
    if (screenShareBtn) screenShareBtn.classList.toggle('hidden', !isActive || currentCallType === 'audio');
    if (recordBtn) recordBtn.classList.toggle('hidden', !isActive);
    if (minimizeBtn) minimizeBtn.classList.toggle('hidden', !isActive);
    if (addParticipantBtn) addParticipantBtn.classList.toggle('hidden', !isActive);
}

function updateCallUI() {
    const videoGrid = document.getElementById('videoGrid');
    if (!videoGrid) return;
    
    if (currentCallType === 'video') {
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

function playRingtone() {
    // Simple ringtone implementation - could be enhanced
    console.log('Playing ringtone');
}

function stopRingtone() {
    console.log('Stopping ringtone');
}

function showAddParticipantModal() {
    const modal = document.getElementById('addParticipantModal');
    if (!modal) return;
    
    // Get workspace members (should be available from template)
    const membersList = document.getElementById('addParticipantMembersList');
    if (!membersList) return;
    
    // Filter out current participants
    const currentParticipantIds = currentCall ? currentCall.participants.map(p => p.id) : [];
    
    // Members list should be populated from template
    modal.classList.remove('hidden');
}

function hideAddParticipantModal() {
    const modal = document.getElementById('addParticipantModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function addParticipantToCall(userId) {
    if (!currentCall) return;
    
    socket.emit('add_participant', {
        call_id: currentCall.callId,
        user_id: userId
    });
    
    hideAddParticipantModal();
}

function toggleBackgroundBlur() {
    if (isScreenSharing) return;
    
    backgroundEffect = backgroundEffect === 'blur' ? 'none' : 'blur';
    updateLocalVideo();
}
