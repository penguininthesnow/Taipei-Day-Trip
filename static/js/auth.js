// ===== DOM =====
const loginModal = document.getElementById("login-modal");
const authModal = document.getElementById("auth-modal");

// header
const loginBtn = document.getElementById("login");
const logoutBtn = document.getElementById("logout-btn");
const userNameSpan = document.getElementById("user-name");

// login modal
const closeLogin = document.getElementById("close-login");
const loginEmail = document.getElementById("login-email");
const loginPassword = document.getElementById("login-password");
const loginSubmit = document.getElementById("login-submit");
const toSignup = document.getElementById("to-signup");

// signup modal
const closeAuth = document.getElementById("close-auth");
const authName = document.getElementById("auth-name");
const authEmail = document.getElementById("auth-email");
const authPassword = document.getElementById("auth-password");
const authSubmit = document.getElementById("auth-submit");
const toLogin = document.getElementById("switch-to-login");
const authMessage = document.getElementById("auth-message");
const loginMessage = document.getElementById("login-message");


// ===== Modal 控制 =====
loginBtn?.addEventListener("click", () => {
  openLoginModal();
});

// 關閉視窗鈕的設定 "X"
closeLogin?.addEventListener("click", closeAllModals);
closeAuth?.addEventListener("click", closeAllModals);
// 按叉叉可以關
document.querySelectorAll(".modal-content").forEach(el => {
  el.addEventListener("click", e => e.stopPropagation());
});
// 按遮罩可以關
loginModal.addEventListener("click", closeAllModals);
authModal.addEventListener("click", closeAllModals);

function openLoginModal() {
  closeAllModals();
  loginModal.classList.remove("hidden"); // 按登入/註冊 時，先打開登入頁面
  authName.classList.add("hidden")
}

function openSignupModal() {
  closeAllModals();
  authModal.classList.remove("hidden");
  authName.classList.remove("hidden")
}

function closeAllModals() {
  loginModal?.classList.add("hidden");
  authModal?.classList.add("hidden");
}

// ===== modal 之間切換 =====
toSignup?.addEventListener("click", () => {
  openSignupModal();
});

toLogin?.addEventListener("click", () => {
  openLoginModal();
});

// ===== 登入 =====
loginSubmit?.addEventListener("click", async () => {
  loginMessage.textContent = "";
  loginMessage.className = "message";

  const email = loginEmail.value;
  const password = loginPassword.value;

  const res = await fetch("/api/user/auth", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (data.token) {
    localStorage.setItem("token", data.token);

    closeAllModals(); // 關 modal
    checkLoginStatus(); // 更新 headers
  } else {
    loginMessage.textContent = data.message || "電子郵件或密碼錯誤";
    loginMessage.classList.add("error");
  }
});

// ===== 註冊送出:成功顯示註冊成功; 重複顯示已有註冊過 =====
authSubmit.addEventListener("click", async () => {
  authMessage.textContent = "";
  authMessage.className = "message";

  const name = authName.value;
  const email = authEmail.value;
  const password = authPassword.value;

  const res = await fetch("/api/user", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password })
  });

  const data = await res.json();

  if (data.ok) {
    authMessage.textContent = "註冊成功，請登入系統";
    authMessage.classList.add("success");
  } else {
    authMessage.textContent = data.message || "註冊失敗";
    authMessage.classList.add("error");
  }
});

// ===== 登入狀態 =====
function checkLoginStatus() {
  const token = localStorage.getItem("token");

  if (!token) {
    showLoggedOutUI();
    return;
  }

  fetch("/api/user/auth", {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  })
  .then(res => res.json())
  .then(data => {
    if (data.data) {
      showLoggedInUI(data.data);
    } else {
      localStorage.removeItem("token");
      showLoggedOutUI();
    }
  });
}

/* 登入系統右上方顯示內容 */
function showLoggedInUI(user) {
  userNameSpan.textContent = user.name;
  loginBtn.style.display = "none";
  logoutBtn.style.display = "block";
}

function showLoggedOutUI() {
  loginBtn.style.display = "block";
  logoutBtn.style.display = "none";
}

// ===== 登出 =====
logoutBtn?.addEventListener("click", () => {
  localStorage.removeItem("token");
  showLoggedOutUI();
});

// ===== 初始化檢查登入狀態 =====
document.addEventListener("DOMContentLoaded", () => {
  closeAllModals();
  checkLoginStatus();
});
