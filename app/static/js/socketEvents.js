// Establish a socket connection
const socket = io.connect(`${location.protocol}//${document.domain}:${location.port}`, {
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: Infinity,
    transports: ['polling']
});

// Get room ID from the page
const roomId = $('#roomId').data('id');

// Initialize lastMessageTime to allow immediate message sending
let lastMessageTime = Date.now() - 3000;

// Function to handle socket connection
function setupSocketConnection() {
    socket.on('connect', () => {
        console.log(`Connected. Attempting to join room: ${roomId}`);
        socket.emit('join_room', { roomId });
    });

    socket.on('join_confirmation', data => {
        console.log(`Server confirmed join for room ${data.room}.`);
    });

    socket.on('receive_message', data => {
        // Assuming addMessageToList is defined in uiUpdates.js
        addMessageToList(data.message);
    });
}

// Function to send a message
function sendMessage(message) {
    const now = Date.now();
    if (now - lastMessageTime >= 3000 && message.trim().length > 0) {
        socket.emit('send_message', { message: message.trim(), roomId: roomId });
        lastMessageTime = now;
        // Assuming clearInput and autoScroll are defined in uiUpdates.js
        clearInput();
        autoScroll();
    } else {
        // Optionally handle message send cooldown, e.g., show a warning
        console.log("Please wait before sending another message.");
    }
}

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    setupSocketConnection();

    // Assuming setupUIEventListeners is defined in uiUpdates.js and sets up event listeners for UI elements
    setupUIEventListeners(sendMessage);
});

