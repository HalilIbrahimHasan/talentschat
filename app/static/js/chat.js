// Chat functionality with SocketIO
let socket;
let currentChannelId = CHANNEL_ID;
let emojiPickerVisible = null; // Track which message's picker is visible

// Popular emojis for quick access
const popularEmojis = ['👍', '❤️', '😂', '😮', '😢', '🔥', '🎉', '👏', '🙌', '💯', '✨', '🎯', '🚀', '💪', '👀'];

// Extended emoji list
const allEmojis = [
    '👍', '👎', '❤️', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎',
    '😂', '😮', '😢', '😡', '😱', '😴', '🤔', '😎', '🥳', '😍',
    '🔥', '💯', '✨', '⭐', '🌟', '💫', '🎉', '🎊', '🎈', '🎁',
    '👏', '🙌', '🤝', '👍', '👎', '✊', '👊', '🤞', '🤟', '🤘',
    '🚀', '💪', '👀', '👁️', '🧠', '💭', '🗣️', '👤', '👥', '🤖',
    '✅', '❌', '⚠️', '❓', '❗', '💡', '🔔', '🔕', '📢', '📣',
    '🎯', '🏆', '🥇', '🥈', '🥉', '🎖️', '🏅', '🎗️', '🎪', '🎭',
    '🎨', '🖼️', '🎬', '📸', '📷', '📹', '🎥', '📺', '📻', '🎙️',
    '🎚️', '🎛️', '🎤', '🎧', '📻', '💿', '📀', '💾', '💽', '📱',
    '📞', '☎️', '📟', '📠', '📧', '📨', '📩', '📤', '📥', '📦'
];

function initSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('✅ Connected to server, socket ID:', socket.id);
        socket.emit('join_room', { channel_id: currentChannelId });
        console.log('📤 Emitted join_room for channel:', currentChannelId);
    });
    
    socket.on('joined_room', (data) => {
        console.log('✅ Joined room:', data);
    });
    
    socket.on('connected', (data) => {
        console.log('✅ Server confirmed connection:', data);
    });
    
    socket.on('message_created', (data) => {
        addMessageToUI(data);
    });
    
    socket.on('reaction_updated', (data) => {
        console.log('✅ Socket received reaction_updated event:', data);
        console.log('Reactions in event:', data.reactions);
        updateReaction(data);
    });
    
    socket.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
    });
    
    socket.on('disconnect', (reason) => {
        console.log('Socket disconnected:', reason);
    });
    
    socket.on('highlight_updated', (data) => {
        updateHighlight(data);
    });
    
    socket.on('user_typing', (data) => {
        // Show typing indicator (optional)
    });
}

function addMessageToUI(message) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3';
    messageDiv.id = `message-${message.id}`;
    
    const isOwn = message.user_id === CURRENT_USER_ID;
    const bgColor = isOwn ? 'bg-indigo-50' : 'bg-white';
    
    // Build reactions HTML - ensure we have the reactions array
    const reactions = message.reactions || [];
    console.log(`🎨 Building UI for message ${message.id} with ${reactions.length} reactions:`, reactions);
    const reactionsHtml = buildReactionsHtml(reactions, message.id);
    console.log(`📦 Reactions HTML for message ${message.id}:`, reactionsHtml);
    
    messageDiv.innerHTML = `
        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm">
            ${message.user_name.charAt(0).toUpperCase()}
        </div>
        <div class="flex-1 ${bgColor} rounded-lg p-3">
            <div class="flex items-center justify-between mb-1">
                <span class="text-sm font-medium text-gray-900">${message.user_name}</span>
                <span class="text-xs text-gray-500">${formatTime(message.created_at)}</span>
            </div>
            <div class="text-gray-700 mb-2">${message.content_html || message.content}</div>
            <div id="reactions-wrapper-${message.id}" class="reactions-wrapper">
                ${reactionsHtml}
            </div>
            <div class="flex items-center space-x-2 mt-2">
                <button class="emoji-picker-btn text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-100" data-message-id="${message.id}">
                    😀 Add Reaction
                </button>
                <button class="highlight-btn text-xs text-gray-500 hover:text-yellow-600 px-2 py-1 rounded hover:bg-gray-100" data-message-id="${message.id}">
                    ⭐ Highlight
                </button>
            </div>
        </div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    
    // Verify reactions wrapper was created
    const wrapper = messageDiv.querySelector(`#reactions-wrapper-${message.id}`);
    if (wrapper) {
        console.log(`✅ Reactions wrapper created for message ${message.id}`);
        console.log(`   Wrapper HTML:`, wrapper.innerHTML);
        console.log(`   Has reaction items:`, wrapper.querySelectorAll('.reaction-item').length);
    } else {
        console.error(`❌ Reactions wrapper NOT found for message ${message.id}`);
    }
    
    scrollToBottom();
    
    // Attach event listeners
    attachMessageListeners(messageDiv);
}

