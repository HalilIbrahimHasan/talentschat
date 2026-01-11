// Video recording and screen sharing functionality

let recordingMediaRecorder = null;
let recordingRecordedChunks = [];
let recordingStream = null;
let selfRecordingStartTime = null; // Renamed from recordingStartTime to avoid conflict with calls.js
let recordingTimer = null;
let isSelfRecording = false; // Changed from isRecording to avoid conflict with calls.js
let isScreenShare = false;

const MAX_RECORDING_DURATION = 30 * 60 * 1000; // 30 minutes in milliseconds

// Initialize recording UI
function initRecording() {
    console.log('Initializing recording UI...');
    const recordBtn = document.getElementById('recordBtn');
    const screenRecordingBtn = document.getElementById('screenRecordingBtn');
    const recordingModal = document.getElementById('recordingModal');
    const stopRecordingBtn = document.getElementById('stopRecordingBtn');
    const cancelRecordingBtn = document.getElementById('cancelRecordingBtn');
    const previewVideo = document.getElementById('previewVideo');
    const recordingTimerEl = document.getElementById('recordingTimer');
    
    console.log('recordBtn found:', !!recordBtn);
    console.log('screenRecordingBtn found:', !!screenRecordingBtn);
    
    if (recordBtn) {
        recordBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Record button clicked!');
            console.log('Calling startRecording("camera")...');
            try {
                await startRecording('camera');
                console.log('startRecording completed');
            } catch (error) {
                console.error('Error in startRecording:', error);
                alert('Error starting recording: ' + error.message);
            }
        });
        console.log('Record button event listener attached');
    } else {
        console.error('Record button not found!');
    }
    
    if (screenRecordingBtn) {
        screenRecordingBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Screen recording button clicked!');
            startRecording('screen');
        });
        console.log('Screen recording button event listener attached');
    } else {
        console.warn('Screen recording button not found!');
    }
    
    if (stopRecordingBtn) {
        stopRecordingBtn.addEventListener('click', stopRecording);
    }
    
    if (cancelRecordingBtn) {
        cancelRecordingBtn.addEventListener('click', cancelRecording);
    }
    
    console.log('Recording UI initialized');
}

async function startRecording(type) {
    try {
        console.log('startRecording called with type:', type);
        isScreenShare = (type === 'screen');
        
        // Request media access
        console.log('Requesting media access...');
        if (type === 'screen') {
            recordingStream = await navigator.mediaDevices.getDisplayMedia({
                video: { mediaSource: 'screen' },
                audio: true
            });
        } else {
            console.log('Calling getUserMedia for camera...');
            recordingStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });
            console.log('getUserMedia succeeded, stream obtained:', recordingStream);
        }
        
        // Show preview
        const previewVideo = document.getElementById('previewVideo');
        if (previewVideo) {
            previewVideo.srcObject = recordingStream;
            previewVideo.play();
        }
        
        // Show recording modal
        const recordingModal = document.getElementById('recordingModal');
        if (recordingModal) {
            recordingModal.classList.remove('hidden');
        }
        
        // Setup MediaRecorder
        const options = {
            mimeType: 'video/webm;codecs=vp9,opus',
            videoBitsPerSecond: 2500000 // 2.5 Mbps for good quality
        };
        
        // Fallback to webm if vp9 not supported
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = 'video/webm;codecs=vp8,opus';
        }
        
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = 'video/webm';
        }
        
        recordingMediaRecorder = new MediaRecorder(recordingStream, options);
        recordingRecordedChunks = [];
        
        recordingMediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordingRecordedChunks.push(event.data);
            }
        };
        
        recordingMediaRecorder.onstop = () => {
            handleRecordingComplete();
        };
        
        recordingMediaRecorder.onerror = (event) => {
            console.error('MediaRecorder error:', event.error);
            alert('Recording error: ' + event.error.message);
            cancelRecording();
        };
        
        // Start recording
        recordingMediaRecorder.start(1000); // Collect data every second
        isSelfRecording = true;
        selfRecordingStartTime = Date.now();
        
        // Start timer
        updateRecordingTimer();
        recordingTimer = setInterval(updateRecordingTimer, 1000);
        
        // Auto-stop at 30 minutes
        setTimeout(() => {
            if (isSelfRecording) {
                stopRecording();
            }
        }, MAX_RECORDING_DURATION);
        
        // Handle stream end (user stops sharing screen)
        recordingStream.getVideoTracks()[0].addEventListener('ended', () => {
            if (isSelfRecording) {
                stopRecording();
            }
        });
        
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Could not start recording: ' + error.message);
        cancelRecording();
    }
}

