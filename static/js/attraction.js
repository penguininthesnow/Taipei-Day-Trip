let images = [];
let currentIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
    const attractionId = window.location.pathname.split("/").pop();
    fetchAttraction(attractionId);
    const priceElement = document.getElementById("price");
    const timeRadios = document.querySelectorAll(`input[name="time"]`);

    // 加左右箭頭設定
    document.getElementById("arrow-left").addEventListener("click", () => {
        if (currentIndex === 0) {
            currentIndex = images.length - 1;
        } else {
            currentIndex--;
        }
        updateImage();
        updateIndicators(); // 點擊左右箭頭時下面分段線也會跟著一起動
    });

    document.getElementById("arrow-right").addEventListener("click", () => {
        if (currentIndex === images.length - 1) {
            currentIndex = 0;
        } else {
            currentIndex++;
        }
        updateImage();
        updateIndicators(); // 點擊左右箭頭時下面分段線也會跟著一起動
    });

    // 導覽價格設定
    timeRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.value === "morning") {
                priceElement.textContent = 2000;
            } else {
                priceElement.textContent = 2500;
            }
        });
    });
});

function fetchAttraction(attractionId) {
    fetch(`/api/attraction/${attractionId}`)
        .then(response => response.json())
        .then(result => {
            const attraction = result.data;

            document.getElementById("attraction-name").textContent = attraction.name;

            document.getElementById("attraction-info").textContent = `${attraction.category} at ${attraction.mrt}`;

            document.getElementById("attraction-description").textContent = attraction.description;

            document.getElementById("attraction-address").textContent = attraction.address;

            document.getElementById("attraction-transport").textContent = attraction.transport;

            images = attraction.images;
            // 動態indicator
            createIndicators();

            if (images && images.length> 0) {
                currentIndex = 0;
                updateImage();
                // const imageElement = document.getElementById("attraction-image");
                // imageElement.src = images[0];
            }
        })
        
        .catch(error => {
            console.error("Fetch error:", error);
        });

        // .then(data => {
        //     console.log("data:", data);
        // })
        
}

function updateImage() {
    const imageElement = document.getElementById("attraction-image");
    imageElement.src = images[currentIndex];
}

// 動態indicator設定
function createIndicators() {
    const indicatorsContainer = document.getElementById("indicators");
    indicatorsContainer.innerHTML = "";

    images.forEach((_, index) => {
        const line = document.createElement("span"); // 線段
        line.classList.add("indicator");

        if (index === currentIndex) {
            line.classList.add("active");
        }

        line.addEventListener("click", () => {
            currentIndex = index;
            updateImage();
            updateIndicators();
        });

        indicatorsContainer.appendChild(line);
    });
}   

// 同步更新 active 狀態
function updateIndicators() {
    const lines = document.querySelectorAll(".indicator");
    lines.forEach((line, index) => {
        if (index === currentIndex) {
            line.classList.add("active");
        } else {
            line.classList.remove("active");
        }
    });
}