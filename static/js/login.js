function login(){
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const errorMsg = document.getElementById('error-msg');

    // Simple validation
    if(username === "" || password === ""){
        errorMsg.style.color = "red";
        errorMsg.textContent = "Please enter both username and password!";
        return;
    }

    // Dummy login check
    if(username === "admin" && password === "admin123"){
        errorMsg.style.color = "green";
        errorMsg.textContent = "Login successful! Redirecting...";
        setTimeout(() => {
            window.location.href = "dashboard.html"; // redirect to dashboard
        }, 1000);
    } else {
        errorMsg.style.color = "red";
        errorMsg.textContent = "Invalid username or password!";
    }
}
