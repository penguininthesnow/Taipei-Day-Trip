document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const orderNumber = params.get("number");

    // document.getElementById("order-number").textContent = orderNumber;

    const orderNumberEl = document.getElementById("order-number");

    if (orderNumber && orderNumberEl) {
        orderNumberEl.textContent = orderNumber;
    }
    // if (!orderNumber) return;

    // const el = document.getElementById("order-number");
    // if (el) {
    //     el.textContent = orderNumber;
    // }

});    