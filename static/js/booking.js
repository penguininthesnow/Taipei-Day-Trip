document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    // 如果沒登入，要預訂，要請使用者先登入會員
    if (!token) {
        window.location.href = "/?from=booking";
        return;
    }

    try {
        // 檢查登入狀態(拿使用者姓名)
        const userRes = await fetch("/api/user/auth", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        const userData = await userRes.json();

        if(!userData.data) {
            window.location.href = "/?from=booking"; 
            return;       
        }

        // 顯示使用者名稱
        document.getElementById("user-name").textContent = userData.data.name;

        // 聯絡資訊 (input)
        document.getElementById("auth-name").value = userData.data.name;
        document.getElementById("auth-email").value = userData.data.email;

        // 取得 booking 資料
        const bookingRes = await fetch("/api/booking", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });
        
        const bookingData = await bookingRes.json();
        const noBookingEl = document.getElementById("no-booking");
        const bookingInfoEl = document.getElementById("booking-info");

        // 沒有任何行程
        if (!bookingData.data) {
            noBookingEl.classList.remove("hidden");
            bookingInfoEl.classList.add("hidden");
            hideBookingFormSections();
            return;
        }

        // 有 booking
        showBookingFormSections();

        // render booking === 預約確認區塊
        const booking = bookingData.data;

        document.getElementById("booking-image").src = booking.attraction.image;
        document.getElementById("booking-name").textContent = booking.attraction.name;
        document.getElementById("booking-date").textContent = booking.date;
        document.getElementById("booking-time").textContent = booking.time === "morning" ? "早上 9 點到 12 點": "下午 2 點到 5 點";
        document.getElementById("booking-price").textContent = booking.price;
        document.getElementById("booking-address").textContent = booking.attraction.address;

        
        // 付款資訊區塊

        // 總金額區塊
        document.getElementById("price").textContent = booking.price

        noBookingEl.classList.add("hidden");
        bookingInfoEl.classList.remove("hidden");

        // 刪除booking
        const deleteBtn = document.getElementById("delete-booking");

        deleteBtn.addEventListener("click", async () => {
            const res = await fetch("/api/booking", {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const result = await res.json();
            if (result.ok) {
                // 刪除成功，就可以重新載入頁面
                window.location.reload();
            }
            // if (result.ok) {
            //     bookingInfoEl.classList.add("hidden");
            //     noBookingEl.classList.remove("hidden");
            //     document.getElementById("price").textContent = "0";
            // }
        });
    } catch (err) {
        console.error("Booking page error:", err);
        // window.location.href = "/";
    }
});


function hideBookingFormSections() {
    document.querySelectorAll(".booking-divider").forEach(hr => hr.classList.add("hidden"));
    document.querySelector(".booking_contact")?.classList.add("hidden");
    document.querySelector(".booking_payment")?.classList.add("hidden");
    document.querySelector(".booking_finalcheck")?.classList.add("hidden");
}

function showBookingFormSections() {
    document.querySelectorAll(".booking-divider").forEach(hr => hr.classList.remove("hidden"));
    document.querySelector(".booking_contact")?.classList.remove("hidden");
    document.querySelector(".booking_payment")?.classList.remove("hidden");
    document.querySelector(".booking_finalcheck")?.classList.remove("hidden");
}