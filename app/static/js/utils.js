// Function to start a countdown timer for any purpose, e.g., before sending the next message
function startCountdown(duration, displayElementId) {
    let remainingTime = duration;
    const countdownElement = document.getElementById(displayElementId);
    countdownElement.textContent = `Next message in ${remainingTime} seconds`;

    const countdownTimer = setInterval(() => {
        remainingTime -= 1;
        countdownElement.textContent = `Next message in ${remainingTime} seconds`;

        if (remainingTime <= 0) {
            clearInterval(countdownTimer);
            countdownElement.textContent = ''; // Hide the countdown
        }
    }, 1000);
}

// Example utility function for formatting dates, which could be used for timestamping messages
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

// Utility function to debounce rapid-fire events, e.g., for live search or resizing events
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Function to validate message content if needed, e.g., for preventing empty messages or messages with only whitespace
function isValidMessage(message) {
    return message && message.trim().length > 0;
}

// Any additional utility functions needed across the application can be added here