function buildReactionsHtml(reactions, messageId = null) {
    // Always create container, even if empty
    const msgId = messageId || (reactions && reactions[0] && reactions[0].message_id) || '';
    
    console.log('buildReactionsHtml called with:', { reactions, messageId: msgId, reactionsLength: reactions ? reactions.length : 0 });
    
    if (!reactions || reactions.length === 0) {
        console.log('No reactions, returning empty container');
        return `<div class="reactions-container mt-2 flex flex-wrap gap-1" data-message-id="${msgId}"></div>`;
    }
    
    // Group reactions by emoji
    const reactionGroups = {};
    reactions.forEach(r => {
        if (!r || !r.emoji) {
            console.warn('Invalid reaction:', r);
            return;
        }
        if (!reactionGroups[r.emoji]) {
            reactionGroups[r.emoji] = [];
        }
        reactionGroups[r.emoji].push(r);
    });
    
    console.log('Reaction groups:', reactionGroups);
    
    if (Object.keys(reactionGroups).length === 0) {
        return `<div class="reactions-container mt-2 flex flex-wrap gap-1" data-message-id="${msgId}"></div>`;
    }
    
    let html = `<div class="reactions-container mt-2 flex flex-wrap gap-1" data-message-id="${msgId}">`;
    for (const [emoji, users] of Object.entries(reactionGroups)) {
        const count = users.length;
        const userReacted = users.some(r => r.user_id === CURRENT_USER_ID);
        const bgClass = userReacted ? 'bg-indigo-100 border-indigo-300' : 'bg-gray-100 border-gray-300';
        html += `
            <button class="reaction-item ${bgClass} border rounded-full px-2 py-1 text-xs flex items-center space-x-1 hover:bg-indigo-50 cursor-pointer" 
                    data-emoji="${emoji}" data-message-id="${msgId}">
                <span class="text-lg">${emoji}</span>
                <span class="text-gray-600 font-medium ml-1">${count}</span>
            </button>
        `;
    }
    html += '</div>';
    console.log('Built reactions HTML:', html);
    return html;
}

function attachMessageListeners(messageDiv) {
    const emojiPickerBtn = messageDiv.querySelector('.emoji-picker-btn');
    const highlightBtn = messageDiv.querySelector('.highlight-btn');
    const reactionItems = messageDiv.querySelectorAll('.reaction-item');
    
    if (emojiPickerBtn) {
        // Remove existing listeners to avoid duplicates
        const newBtn = emojiPickerBtn.cloneNode(true);
        emojiPickerBtn.parentNode.replaceChild(newBtn, emojiPickerBtn);
        newBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const messageId = newBtn.dataset.messageId;
            console.log('Emoji picker button clicked for message:', messageId);
            if (messageId) {
                toggleEmojiPicker(messageId);
            }
        });
    }
    
    if (highlightBtn) {
        const newHighlightBtn = highlightBtn.cloneNode(true);
        highlightBtn.parentNode.replaceChild(newHighlightBtn, highlightBtn);
        newHighlightBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const messageId = newHighlightBtn.dataset.messageId;
            if (messageId) {
                toggleHighlight(messageId);
            }
        });
    }
    
    // Add click handlers to existing reactions
    reactionItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const messageId = item.dataset.messageId;
            const emoji = item.dataset.emoji;
            console.log('Reaction item clicked:', { messageId, emoji });
            if (messageId && emoji) {
                toggleReaction(messageId, emoji);
            }
        });
    });
}

