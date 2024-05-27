document.addEventListener("DOMContentLoaded", function() {
    const searchBox = document.getElementById('searchBox');
    const noResults = document.getElementById('noResults');

    searchBox.addEventListener('keyup', function(e) {
        const term = e.target.value.toLowerCase();
        const gameButtons = document.querySelectorAll('.btn.game-button');
        let visibleGames = 0;

        gameButtons.forEach(function(button) {
            const game = button.textContent.toLowerCase();
            if (game.includes(term)) {
                button.parentElement.style.display = '';
                visibleGames++;
            } else {
                button.parentElement.style.display = 'none';
            }
        });

        if (visibleGames === 0) {
            noResults.style.display = 'block'; // Show the no results message
        } else {
            noResults.style.display = 'none'; // Hide the no results message
        }
    });
});
