document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("請先登入");
        window.location.href = "/";
        return;
    }

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
        const res = await fetch(`/api/order/${orderNumber}`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const result = await res.json();

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