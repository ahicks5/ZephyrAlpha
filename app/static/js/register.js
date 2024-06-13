document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const errorMessage = document.getElementById('errorMessage');

    form.addEventListener('submit', function(event) {
        let valid = true;
        let errorMessages = [];

        // Username validation
        const usernameRegex = /^[a-zA-Z0-9]{5,15}$/;
        if (!usernameRegex.test(username.value)) {
            valid = false;
            errorMessages.push("Username must be 5-15 characters long and contain only letters and numbers.");
        }

        // Password validation
        if (password.value !== confirmPassword.value) {
            valid = false;
            errorMessages.push("Passwords do not match.");
        }

        if (!valid) {
            event.preventDefault(); // Prevent form submission
            errorMessage.innerHTML = errorMessages.join("<br>"); // Show error messages
            errorMessage.style.display = 'block';
        } else {
            errorMessage.style.display = 'none'; // Hide error message
        }
    });
});
