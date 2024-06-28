document.addEventListener("DOMContentLoaded", function() {
    const navLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-content');

    function handleTabClick(link) {
        navLinks.forEach(function(navLink) {
            navLink.classList.remove('active');
        });
        link.classList.add('active');

        const target = link.getAttribute('data-target');
        tabContents.forEach(function(content) {
            if (content.id === target) {
                content.style.display = 'block';
            } else {
                content.style.display = 'none';
            }
        });
    }

    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            handleTabClick(link);
        });
    });

    // Automatically click the "Favorites" tab if it exists and user is authenticated
    const favoriteTab = document.querySelector('.nav-link[data-target="favorites"]');
    if (favoriteTab) {
        handleTabClick(favoriteTab);
    } else {
        // Default to "Today" tab
        const homeTab = document.querySelector('.nav-link[data-target="home"]');
        if (homeTab) {
            handleTabClick(homeTab);
        }
    }

    // Collapsible section for Later Games
    const collapsibleElements = document.querySelectorAll(".collapsible");
    collapsibleElements.forEach(function(element) {
        element.addEventListener("click", function() {
            this.classList.toggle("active");
            const content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
            const arrow = this.querySelector('.arrow');
            if (this.classList.contains("active")) {
                arrow.innerHTML = "&#9650;"; // Unicode for up arrow
            } else {
                arrow.innerHTML = "&#9660;"; // Unicode for down arrow
            }
        });
    });
});
