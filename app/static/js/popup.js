document.addEventListener("DOMContentLoaded", function() {
    // Show the pop-up after a delay
    setTimeout(showPopup, 2000); // 2 seconds delay

    function showPopup() {
        const popup = document.getElementById('signupPopup');
        popup.style.display = 'block';
        setTimeout(() => popup.classList.add('show'), 10); // Delay adding the show class for transition
    }

    window.closePopup = function() {
        const popup = document.getElementById('signupPopup');
        popup.classList.remove('show');
        setTimeout(() => popup.style.display = 'none', 500); // Wait for transition to finish before hiding
    };
});
