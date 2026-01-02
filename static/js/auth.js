// 登入 modal畫面串接 (點登入視窗彈出)
const loginBtn = document.getElementById("login-btn");
const loginModal = document.getElementById("login-modal");
const closeLogin = document.getElementById("close-login");

loginBtn.addEventListener("click", () => {
    loginModal.classList.remove("hidden");
});

closeLogin.addEventListener("click", () => {
    loginModal.classList.add("hidden");
});

// 登入API串接
document.getElementById("login-submit").addEventListener("click", () => {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    fetch("/api/user/auth", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
        if(data.token) {
            // 登入成功
            localStorage.setItem("token", data.token);
            loginModal.classList.add("hidden");
            checkLoginStatus();
        } else {
            alert(data.message);
        }
    });
});

// 頁面載入時鑒察登入狀態
document.addEventListener("DOMContentLoaded", () => {
    checkLoginStatus();
});