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
        
        // Initialize calls after socket is connected
        if (typeof initCalls === 'function') {
            initCalls();
        }
    });
    
    socket.on('joined_room', (data) => {
        console.log('✅ Joined room:', data);
        if (data.online_users) {
            updateOnlineUsers(data.online_users);
        }
    });
    
    socket.on('presence_updated', (data) => {
        console.log('👥 Presence updated:', data);
        if (data.online_users) {
            updateOnlineUsers(data.online_users);
        }
    });
    
    socket.on('joined_room', (data) => {
        console.log('✅ Joined room:', data);
        if (data.online_users) {
            updateOnlineUsers(data.online_users);
        }
    });
    
    socket.on('presence_updated', (data) => {
        console.log('👥 Presence updated:', data);
        if (data.online_users) {
            updateOnlineUsers(data.online_users);
        }
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
    const bgGradient = isOwn 
        ? 'bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-50 border-2 border-indigo-300' 
        : 'bg-gradient-to-br from-white to-blue-50 border-2 border-blue-200';
    
    // Build reactions HTML - ensure we have the reactions array
    const reactions = message.reactions || [];
    console.log(`🎨 Building UI for message ${message.id} with ${reactions.length} reactions:`, reactions);
    const reactionsHtml = buildReactionsHtml(reactions, message.id);
    console.log(`📦 Reactions HTML for message ${message.id}:`, reactionsHtml);
    
    // Random gradient for avatar
    const avatarGradients = [
        'from-indigo-500 to-purple-600',
        'from-blue-500 to-cyan-600',
        'from-pink-500 to-rose-600',
        'from-green-500 to-emerald-600',
        'from-yellow-500 to-orange-600',
        'from-purple-500 to-indigo-600'
    ];
    const avatarGradient = avatarGradients[message.user_id % avatarGradients.length];
    
    messageDiv.innerHTML = `
        <a href="/profile/${message.user_id}" class="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br ${avatarGradient} flex items-center justify-center text-white text-lg font-bold shadow-lg hover:shadow-xl transform hover:scale-105 transition cursor-pointer">
            ${message.user_name.charAt(0).toUpperCase()}
        </a>
        <div class="flex-1 ${bgGradient} rounded-2xl p-4 shadow-md hover:shadow-lg transition">
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                    <a href="/profile/${message.user_id}" class="text-sm font-bold ${isOwn ? 'text-indigo-700' : 'text-gray-900'} hover:underline transition">${message.user_name}</a>
                    ${!isOwn ? `
                    <button onclick="if (typeof initiateCall !== 'undefined') { initiateCall(${message.user_id}, '${escapeHtml(message.user_name)}', 'video'); }" 
                            class="p-1.5 bg-green-500 hover:bg-green-600 text-white rounded-lg transition text-xs" 
                            title="Video call">
                        <i class="fas fa-video"></i>
                    </button>
                    ` : ''}
                </div>
                <span class="text-xs ${isOwn ? 'text-indigo-600' : 'text-gray-500'} font-medium">${formatTime(message.created_at)}</span>
            </div>
            <div class="text-gray-800 mb-3 leading-relaxed">${message.content_html || message.content}</div>
            ${detectAndEmbedVideos(message.content)}
            <div id="reactions-wrapper-${message.id}" class="reactions-wrapper">
                ${reactionsHtml}
            </div>
            <div class="flex items-center space-x-2 mt-3">
                <button class="emoji-picker-btn text-xs font-semibold ${isOwn ? 'text-indigo-600 hover:text-indigo-800' : 'text-gray-600 hover:text-gray-800'} px-3 py-2 rounded-lg hover:bg-white/50 transition" data-message-id="${message.id}">
                    😀 Add Reaction
                </button>
                <button class="highlight-btn text-xs font-semibold ${isOwn ? 'text-yellow-600 hover:text-yellow-800' : 'text-yellow-600 hover:text-yellow-800'} px-3 py-2 rounded-lg hover:bg-yellow-50 transition" data-message-id="${message.id}">
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
    
    // Color gradients for different emojis
    const emojiColors = {
        '👍': 'from-green-400 to-emerald-500',
        '❤️': 'from-red-400 to-pink-500',
        '😂': 'from-yellow-400 to-orange-500',
        '😮': 'from-blue-400 to-cyan-500',
        '😢': 'from-indigo-400 to-purple-500',
        '🔥': 'from-red-500 to-orange-500',
        '🎉': 'from-yellow-400 to-pink-500',
        '👏': 'from-purple-400 to-indigo-500',
        '😀': 'from-yellow-400 to-orange-500',
        '😍': 'from-pink-400 to-rose-500'
    };
    
    let html = `<div class="reactions-container mt-2 flex flex-wrap gap-2" data-message-id="${msgId}">`;
    for (const [emoji, users] of Object.entries(reactionGroups)) {
        const count = users.length;
        const userReacted = users.some(r => r.user_id === CURRENT_USER_ID);
        const gradient = emojiColors[emoji] || 'from-indigo-400 to-purple-500';
        const shadowClass = userReacted ? 'shadow-lg ring-2 ring-white' : 'shadow-md';
        html += `
            <button class="reaction-item bg-gradient-to-r ${gradient} ${shadowClass} text-white rounded-full px-3 py-1.5 text-sm flex items-center space-x-1 hover:shadow-xl transform hover:scale-110 transition cursor-pointer font-semibold" 
                    data-emoji="${emoji}" data-message-id="${msgId}">
                <span class="text-base">${emoji}</span>
                <span class="ml-1">${count}</span>
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

function detectAndEmbedVideos(text) {
    if (!text) return '';
    
    let embedHtml = '';
    
    // YouTube
    const youtubePattern = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/g;
    let match;
    const foundIds = new Set(); // Avoid duplicates
    
    while ((match = youtubePattern.exec(text)) !== null) {
        const videoId = match[1];
        if (!foundIds.has(videoId)) {
            foundIds.add(videoId);
            embedHtml += `
                <div class="my-3">
                    <iframe width="100%" height="315" 
                        src="https://www.youtube.com/embed/${videoId}" 
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen
                        class="rounded-lg"
                        style="max-width: 560px;">
                    </iframe>
                </div>
            `;
        }
    }
    
    // Vimeo
    const vimeoPattern = /(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(\d+)/g;
    foundIds.clear();
    while ((match = vimeoPattern.exec(text)) !== null) {
        const videoId = match[1];
        if (!foundIds.has(videoId)) {
            foundIds.add(videoId);
            embedHtml += `
                <div class="my-3">
                    <iframe src="https://player.vimeo.com/video/${videoId}" 
                        width="100%" 
                        height="315" 
                        frameborder="0" 
                        allow="autoplay; fullscreen; picture-in-picture" 
                        allowfullscreen
                        class="rounded-lg"
                        style="max-width: 560px;">
                    </iframe>
                </div>
            `;
        }
    }
    
    return embedHtml;
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Message form handler
    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
        messageForm.addEventListener('submit', (e) => {
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
    }
    
    // Initialize socket and load messages
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

function updateOnlineUsers(users) {
    const onlineUsersDiv = document.getElementById('onlineUsers');
    if (!onlineUsersDiv) return;
    
    if (!users || users.length === 0) {
        onlineUsersDiv.innerHTML = '<div class="text-xs text-gray-400">No one online</div>';
        return;
    }
    
    // Remove current user from list (they see themselves as "You")
    const filteredUsers = users.filter(u => u.id !== CURRENT_USER_ID);
    
    let html = '';
    
    // Show current user first
    const currentUser = users.find(u => u.id === CURRENT_USER_ID);
    if (currentUser) {
        html += `
            <div class="flex items-center space-x-2 px-2 py-1 rounded text-xs">
                <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                <span class="text-gray-700 font-medium">You</span>
            </div>
        `;
    }
    
    // Show other online users
    filteredUsers.forEach(user => {
        html += `
            <div class="flex items-center justify-between px-2 py-2 rounded hover:bg-white/20 transition">
                <a href="/profile/${user.id}" class="flex items-center space-x-2 flex-1 text-xs">
                    <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span class="text-white/90 hover:text-white font-medium">${escapeHtml(user.name)}</span>
                </a>
                <div class="flex space-x-1">
                    <button onclick="if (typeof initiateCall !== 'undefined') { initiateCall(${user.id}, '${escapeHtml(user.name)}', 'video'); }" 
                            class="p-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition shadow-md hover:shadow-lg" 
                            title="Video call">
                        <i class="fas fa-video text-xs"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    onlineUsersDiv.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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
