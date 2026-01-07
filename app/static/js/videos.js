// Video page functionality
const likeBtn = document.getElementById('likeBtn');
const likeCount = document.getElementById('likeCount');
const commentForm = document.getElementById('commentForm');
const commentInput = document.getElementById('commentInput');
const commentsDiv = document.getElementById('comments');

if (likeBtn) {
    likeBtn.addEventListener('click', () => {
        fetch(`/api/videos/${VIDEO_ID}/like`, {
            method: 'POST'
        })
        .then(res => res.json())
        .then(data => {
            likeCount.textContent = data.like_count;
            if (data.action === 'liked') {
                likeBtn.classList.add('bg-red-50', 'border-red-200', 'text-red-600');
                likeBtn.classList.remove('bg-gray-50', 'border-gray-200', 'text-gray-600');
            } else {
                likeBtn.classList.remove('bg-red-50', 'border-red-200', 'text-red-600');
                likeBtn.classList.add('bg-gray-50', 'border-gray-200', 'text-gray-600');
            }
        })
        .catch(err => console.error('Error toggling like:', err));
    });
}

if (commentForm) {
    commentForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const content = commentInput.value.trim();
        
        if (!content) return;
        
        fetch(`/api/videos/${VIDEO_ID}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        })
        .then(res => res.json())
        .then(data => {
            addCommentToUI(data);
            commentInput.value = '';
        })
        .catch(err => console.error('Error adding comment:', err));
    });
}

function addCommentToUI(comment) {
    const commentDiv = document.createElement('div');
    commentDiv.className = 'border-b pb-4';
    commentDiv.innerHTML = `
        <div class="flex items-start space-x-3">
            <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">${comment.user_name}</p>
                <p class="text-gray-700 mt-1">${comment.content}</p>
                <p class="text-xs text-gray-500 mt-1">${formatTime(comment.created_at)}</p>
            </div>
        </div>
    `;
    commentsDiv.appendChild(commentDiv);
}

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
}

