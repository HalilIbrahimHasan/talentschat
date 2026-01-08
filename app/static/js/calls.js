// WebRTC Call Management - Group Video/Audio Calls with Screen Sharing and Recording
let currentCall = null;
let localStream = null;
let screenShareStream = null;
let peerConnections = {}; // {userId: RTCPeerConnection}
let remoteStreams = {}; // {userId: MediaStream}
let currentCallType = null; // 'video' or 'audio'
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;
let isScreenSharing = false;

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
        // Create peer connections for all existing participants
        currentCall.participants.forEach(participant => {
            if (!participant.isLocal && participant.id !== CURRENT_USER_ID) {
                createPeerConnection(participant.id, true);
            }
        });
        
        // Accept call
        socket.emit('accept_call', {
            call_id: currentCall.callId
        });
        
        // Update UI
        updateCallModal('active', null, type);
        updateCallUI();
        stopRingtone();
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
    
    // Create peer connection with the new participant
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
        
        // Create peer connection
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
    
    if (!peerConnections[from_user_id]) {
        createPeerConnection(from_user_id, false);
    }
    
    peerConnections[from_user_id].setRemoteDescription(new RTCSessionDescription(offer))
        .then(() => {
            return peerConnections[from_user_id].createAnswer();
        })
        .then(answer => {
            return peerConnections[from_user_id].setLocalDescription(answer);
        })
        .then(() => {
            socket.emit('call_answer', {
                call_id: currentCall.callId,
                to_user_id: from_user_id,
                answer: peerConnections[from_user_id].localDescription
            });
        })
        .catch(err => {
            console.error('Error handling offer:', err);
        });
}

function handleCallAnswer(data) {
    const { answer, from_user_id } = data;
    
    if (!peerConnections[from_user_id]) return;
    
    peerConnections[from_user_id].setRemoteDescription(new RTCSessionDescription(answer))
        .catch(err => {
            console.error('Error setting remote description:', err);
        });
}

function handleIceCandidate(data) {
    const { candidate, from_user_id } = data;
    
    if (!peerConnections[from_user_id]) return;
    
    if (candidate) {
        peerConnections[from_user_id].addIceCandidate(new RTCIceCandidate(candidate))
            .catch(err => {
                console.error('Error adding ICE candidate:', err);
            });
    }
}

function handleCallError(data) {
    cleanupCall();
    alert(data.message || 'Call error occurred');
}

function getLocalMedia(type) {
    const constraints = {
        audio: true,
        video: type === 'video' ? {
            width: { ideal: 1280 },
            height: { ideal: 720 }
        } : false
    };
    
    return navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            localStream = stream;
            updateLocalVideo();
            return stream;
        });
}

function createPeerConnection(userId, isCaller) {
    const pc = new RTCPeerConnection(STUN_SERVERS);
    peerConnections[userId] = pc;
    
    // Add local stream tracks
    if (localStream) {
        localStream.getTracks().forEach(track => {
            pc.addTrack(track, localStream);
        });
    }
    
    // Add screen share stream if active
    if (screenShareStream) {
        screenShareStream.getTracks().forEach(track => {
            pc.addTrack(track, screenShareStream);
        });
    }
    
    // Handle remote stream
    pc.ontrack = (event) => {
        remoteStreams[userId] = event.streams[0];
        updateRemoteVideo(userId, event.streams[0]);
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
            // Participant might have left
        }
    };
    
    // Create offer if caller
    if (isCaller) {
        pc.createOffer()
            .then(offer => {
                return pc.setLocalDescription(offer);
            })
            .then(() => {
                socket.emit('call_offer', {
                    call_id: currentCall.callId,
                    to_user_id: userId,
                    offer: pc.localDescription
                });
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
    if (localStream) {
        Object.keys(peerConnections).forEach(userId => {
            const pc = peerConnections[userId];
            const videoTrack = localStream.getVideoTracks()[0];
            if (videoTrack) {
                const sender = pc.getSenders().find(s => s.track && s.track.kind === 'video');
                if (sender) {
                    sender.replaceTrack(videoTrack);
                }
            }
        });
    }
    
    updateScreenShareButton(false);
    updateLocalVideo();
}

function startRecording() {
    if (!localStream || isRecording) return;
    
    const allStreams = [localStream, ...Object.values(remoteStreams)];
    // For simplicity, record local stream only (can be enhanced to mix all streams)
    const streamToRecord = localStream;
    
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(streamToRecord, {
        mimeType: 'video/webm;codecs=vp9,opus'
    });
    
    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    };
    
    mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        downloadRecording(url);
    };
    
    mediaRecorder.start();
    isRecording = true;
    updateRecordButton(true);
}