function toggleEmojiPicker(messageId) {
    console.log('toggleEmojiPicker called for message:', messageId);
    // Close any open picker
    const existingPicker = document.getElementById('emoji-picker');
    if (existingPicker) {
        if (emojiPickerVisible === messageId) {
            existingPicker.remove();
            emojiPickerVisible = null;
            return;
        } else {
            existingPicker.remove();
        }
    }
    
    // Create emoji picker
    const picker = document.createElement('div');
    picker.id = 'emoji-picker';
    picker.className = 'fixed bg-white border border-gray-300 rounded-lg shadow-lg p-4 z-50 max-w-xs';
    picker.style.maxHeight = '300px';
    picker.style.overflowY = 'auto';
    
    // Popular emojis section
    let html = '<div class="mb-3"><div class="text-xs font-semibold text-gray-600 mb-2">Quick Reactions</div><div class="flex flex-wrap gap-2">';
    popularEmojis.forEach(emoji => {
        html += `<button class="emoji-option text-2xl hover:bg-gray-100 rounded p-1" data-emoji="${emoji}" data-message-id="${messageId}">${emoji}</button>`;
    });
    html += '</div></div>';
    
    // All emojis section
    html += '<div><div class="text-xs font-semibold text-gray-600 mb-2">All Emojis</div><div class="flex flex-wrap gap-2">';
    allEmojis.forEach(emoji => {
        html += `<button class="emoji-option text-xl hover:bg-gray-100 rounded p-1" data-emoji="${emoji}" data-message-id="${messageId}">${emoji}</button>`;
    });
    html += '</div></div>';
    
    picker.innerHTML = html;
    
    // Position picker near the button
    const button = document.querySelector(`[data-message-id="${messageId}"].emoji-picker-btn`);
    if (button) {
        const rect = button.getBoundingClientRect();
        picker.style.top = `${rect.bottom + 5}px`;
        picker.style.left = `${rect.left}px`;
    } else {
        picker.style.top = '50%';
        picker.style.left = '50%';
        picker.style.transform = 'translate(-50%, -50%)';
    }
    
    document.body.appendChild(picker);
    emojiPickerVisible = messageId;
    
    // Add click handlers to emoji options
    picker.querySelectorAll('.emoji-option').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const emoji = btn.dataset.emoji;
            const msgId = btn.dataset.messageId;
            console.log('Emoji clicked:', emoji, 'for message:', msgId);
            toggleReaction(msgId, emoji);
            picker.remove();
            emojiPickerVisible = null;
        });
    });
    
    // Close picker when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function closePicker(e) {
            if (!picker.contains(e.target) && e.target.closest('.emoji-picker-btn') !== button) {
                picker.remove();
                emojiPickerVisible = null;
                document.removeEventListener('click', closePicker);
            }
        });
    }, 100);
}

function formatTime(isoString) {
    if (!isoString) return 'just now';
    
    // Parse the ISO string - handle both with and without timezone
    let date;
    if (isoString.endsWith('Z')) {
        // UTC time
        date = new Date(isoString);
    } else if (isoString.includes('+') || isoString.includes('-') && isoString.length > 19) {
        // Has timezone offset
        date = new Date(isoString);
    } else {
        // No timezone - assume UTC
        date = new Date(isoString + 'Z');
    }
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
        console.error('Invalid date:', isoString);
        return 'just now';
    }
    
    const now = new Date();
    const diff = now - date;
    
    // Handle negative diff (future dates) - shouldn't happen but just in case
    if (diff < 0) {
        return 'just now';
    }
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    // For older dates, show formatted date
    return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
}

function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    container.scrollTop = container.scrollHeight;
}

function loadMessages() {
    fetch(`/api/channels/${currentChannelId}/messages?limit=50`)
        .then(res => res.json())
        .then(messages => {
            console.log('📨 Loaded messages:', messages.length);
            messages.forEach(msg => {
                const reactionCount = msg.reactions ? msg.reactions.length : 0;
                console.log(`Message ${msg.id}: "${msg.content.substring(0, 20)}..." - ${reactionCount} reactions`, msg.reactions);
            });
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = '';
            messages.forEach(msg => {
                console.log(`Rendering message ${msg.id} with ${msg.reactions?.length || 0} reactions`);
                addMessageToUI(msg);
            });
        })
        .catch(err => console.error('Error loading messages:', err));
}

// Message form handler
document.getElementById('messageForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('messageInput');
    const content = input.value.trim();
    
    if (!content) return;
    
    if (socket && socket.connected) {
        socket.emit('send_message', {
            channel_id: currentChannelId,
            content: content
        });
    } else {
        // Fallback to HTTP
        fetch('/api/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                channel_id: currentChannelId,
                content: content
            })
        })
        .then(res => res.json())
        .then(data => {
            addMessageToUI(data);
        });
    }
    
    input.value = '';
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initSocket();
    loadMessages();
});

