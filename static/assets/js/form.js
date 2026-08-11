// Markers
let fromMarker = null;
let toMarker = null;

// Route Line
let routeLine = null;

// Create Map

const map = L.map('map').setView([39.8283,-98.5795],4);

// Map Tiles

L.tileLayer(
    'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
        attribution: '&copy; OpenStreetMap contributors'
    }
).addTo(map);


// Show Custom Date

// const pickup =
// document.getElementById("pickupOption");

// const custom =
// document.getElementById("customDateDiv");

// pickup.addEventListener("change",()=>{

//     if(pickup.value==="Custom Date"){

//         custom.classList.remove("d-none");

//     }else{

//         custom.classList.add("d-none");

//     }

// });


let cities = [];

let fromLocation = null;
let toLocation = null;

async function loadCities() {

    const response = await fetch("/static/assets/data/us-cities.json");

    cities = await response.json();

    initializeAutocomplete();

}

loadCities();
function initializeAutocomplete() {

    const options = cities.map(city => ({

        value: city.city + ", " + city.state,

        text: city.city + ", " + city.state,

        lat: city.lat,

        lng: city.lng

    }));


    const from = new TomSelect("#fromCity", {

        options: options,
        valueField: "value",
        labelField: "text",
        searchField: "text",
    
        maxItems: 1,      // Only one city
        create: false,
        persist: false,

        onChange(value) {

            fromLocation = options.find(o => o.value === value);

            console.log("FROM:", fromLocation);
            updateMap();

        }

    });


    const to = new TomSelect("#toCity", {

        options: options,
        valueField: "value",
        labelField: "text",
        searchField: "text",
    
        maxItems: 1,
        create: false,
        persist: false,

        onChange(value) {

            toLocation = options.find(o => o.value === value);

            console.log("TO:", toLocation);
            updateMap();

        }

    });

}
function updateMap() {

    // Don't do anything until both cities are selected
    if (!fromLocation || !toLocation) return;

    // Remove old markers
    if (fromMarker) {
        map.removeLayer(fromMarker);
    }

    if (toMarker) {
        map.removeLayer(toMarker);
    }

    // Remove old route
    if (routeLine) {
        map.removeLayer(routeLine);
    }

    // Pickup marker
    fromMarker = L.marker([
        fromLocation.lat,
        fromLocation.lng
    ]).addTo(map);

    fromMarker.bindPopup(
        "<strong>Pickup</strong><br>" + fromLocation.text
    );

    // Delivery marker
    toMarker = L.marker([
        toLocation.lat,
        toLocation.lng
    ]).addTo(map);

    toMarker.bindPopup(
        "<strong>Delivery</strong><br>" + toLocation.text
    );

    // Draw line
    routeLine = L.polyline([
        [fromLocation.lat, fromLocation.lng],
        [toLocation.lat, toLocation.lng]
    ], {
        color: "#0d6efd",
        weight: 4
    }).addTo(map);

    // Auto Zoom
    map.fitBounds(routeLine.getBounds(), {
        padding: [50, 50]
    });

    calculateDistance();
}
function calculateDistance() {

    const from = turf.point([
        fromLocation.lng,
        fromLocation.lat
    ]);

    const to = turf.point([
        toLocation.lng,
        toLocation.lat
    ]);

    const distance = turf.distance(from, to, {
        units: "miles"
    });

    document.getElementById("distance").innerHTML =
        "Distance: " + distance.toFixed(0) + " Miles";

    document.getElementById("distance_value").value = distance;
}


const pickupOption = document.getElementById("pickupOption");
const customDateContainer = document.getElementById("customDateContainer");
const customDate = document.getElementById("customDate");

pickupOption.addEventListener("change", function () {

    if (this.value === "Custom Date") {

        customDateContainer.style.display = "block";
        customDate.required = true;

    } else {

        customDateContainer.style.display = "none";
        customDate.required = false;
        customDate.value = "";

    }

});

document.addEventListener("DOMContentLoaded", function () {

    

});