function register() {
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    const confirmPassword = document.getElementById('confirm-password').value.trim();
    const errorMsg = document.getElementById('error-msg');

    // Basic validation
    if(username === "" || email === "" || password === "" || confirmPassword === ""){
        errorMsg.style.color = "red";
        errorMsg.textContent = "Please fill in all fields!";
        return;
    }

    if(password !== confirmPassword){
        errorMsg.style.color = "red";
        errorMsg.textContent = "Passwords do not match!";
        return;
    }

    // Dummy success
    errorMsg.style.color = "green";
    errorMsg.textContent = "Registration successful! Redirecting to login...";
    setTimeout(() => {
        window.location.href = "login.html";
    }, 1200);
}