function toggleReaction(messageId, emoji) {
    console.log('toggleReaction called:', { messageId, emoji, socketConnected: socket && socket.connected });
    const msgId = parseInt(messageId);
    
    if (socket && socket.connected) {
        console.log('Emitting add_reaction via socket:', { message_id: msgId, emoji });
        socket.emit('add_reaction', {
            message_id: msgId,
            emoji: emoji
        });
        
        // Fallback: if socket event doesn't arrive in 2 seconds, use HTTP
        setTimeout(() => {
            const messageDiv = document.getElementById(`message-${msgId}`);
            const reactionsWrapper = messageDiv?.querySelector(`#reactions-wrapper-${msgId}`);
            const hasReactions = reactionsWrapper?.querySelector('.reaction-item');
            
            if (!hasReactions) {
                console.log('⚠️ Socket event not received after 2s, using HTTP fallback');
                fetch(`/api/messages/${msgId}/reactions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ emoji: emoji })
                })
                .then(res => res.json())
                .then(data => {
                    console.log('✅ Reaction HTTP response:', data);
                    if (data.reactions) {
                        updateReaction({
                            message_id: msgId,
                            reactions: data.reactions
                        });
                    } else {
                        // Reload messages to get updated reactions
                        fetch(`/api/channels/${currentChannelId}/messages?limit=50`)
                            .then(res => res.json())
                            .then(messages => {
                                const message = messages.find(m => m.id === msgId);
                                console.log('Found message after reaction:', message);
                                if (message) {
                                    updateReaction({
                                        message_id: msgId,
                                        reactions: message.reactions || []
                                    });
                                }
                            });
                    }
                })
                .catch(err => console.error('Error toggling reaction:', err));
            } else {
                console.log('✅ Reactions already visible, socket worked!');
            }
        }, 2000);
    } else {
        console.log('Socket not connected, using HTTP fallback');
        fetch(`/api/messages/${msgId}/reactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emoji: emoji })
        })
        .then(res => res.json())
        .then(data => {
            console.log('Reaction HTTP response:', data);
            // Fetch updated reactions for this message
            fetch(`/api/channels/${currentChannelId}/messages?limit=50`)
                .then(res => res.json())
                .then(messages => {
                    const message = messages.find(m => m.id === msgId);
                    console.log('Found message after reaction:', message);
                    if (message) {
                        updateReaction({
                            message_id: msgId,
                            reactions: message.reactions || []
                        });
                    }
                });
        })
        .catch(err => console.error('Error toggling reaction:', err));
    }
}

function toggleHighlight(messageId) {
    if (socket && socket.connected) {
        socket.emit('toggle_highlight', {
            message_id: messageId
        });
    } else {
        fetch(`/api/messages/${messageId}/highlight`, {
            method: 'POST'
        });
    }
}

function updateReaction(data) {
    console.log('🔄 updateReaction called with:', data);
    const msgId = data.message_id;
    const reactions = data.reactions || [];
    
    console.log(`📝 Updating reactions for message ${msgId}, count: ${reactions.length}`);
    
    // Update reactions for the message
    const messageDiv = document.getElementById(`message-${msgId}`);
    if (!messageDiv) {
        console.error(`❌ Message div not found for: ${msgId}`);
        // Try to reload messages if div doesn't exist
        setTimeout(() => loadMessages(), 500);
        return;
    }
    
    console.log('✅ Found message div');
    
    // Find or create reactions wrapper
    let reactionsWrapper = messageDiv.querySelector(`#reactions-wrapper-${msgId}`);
    if (!reactionsWrapper) {
        console.log('⚠️ Reactions wrapper not found, creating...');
        const contentDiv = messageDiv.querySelector('.text-gray-700');
        if (contentDiv && contentDiv.parentElement) {
            reactionsWrapper = document.createElement('div');
            reactionsWrapper.id = `reactions-wrapper-${msgId}`;
            reactionsWrapper.className = 'reactions-wrapper';
            contentDiv.parentElement.insertBefore(reactionsWrapper, contentDiv.nextSibling);
            console.log('✅ Created reactions wrapper');
        } else {
            console.error('❌ Could not find content div or parent');
            return;
        }
    }
    
    // Build and update reactions HTML
    const newHtml = buildReactionsHtml(reactions, msgId);
    console.log('📦 New reactions HTML:', newHtml);
    reactionsWrapper.innerHTML = newHtml;
    
    // Reattach listeners
    attachMessageListeners(messageDiv);
    
    // Force a visual update
    reactionsWrapper.style.display = 'block';
    reactionsWrapper.style.visibility = 'visible';
    
    console.log('✅ Reactions updated successfully!');
    console.log('🔍 Reactions wrapper after update:', reactionsWrapper.innerHTML);
}

function updateHighlight(data) {
    const messageDiv = document.getElementById(`message-${data.message_id}`);
    if (!messageDiv) return;
    
    if (data.action === 'added') {
        messageDiv.classList.add('bg-yellow-50');
        messageDiv.classList.remove('bg-white', 'bg-indigo-50');
    } else {
        // Restore original background
        const isOwn = messageDiv.querySelector('.text-gray-900').textContent === document.querySelector('.text-gray-700').textContent;
        messageDiv.querySelector('.flex-1').classList.remove('bg-yellow-50');
        messageDiv.querySelector('.flex-1').classList.add(isOwn ? 'bg-indigo-50' : 'bg-white');
    }
}
