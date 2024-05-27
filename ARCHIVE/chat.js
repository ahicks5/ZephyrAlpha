var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port, {
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: Infinity,
    transports: ['polling']
});

var roomId = $('#roomId').data('id');
// Set lastMessageTime to 5 seconds ago so the first message can be sent immediately
var lastMessageTime = Date.now() - 5000;

// Emit join_room event immediately after connection
socket.on('connect', function() {
    console.log("Connected. Attempting to join room:", roomId);
    socket.emit('join_room', {roomId: roomId});
});

// Listen for join_confirmation from the server
socket.on('join_confirmation', function(data) {
    console.log(`Server confirmed join for room ${data.room}.`);
    // Show the confirmation message
    document.getElementById('joinConfirmation').style.display = 'block';
});

socket.on('receive_message', function(data) {
    var messagesList = document.getElementById('messages');
    var li = document.createElement('li');
    li.textContent = data.message;
    messagesList.appendChild(li);

    // Limit the number of messages to 100
    while (messagesList.children.length > 100) {
        messagesList.removeChild(messagesList.firstChild);
    }

    // Auto-scroll to the bottom
    messagesList.scrollTop = messagesList.scrollHeight;
});


function sendMessage() {
    var now = Date.now();
    if (now - lastMessageTime >= 3000) {
        var input = document.getElementById("myMessage");
        var message = input.value.trim();
        if (message) {
            socket.emit('send_message', {message: message, roomId: roomId});
            input.value = '';
            lastMessageTime = now;
        }
        // Auto-scroll to the bottom when sending a message
        var messagesList = document.getElementById('messages');
        messagesList.scrollTop = messagesList.scrollHeight;
    } else {
        // Optionally handle message send cooldown
    }
}

function updateProbabilityBars() {
    var bars = document.querySelectorAll('.probability-bar');
    bars.forEach(function(bar) {
        var homeProb = bar.getAttribute('data-home-prob');
        var awayProb = bar.getAttribute('data-away-prob');
        var overProb = bar.getAttribute('data-over-prob');
        var underProb = bar.getAttribute('data-under-prob');

        bar.innerHTML = ''; // Clear previous content

        if (homeProb && awayProb) {
            bar.style.position = 'relative';
            var homeWidth = parseFloat(homeProb);
            var awayWidth = parseFloat(awayProb);

            // Create home (green) section
            var homeDiv = document.createElement('div');
            homeDiv.className = 'home';
            homeDiv.style.width = `${homeWidth}%`;
            homeDiv.style.backgroundColor = 'green';
            homeDiv.style.height = '100%';
            homeDiv.style.position = 'absolute';
            homeDiv.style.right = '0'; // Position from the right

            var homeText = document.createElement('span');
            homeText.className = 'probability-text';
            homeText.style.position = 'absolute';
            homeText.style.right = '5px'; // Ensure some padding
            homeText.style.color = 'white';
            homeText.style.fontSize = '11px';
            homeText.textContent = `${homeProb}%`;
            homeDiv.appendChild(homeText);

            // Create away (red) section
            var awayDiv = document.createElement('div');
            awayDiv.className = 'away';
            awayDiv.style.width = `${awayWidth}%`;
            awayDiv.style.backgroundColor = 'red';
            awayDiv.style.height = '100%';
            awayDiv.style.position = 'absolute';
            awayDiv.style.left = '0'; // Position from the left

            var awayText = document.createElement('span');
            awayText.className = 'probability-text';
            awayText.style.position = 'absolute';
            awayText.style.left = '5px'; // Ensure some padding
            awayText.style.color = 'white';
            awayText.style.fontSize = '11px';
            awayText.textContent = `${awayProb}%`;
            awayDiv.appendChild(awayText);

            bar.appendChild(awayDiv);
            bar.appendChild(homeDiv);
        }

        // Implement similar logic for Over/Under bets using overProb and underProb
        if (overProb && underProb) {
            bar.style.position = 'relative';
            var overWidth = parseFloat(overProb);
            var underWidth = parseFloat(underProb);

            // Create over (green) section
            var overDiv = document.createElement('div');
            overDiv.className = 'over';
            overDiv.style.width = `${overWidth}%`;
            overDiv.style.backgroundColor = 'green';
            overDiv.style.height = '100%';
            overDiv.style.position = 'absolute';
            overDiv.style.right = '0'; // Position from the right

            var overText = document.createElement('span');
            overText.className = 'probability-text';
            overText.style.position = 'absolute';
            overText.style.right = '5px'; // Ensure some padding
            overText.style.color = 'white';
            overText.style.fontSize = '11px';
            overText.textContent = `${overProb}%`;
            overDiv.appendChild(overText);

            // Create under (red) section
            var underDiv = document.createElement('div');
            underDiv.className = 'under';
            underDiv.style.width = `${underWidth}%`;
            underDiv.style.backgroundColor = 'red';
            underDiv.style.height = '100%';
            underDiv.style.position = 'absolute';
            underDiv.style.left = '0'; // Position from the left

            var underText = document.createElement('span');
            underText.className = 'probability-text';
            underText.style.position = 'absolute';
            underText.style.left = '5px'; // Ensure some padding
            underText.style.color = 'white';
            underText.style.fontSize = '11px';
            underText.textContent = `${underProb}%`;
            underDiv.appendChild(underText);

            bar.appendChild(underDiv);
            bar.appendChild(overDiv);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    updateProbabilityBars();
});


document.getElementById('myMessage').addEventListener('keypress', function(e) {
    if (e.which === 13 || e.keyCode === 13) {
        e.preventDefault();
        sendMessage();
    }
});

document.querySelector('button').addEventListener('click', sendMessage);

function startCountdown() {
    var countdownElement = document.getElementById('countdown');
    var remainingTime = 5; // 5 seconds countdown
    countdownElement.textContent = `Next message in ${remainingTime} seconds`;

    var countdownTimer = setInterval(function() {
        remainingTime -= 1;
        countdownElement.textContent = `Next message in ${remainingTime} seconds`;

        if (remainingTime <= 0) {
            clearInterval(countdownTimer);
            countdownElement.textContent = ''; // Hide the countdown
        }
    }, 1000);
}
