// File upload functionality
const fileInput = document.getElementById('fileInput');
const fileUploadBtn = document.getElementById('fileUploadBtn');

if (fileUploadBtn && fileInput) {
    fileUploadBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        files.forEach(file => uploadFile(file));
    });
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('workspace_id', WORKSPACE_ID);
    formData.append('channel_id', CHANNEL_ID);
    
    // Determine file type
    const fileType = file.type.startsWith('video/') ? 'video' : 'documents';
    formData.append('type', fileType);
    
    const xhr = new XMLHttpRequest();
    
    // Progress bar
    const progressDiv = document.createElement('div');
    progressDiv.className = 'fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm';
    progressDiv.innerHTML = `
        <div class="flex items-center space-x-3">
            <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">${file.name}</p>
                <div class="mt-2 bg-gray-200 rounded-full h-2">
                    <div class="bg-indigo-600 h-2 rounded-full" style="width: 0%"></div>
                </div>
            </div>
            <button class="text-gray-400 hover:text-gray-600" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    document.body.appendChild(progressDiv);
    const progressBar = progressDiv.querySelector('.bg-indigo-600');
    
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percent = (e.loaded / e.total) * 100;
            progressBar.style.width = percent + '%';
        }
    });
    
    xhr.addEventListener('load', () => {
        if (xhr.status === 201) {
            const response = JSON.parse(xhr.responseText);
            progressDiv.innerHTML = `
                <div class="flex items-center space-x-2 text-green-600">
                    <i class="fas fa-check-circle"></i>
                    <span class="text-sm">Upload complete!</span>
                </div>
            `;
            setTimeout(() => progressDiv.remove(), 2000);
            
            // If video, redirect to video page
            if (response.type === 'video') {
                setTimeout(() => {
                    window.location.href = `/v/${response.id}`;
                }, 1000);
            }
        } else {
            progressDiv.innerHTML = `
                <div class="flex items-center space-x-2 text-red-600">
                    <i class="fas fa-exclamation-circle"></i>
                    <span class="text-sm">Upload failed</span>
                </div>
            `;
            setTimeout(() => progressDiv.remove(), 3000);
        }
    });
    
    xhr.addEventListener('error', () => {
        progressDiv.innerHTML = `
            <div class="flex items-center space-x-2 text-red-600">
                <i class="fas fa-exclamation-circle"></i>
                <span class="text-sm">Upload error</span>
            </div>
        `;
        setTimeout(() => progressDiv.remove(), 3000);
    });
    
    xhr.open('POST', '/api/upload');
    xhr.send(formData);
}


