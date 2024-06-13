document.addEventListener("DOMContentLoaded", function() {
    const searchBox = document.getElementById('searchBox');
    const noResults = document.getElementById('noResults');

    function filterGames() {
        const term = searchBox.value.toLowerCase();
        const gameButtons = document.querySelectorAll('.btn.game-button');
        let visibleGames = 0;

        gameButtons.forEach(function(button) {
            const game = button.textContent.toLowerCase();
            const isLive = button.getAttribute('data-live') === 'True';
            const matchesTerm = game.includes(term);

            if (matchesTerm) {
                button.parentElement.style.display = '';
                visibleGames++;
                if (isLive && !button.innerHTML.includes('🔥')) {
                    button.innerHTML += ' 🔥'; // Add fire emoji for live games
                }
            } else {
                button.parentElement.style.display = 'none';
            }

            if (!isLive) {
                button.innerHTML = button.innerHTML.replace(' 🔥', ''); // Remove fire emoji if not live
            }
        });

        if (visibleGames === 0) {
            noResults.style.display = 'block'; // Show the no results message
        } else {
            noResults.style.display = 'none'; // Hide the no results message
        }
    }

    searchBox.addEventListener('keyup', filterGames);

    // Initialize to show all games
    filterGames();

    // Collapsible section for Later Games
    var coll = document.getElementsByClassName("collapsible");
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
            var arrow = this.querySelector('.arrow');
            if (this.classList.contains("active")) {
                arrow.innerHTML = "&#9650;"; // Unicode for up arrow
            } else {
                arrow.innerHTML = "&#9660;"; // Unicode for down arrow
            }
        });
    }
});
