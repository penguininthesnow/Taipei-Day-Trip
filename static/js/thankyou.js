document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("請先登入");
        window.location.href = "/";
        return;
    }
// =================== 檢查登入狀態 =============
    const authRes = await fetch("/api/user/auth", {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    if (!authRes.ok) {
        window.location.href = "/";
        return;
    }

    const authData = await authRes.json();

    if (!authData.data) {
        window.location.href = "/";
        return;
    }

    document.getElementById("login")?.classList.add("hidden");
    document.getElementById("logout-btn")?.classList.remove("hidden");

// =============== 取得訂單編號 ================
    const params = new URLSearchParams(window.location.search);
    const orderNumber = params.get("number");

    if (!orderNumber) {
        alert("訂單編號不存在");    
        return;
    }

    // 顯示訂單編號
    const orderNumberEl = document.getElementById("order-number");

    if (orderNumber && orderNumberEl) {
        orderNumberEl.textContent = orderNumber;
    }

    try {
        const orderRes = await fetch(`/api/order/${orderNumber}`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });


        if (!orderRes.ok) {
            console.error("訂單 API回傳錯誤:", orderRes.status);
            alert("訂單資料讀取錯誤失敗");
            return;
        }

        const result = await orderRes.json();

        if (!result.data) {
            alert("查無此訂單");
            return;
        }

        console.log("訂單資料: ", result.data);

    } catch (err) {
        console.error("取得訂單失敗", err);
        alert("系統錯誤，請稍後再試!");
    }
});    