function updateRecordingTimer() {
    if (!isSelfRecording || !selfRecordingStartTime) return;
    
    const elapsed = Date.now() - selfRecordingStartTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    const recordingTimerEl = document.getElementById('recordingTimer');
    if (recordingTimerEl) {
        recordingTimerEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
    
    // Check if approaching 30 minute limit
    if (elapsed >= MAX_RECORDING_DURATION - 60000) { // 1 minute before limit
        const warningEl = document.getElementById('recordingWarning');
        if (warningEl) {
            warningEl.classList.remove('hidden');
            warningEl.textContent = 'Recording will stop automatically in 1 minute (30 min limit)';
        }
    }
}

function stopRecording() {
    if (!isSelfRecording || !recordingMediaRecorder) return;
    
    isSelfRecording = false;
    recordingMediaRecorder.stop();
    
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
    
    // Stop all tracks
    if (recordingStream) {
        recordingStream.getTracks().forEach(track => track.stop());
    }
    
    // Hide preview
    const previewVideo = document.getElementById('previewVideo');
    if (previewVideo) {
        previewVideo.srcObject = null;
    }
}

function cancelRecording() {
    if (isSelfRecording) {
        recordingMediaRecorder.stop();
    }
    
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
    
    if (recordingStream) {
        recordingStream.getTracks().forEach(track => track.stop());
        recordingStream = null;
    }
    
    recordingRecordedChunks = [];
    isSelfRecording = false;
    
    const recordingModal = document.getElementById('recordingModal');
    if (recordingModal) {
        recordingModal.classList.add('hidden');
    }
    
    const previewVideo = document.getElementById('previewVideo');
    if (previewVideo) {
        previewVideo.srcObject = null;
    }
    
    const warningEl = document.getElementById('recordingWarning');
    if (warningEl) {
        warningEl.classList.add('hidden');
    }
}

async function handleRecordingComplete() {
    if (recordingRecordedChunks.length === 0) {
        alert('No recording data available');
        cancelRecording();
        return;
    }
    
    // Create blob from chunks
    const blob = new Blob(recordingRecordedChunks, { type: 'video/webm' });
    
    // Check file size (max 200MB)
    const maxSize = 200 * 1024 * 1024;
    if (blob.size > maxSize) {
        alert('Recording is too large (max 200MB). Please record a shorter video.');
        cancelRecording();
        return;
    }
    
    // Create file from blob
    const filename = `recording_${Date.now()}.webm`;
    const file = new File([blob], filename, { type: 'video/webm' });
    
    // Upload the recording
    await uploadRecording(file, isScreenShare ? 'screen_share' : 'recording');
    
    // Reset
    recordingRecordedChunks = [];
    isSelfRecording = false;
    
    const recordingModal = document.getElementById('recordingModal');
    if (recordingModal) {
        recordingModal.classList.add('hidden');
    }
    
    const warningEl = document.getElementById('recordingWarning');
    if (warningEl) {
        warningEl.classList.add('hidden');
    }
}

async function uploadRecording(file, videoType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('workspace_id', WORKSPACE_ID);
    formData.append('channel_id', CHANNEL_ID);
    formData.append('type', 'video');
    formData.append('video_type', videoType);
    
    // Show upload progress
    const progressDiv = document.createElement('div');
    progressDiv.className = 'fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm z-50';
    progressDiv.innerHTML = `
        <div class="flex items-center space-x-3">
            <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">Uploading recording...</p>
                <div class="mt-2 bg-gray-200 rounded-full h-2">
                    <div class="bg-indigo-600 h-2 rounded-full" style="width: 0%"></div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(progressDiv);
    const progressBar = progressDiv.querySelector('.bg-indigo-600');
    
    try {
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = (e.loaded / e.total) * 100;
                progressBar.style.width = percent + '%';
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 201) {
                const response = JSON.parse(xhr.responseText);
                progressBar.style.width = '100%';
                
                // Send message with video link
                const messageContent = videoType === 'screen_share' 
                    ? `📹 Screen recording shared` 
                    : `🎥 Video recording shared`;
                
                // Use socket to send message
                if (window.socket) {
                    window.socket.emit('send_message', {
                        channel_id: CHANNEL_ID,
                        content: messageContent,
                        video_id: response.id
                    });
                }
                
                setTimeout(() => {
                    progressDiv.remove();
                }, 1000);
            } else {
                alert('Failed to upload recording');
                progressDiv.remove();
            }
        });
        
        xhr.addEventListener('error', () => {
            alert('Error uploading recording');
            progressDiv.remove();
        });
        
        xhr.open('POST', '/api/upload');
        xhr.send(formData);
        
    } catch (error) {
        console.error('Error uploading recording:', error);
        alert('Error uploading recording: ' + error.message);
        progressDiv.remove();
    }
}

// Make startRecording globally available
window.startRecording = startRecording;

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRecording);
} else {
    initRecording();
}