function stopRecording() {
    if (!mediaRecorder || !isRecording) return;
    
    mediaRecorder.stop();
    isRecording = false;
    updateRecordButton(false);
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
        stopRecording();
    }
    
    // Stop screen share if active
    if (isScreenSharing) {
        stopScreenShare();
    }
    
    // Stop local stream
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    
    // Close all peer connections
    Object.values(peerConnections).forEach(pc => pc.close());
    peerConnections = {};
    
    // Clear remote streams
    remoteStreams = {};
    
    // Clear call state
    currentCall = null;
    currentCallType = null;
    
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
    
    // Update video grid
    updateVideoGrid();
}

function updateVideoGrid() {
    const videoGrid = document.getElementById('videoGrid');
    if (!videoGrid) return;
    
    videoGrid.innerHTML = '';
    
    // Add local video
    const localVideoDiv = document.createElement('div');
    localVideoDiv.className = 'relative bg-black rounded-lg overflow-hidden';
    localVideoDiv.innerHTML = `
        <video id="localVideo" autoplay muted class="w-full h-full object-cover"></video>
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
            remoteVideoDiv.innerHTML = `
                <video id="remoteVideoStream-${userId}" autoplay class="w-full h-full object-cover"></video>
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

function updateLocalVideo() {
    const localVideo = document.getElementById('localVideo');
    if (localVideo) {
        localVideo.srcObject = isScreenSharing ? screenShareStream : localStream;
    }
}

function updateRemoteVideo(userId, stream) {
    const remoteVideo = document.getElementById(`remoteVideoStream-${userId}`);
    if (remoteVideo) {
        remoteVideo.srcObject = stream;
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
    
    if (state === 'incoming') {
        if (acceptBtn) acceptBtn.classList.remove('hidden');
        if (rejectBtn) rejectBtn.classList.remove('hidden');
        if (endCallBtn) endCallBtn.classList.add('hidden');
    } else if (state === 'outgoing') {
        if (acceptBtn) acceptBtn.classList.add('hidden');
        if (rejectBtn) rejectBtn.classList.remove('hidden');
        if (endCallBtn) endCallBtn.classList.add('hidden');
    } else if (state === 'active') {
        if (acceptBtn) acceptBtn.classList.add('hidden');
        if (rejectBtn) rejectBtn.classList.add('hidden');
        if (endCallBtn) endCallBtn.classList.remove('hidden');
    }
}

function hideCallModal() {
    const modal = document.getElementById('callModal');
    if (modal) {
        modal.classList.add('hidden');
    }
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
            muteBtn.classList.toggle('bg-red-500', !audioTracks[0].enabled);
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
            videoBtn.classList.toggle('bg-red-500', !videoTracks[0].enabled);
        }
    }
}

function updateScreenShareButton(isSharing) {
    const screenShareBtn = document.getElementById('screenShareBtn');
    if (screenShareBtn) {
        screenShareBtn.classList.toggle('bg-green-500', isSharing);
        screenShareBtn.classList.toggle('bg-purple-500', !isSharing);
    }
}

function updateRecordButton(isRecording) {
    const recordBtn = document.getElementById('recordBtn');
    if (recordBtn) {
        recordBtn.classList.toggle('bg-red-500', isRecording);
        recordBtn.classList.toggle('bg-gray-500', !isRecording);
    }
}
