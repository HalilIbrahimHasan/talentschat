// Highlight handling (complementary to chat.js)
// This file can be extended for more highlight features

function updateHighlightUI(messageId, action) {
    const messageDiv = document.getElementById(`message-${messageId}`);
    if (!messageDiv) return;
    
    if (action === 'added') {
        messageDiv.classList.add('bg-yellow-50');
    } else {
        messageDiv.classList.remove('bg-yellow-50');
    }
}




