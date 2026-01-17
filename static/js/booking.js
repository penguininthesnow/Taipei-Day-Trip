document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");

    // Tappay 初始化
    TPDirect.setupSDK(
        166513,
        "app_gmFxqwVoGjoT3njpM1FQofmTKmZhO5ncW1ypsy6PkaMG0fYApm6O6wIeSg6I",
        "sandbox"
    );

    // 設定信用卡欄位(card field)
    TPDirect.card.setup({
        fields: {
            number:{
                element: "#card-number",
                placeholder: "**** **** **** ****"
            },
            expirationDate: {
                element: "#card-exp-date",
                placeholder: "MM / YY"
            },
            ccv: {
                element: "#card-ccv",
                placeholder: "CCV"
            }
        },
        styles: {
            input: {
                color: "gray"
            },
            ".valid": {
                color: "green"
            },
            ".invalid": {
                color: "red"
            }
        }
    });

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
        document.getElementById("auth-phone").value;

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

// 付款
// ===== 確認訂購並付款 =====
const submitBtn = document.getElementById("booking_submit");

if (submitBtn) {
    submitBtn.addEventListener("click", () => {
        const token = localStorage.getItem("token");
        if (!token) {
            alert("請先登入");
            return;
        }

        const contactName = document.getElementById("auth-name").value;
        const contactEmail = document.getElementById("auth-email").value;
        const contactPhone = document.getElementById("auth-phone").value;

        if (!contactName || !contactEmail || !contactPhone) {
            alert("請填寫完整聯絡資訊!");
            return;
        }

        // 建立 TapPay 卡片資訊
        TPDirect.card.getPrime(async (result) => {
            if (result.status !==0) {
                alert("信用卡資訊有誤，請重新輸入");
                return;
            }

            const prime = result.card.prime;

            const orderData = {
                prime,
                order: {
                    price: booking.price,
                    trip: {
                        attraction: booking.attraction,
                        date: booking.date,
                        time: booking.time
                    },
                    contact: { 
                        name: contactName, 
                        email: contactEmail, 
                        phone: contactPhone 
                    }
                }
            };

            try {
                const res = await fetch("/api/orders", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`
                    },
                    body: JSON.stringify(orderData)
                });

                const data = await res.json();
                console.log("Order result:", data);

                if (data.data) {
                    // 付款成功 => 導向 thankyou.html
                    window.location.href = `/thankyou.html?number=${data.data.number}`
                } else {
                    // 付款失敗，留在 booking 頁
                    alert("付款失敗");
                }
            } catch (err) {
                console.error(err);
                alert("系統錯誤");
            }
        });
    });
}

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
