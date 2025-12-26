let images = [];
let currentIndex = 0;

document.addEventListener("DOMContentLoaded", () => {
    const attractionId = window.location.pathname.split("/").pop();
    fetchAttraction(attractionId);

    // 加左右箭頭設定
    document.getElementById("arrow-left").addEventListener("click", () => {
        if (currentIndex === 0) {
            currentIndex = images.length - 1;
        } else {
            currentIndex--;
        }
        updateImage();
    });

    document.getElementById("arrow-right").addEventListener("click", () => {
        if (currentIndex === images.length - 1) {
            currentIndex = 0;
        } else {
            currentIndex++;
        }
        updateImage();
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

            images = attraction.images;

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
