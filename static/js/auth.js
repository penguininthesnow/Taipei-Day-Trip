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

// booking 預定按鈕設定
const bookingBtn = document.querySelector(".header__booking");


// ===== Modal 控制 =====
loginBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  openLoginModal();
});

// 關閉視窗鈕的設定 "X"
closeLogin?.addEventListener("click", closeAllModals);
closeAuth?.addEventListener("click", closeAllModals);

// 按遮罩可以關
loginModal?.addEventListener("click", closeAllModals); //
authModal?.addEventListener("click", closeAllModals);

function openLoginModal() {
  closeAllModals();
  loginModal?.classList.add("show"); // 按登入/註冊 時，先打開登入頁面
  authName.classList.add("hidden")
}

function openSignupModal() {
  closeAllModals();
  authModal?.classList.add("show");
  authName.classList.remove("hidden")
}

function closeAllModals() {
  loginModal?.classList.remove("show");
  authModal?.classList.remove("show");
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

  const email = loginEmail.value.trim();
  const password = loginPassword.value.trim();

  if (!email || !password) {
    loginMessage.textContent = "電子郵件或密碼錯誤";
    loginMessage.classList.add("error");
    return;
  }

  try {
    const res = await fetch("/api/user/auth", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

  // 只要不是成功，一律顯示錯誤
  if ( !res.ok || !data.token) {
    loginMessage.textContent = "電子郵件或密碼錯誤";
    loginMessage.classList.add("error");
    return;
  }
  // 登入成功
    localStorage.setItem("token", data.token);
    closeAllModals(); // 關 modal
    checkLoginStatus(); // 更新 headers

  } catch (err) {
    loginMessage.textContent = "電子郵件或密碼錯誤";
    loginMessage.className = "message error"; // 確保 class 加上
    loginMessage.classList.add("error");
    loginMessage.style.display = "block"; // 確保可見
  }
});

// ===== 註冊送出:成功顯示註冊成功; 重複顯示已有註冊過 =====
authSubmit?.addEventListener("click", async () => {
  authMessage.textContent = "";
  authMessage.className = "message";

  const name = authName.value.trim();
  const email = authEmail.value.trim();
  const password = authPassword.value.trim();

  // 前端檢查欄位
  if (!name || !email || !password) {
    authMessage.textContent = "請填寫所有欄位";
    authMessage.classList.add("error");
    return;
  }

  try {
    const res = await fetch("/api/user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });

    const data = await res.json();

    if (res.ok && data.ok) {
      authMessage.textContent = "註冊成功，請登入系統";
      authMessage.classList.add("success");
    } else {
      authMessage.textContent = data.message || "註冊失敗";
      authMessage.classList.add("error");
    }
  } catch (err) {
    authMessage.textContent = "註冊失敗";
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

// ===== 登入系統右上方顯示內容 =====
function showLoggedInUI() {
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
  // 按叉叉可以關
  document.querySelectorAll(".modal-content").forEach(el => {
    el.addEventListener("click", e => e.stopPropagation());
  });

  loginModal?.classList.add("hidden");
  authModal?.classList.add("hidden");

  closeAllModals();
  checkLoginStatus();

  // 按booking鈕，沒登入就出現modal
  const bookingBtn = document.querySelector(".header__booking");
  // const bookingBtn = document.querySelector(".booking-btn");

  if(bookingBtn) {
    bookingBtn.addEventListener("click", () => {
      const token = localStorage.getItem("token");

      if(!token) {
        // 未登入，跳modal
        document.getElementById("login-modal").classList.add("show");
      } else {
        // 已登入，登入 "/booking"
        window.location.href = "/booking";
      }
    });
  }

  const params = new URLSearchParams(window.location.search);
  // 如果是從"/booking" 被導回來的
  if (params.get("from") === "booking") {
    openLoginModal();
  }

});

console.log("header js loaded");
// document.addEventListener("DOMContentLoaded", () => {
//     const bookingBtn = document.querySelector(".header__booking");
//     console.log("bookingBtn =", bookingBtn);

//     if (!bookingBtn) {
//         console.error("❌ 找不到 .header__booking");
//         return;
//     }

//     bookingBtn.addEventListener("click", () => {
//         console.log("🔥 booking clicked");

//         const token = localStorage.getItem("token");

//         if (!token) {
//             document.getElementById("login-modal").classList.remove("hidden");
//         } else {
//             window.location.href = "/booking";
//         }
//     });
// });