// Function to update the join confirmation visibility
//function updateJoinConfirmation(isVisible) {
//    document.getElementById('joinConfirmation').style.display = isVisible ? 'block' : 'none';
//}

// Function to add a message to the message list
function addMessageToList(message) {
    const messagesList = document.getElementById('messages');
    const li = document.createElement('li');
    li.textContent = message;
    messagesList.appendChild(li);

    // Keep the message list to a maximum of 100 messages
    while (messagesList.children.length > 100) {
        messagesList.removeChild(messagesList.firstChild);
    }

    autoScroll();
}

// Function to clear the message input field
function clearInput() {
    document.getElementById("myMessage").value = '';
}

// Function to automatically scroll the messages list to the bottom
function autoScroll() {
    const messagesList = document.getElementById('messages');
    messagesList.scrollTop = messagesList.scrollHeight;
}

// Function to setup UI event listeners
function setupUIEventListeners(sendMessageCallback) {
    // Listener for the message input keypress (Enter key)
    document.getElementById('myMessage').addEventListener('keypress', function(e) {
        if (e.which === 13 || e.keyCode === 13) {
            e.preventDefault();
            sendMessageCallback(this.value);
        }
    });

    // Listener for the send button click
    document.querySelector('button').addEventListener('click', () => {
        const input = document.getElementById("myMessage");
        sendMessageCallback(input.value);
    });

    // Call to update probability bars on load
    updateProbabilityBars();
}

function updateProbabilityBars() {
    var bars = document.querySelectorAll('.probability-bar');
    bars.forEach(function(bar) {
        var homeProb = parseFloat(bar.getAttribute('data-home-prob'));
        var awayProb = parseFloat(bar.getAttribute('data-away-prob'));
        var juice = bar.hasAttribute('data-juice') ? parseFloat(bar.getAttribute('data-juice')) : null;

        bar.innerHTML = ''; // Clear previous content

        if (juice !== null) {
            // Handle the juice-adjusted bar
            console.log('Creating juice-adjusted bar for', bar.id); // Debugging
            createJuiceAdjustedBar(bar, homeProb, awayProb, juice);
        } else {
            // Handle the standard bar
            console.log('Creating standard bar for', bar.id); // Debugging
            createStandardBar(bar, homeProb, awayProb);
        }
    });
}


function createStandardBar(bar, homeProb, awayProb) {
    // Creates the standard bar without considering juice
    var totalWidth = 100; // Total width for the bar
    var homeWidth = (homeProb / (homeProb + awayProb)) * totalWidth;
    var awayWidth = (awayProb / (homeProb + awayProb)) * totalWidth;

    // Create away (red) section
    var awayDiv = createProbabilitySection('away', awayWidth, 'red', `${Math.round(awayProb)}%`);

    // Create home (green) section
    var homeDiv = createProbabilitySection('home', homeWidth, 'green', `${Math.round(homeProb)}%`);
    homeDiv.style.left = `${awayWidth}%`; // Position the home section next to the away section

    // Append sections to the bar
    bar.appendChild(awayDiv);
    bar.appendChild(homeDiv);
}

function createJuiceAdjustedBar(bar, homeProb, awayProb, juice) {
    var totalProb = homeProb + awayProb;
    var effectiveTotalWidth = 100 - juice;
    var homeWidthPercentage = (homeProb / totalProb) * effectiveTotalWidth;
    var awayWidthPercentage = (awayProb / totalProb) * effectiveTotalWidth;

    var awayDiv = createProbabilitySection('away', awayWidthPercentage, 'red', `${Math.round(awayProb)}%`);
    awayDiv.style.left = `0%`;

    // Adjusted to ensure juice percentage is rounded
    var juiceDiv = createProbabilitySection('juice', juice, '#E67E22', `${Math.round(juice)}%`);
    juiceDiv.style.left = `${awayWidthPercentage}%`;

    var homeDiv = createProbabilitySection('home', homeWidthPercentage, 'green', `${Math.round(homeProb)}%`);
    homeDiv.style.left = `${awayWidthPercentage + juice}%`;

    bar.appendChild(awayDiv);
    bar.appendChild(juiceDiv);
    bar.appendChild(homeDiv);
}

function createProbabilitySection(className, width, backgroundColor, textContent) {
    var div = document.createElement('div');
    div.className = className;
    div.style.width = `${width}%`;
    div.style.backgroundColor = backgroundColor;
    div.style.height = '100%';
    div.style.position = 'absolute';

    var text = document.createElement('span');
    text.style.position = 'absolute';
    text.style.color = 'white';
    text.style.fontSize = '12px';
    text.textContent = textContent;

    // Additional styles for vertical centering
    text.style.top = '50%'; // Position at 50% of the parent's height
    text.style.transform = 'translateY(-50%)'; // Move up by half of its own height

    // Adjusting z-index for juice text to ensure visibility
    if (className === 'juice') {
        text.style.left = '3px';
        text.style.zIndex = '2'; // Ensure juice text appears over the home section if overlapping
        text.title = "Bookie juice refers to the commission bookmakers take on bets."; // Tooltip text
    } else if (className === 'home') {
        text.style.right = '3px';
        text.style.zIndex = '1'; // Default layering for home, under juice text
    } else { // "away" class
        text.style.left = '3px';
        text.style.zIndex = '1'; // Default layering for away
    }

    div.appendChild(text);

    return div;
}

