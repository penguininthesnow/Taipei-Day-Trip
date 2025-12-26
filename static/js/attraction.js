document.addEventListener("DOMContentLoaded", () => {
    const attractionId = window.location.pathname.split("/").pop();
    fetchAttraction(attractionId);
});

function fetchAttraction(attractionId) {
    fetch(`/api/attraction/${attractionId}`)
        .then(response => response.json())
        .then(result => {
            const attraction = result.data;

            document.getElementById("attraction-name").textContent = attraction.name;

            document.getElementById("attraction-info").textContent = `${attraction.category} at ${attraction.mrt}`;

            document.getElementById("attraction-description").textContent = attraction.description;

            const images = attraction.images;

            if (images && images.length> 0) {
                const imageElement = document.getElementById("attraction-image");
                imageElement.src = images[0];
            }
        })
        
        .catch(error => {
            console.error("Fetch error:", error);
        });

        // .then(data => {
        //     console.log("data:", data);
        // })
        
}