function updateBetStatus() {
    console.log('Updating bet status...');

    // Correctly targeting the away team's score
    const awayScoreElement = document.querySelector('.live-score-container .score-cell:first-child .team-score');

    // Correctly targeting the home team's score
    const homeScoreElement = document.querySelector('.live-score-container .score-cell:last-child .team-score');

    console.log('awayScoreElement:', awayScoreElement);
    console.log('homeScoreElement:', homeScoreElement);

    // Check if score elements were found
    if (!awayScoreElement || !homeScoreElement) {
        console.error('Score elements not found');
        return;
    }

    const awayScore = parseInt(awayScoreElement.innerText);
    const homeScore = parseInt(homeScoreElement.innerText);

    console.log(`Parsed scores - Away: ${awayScore}, Home: ${homeScore}`);

    // Assuming you have elements with class 'moneyline-odds' for both teams
    const awayMoneylineElement = document.querySelector('.away-odds');
    const homeMoneylineElement = document.querySelector('.home-odds');

    console.log('awayMoneylineElement:', awayMoneylineElement);
    console.log('homeMoneylineElement:', homeMoneylineElement);

    // Update Moneyline status based on the current leading team
    if (awayScore > homeScore) {
        // Highlight the away team as winning
        awayMoneylineElement.style.color = 'green';
        awayMoneylineElement.style.fontWeight = 'bold';
        console.log('Highlighting away team as winning');
        // Ensure the home element is not highlighted
        homeMoneylineElement.style.color = ''; // Reset to default
        homeMoneylineElement.style.fontWeight = ''; // Reset to default
    } else if (homeScore > awayScore) {
        // Highlight the home team as winning
        homeMoneylineElement.style.color = 'green';
        homeMoneylineElement.style.fontWeight = 'bold';
        console.log('Highlighting home team as winning');
        // Ensure the away element is not highlighted
        awayMoneylineElement.style.color = ''; // Reset to default
        awayMoneylineElement.style.fontWeight = ''; // Reset to default
    } else {
        // In case of a tie, ensure no team is highlighted
        awayMoneylineElement.style.color = ''; // Reset to default
        homeMoneylineElement.style.fontWeight = ''; // Reset to default
        console.log('No team is highlighted, it\'s a tie');
    }

    // Update the spread bets status
    document.querySelectorAll('.away-spread, .home-spread').forEach((element, index) => {
        console.log(`Evaluating spread bet for element ${index}`, element);

        const betType = element.classList.contains('away-spread') ? 'away' : 'home';
        const spreadText = element.innerText;
        const spreadValue = parseFloat(spreadText.match(/-?\d+(\.\d+)?/)[0]);

        console.log(`Spread bet details - Element ${index}: Type: ${betType}, Value: ${spreadValue}`);

        let conditionMet = false;

        if (betType === 'away') {
            const adjustedAwayScore = awayScore + spreadValue;
            conditionMet = adjustedAwayScore > homeScore;
        } else { // 'home'
            const adjustedHomeScore = homeScore + spreadValue;
            conditionMet = adjustedHomeScore > awayScore;
        }

        console.log(`Condition for element ${index} - Type: ${betType}, Met: ${conditionMet}`);

        if (conditionMet) {
            element.style.color = 'green';
            element.style.fontWeight = 'bold';
        } else {
            element.style.color = ''; // Reset to default
            element.style.fontWeight = ''; // Reset to default
        }
    });

    // Update the over/under bets status
    document.querySelectorAll('.under-odds, .over-odds').forEach((element, index) => {
        console.log(`Evaluating over/under bet for element ${index}`, element);

        const totalPoints = awayScore + homeScore;
        const betText = element.innerText;
        const betValue = parseFloat(betText.match(/-?\d+(\.\d+)?/)[0]);
        let conditionMet = false;

        console.log(`Over/under bet details - Element ${index}: Total points: ${totalPoints}, Bet value: ${betValue}`);

        if (element.classList.contains('under-odds')) {
            conditionMet = totalPoints < betValue;
        } else { // 'over-odds'
            conditionMet = totalPoints > betValue;
        }

        console.log(`Condition for element ${index} - Type: ${element.classList.contains('under-odds') ? 'under' : 'over'}, Met: ${conditionMet}`);

        if (conditionMet) {
            element.style.color = 'green';
            element.style.fontWeight = 'bold';
        } else {
            element.style.color = ''; // Reset to default
            element.style.fontWeight = ''; // Reset to default
        }
    });
}



// Document ready function to initialize everything
document.addEventListener('DOMContentLoaded', () => {
    // Assuming sendMessage is defined and passed from socketEvents.js or similar
    setupUIEventListeners(sendMessage);
    console.log('DOM fully loaded and parsed');
    updateBetStatus();
});


