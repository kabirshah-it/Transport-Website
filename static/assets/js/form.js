// Markers
let fromMarker = null;
let toMarker = null;

// Route Line
let routeLine = null;

// Create Map

const map = L.map('map').setView([39.8283,-98.5795],4);

// Map Tiles

const GEOAPIFY_API_KEY = '0e8a10c7d7d64ab5a4e972eacaf4df5d';

L.tileLayer(
    `https://maps.geoapify.com/v1/tile/osm-carto/{z}/{x}/{y}.png?apiKey=${GEOAPIFY_API_KEY}`,
    {
        maxZoom: 20,
        attribution:
            'Powered by <a href="https://www.geoapify.com/" target="_blank">Geoapify</a> | ' +
            '<a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap contributors</a>'
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


let fromLocation = null;
let toLocation = null;

async function loadCities() {

    try {

        const response = await fetch(
            "/static/assets/data/usa_locations_optimized.json"
        );

        if (!response.ok) {
            throw new Error("Failed to load location data.");
        }

        const data = await response.json();

        const options = Object.entries(data).map(([zip, location]) => ({
            value: zip,
            text: location.city + ", " + location.state + " " + zip,
            city: location.city,
            state: location.state,
            zip: zip,
            lat: location.lat,
            lng: location.lng
        }));

        console.log("Locations loaded:", options.length);
        console.log("First location:", options[0]);

        initializeAutocomplete(options);

    } catch (error) {

        console.error("Location data error:", error);

    }

}

loadCities();


function initializeAutocomplete(options) {


    const from = new TomSelect("#fromCity", {

        options: options,
        valueField: "value",
        labelField: "text",
        searchField: "text",
        score: function(search) {
            const query = search.toLowerCase();
        
            return function(item) {
                const text = item.text.toLowerCase();
        
                if (text.startsWith(query)) {
                    return 1;
                }
        
                if (text.includes(query)) {
                    return 0.5;
                }
        
                return 0;
            };
        },
    
        maxItems: 1,      // Only one city
        create: false,
        persist: false,
        maxOptions: 50,

        onChange(value) {

            fromLocation = options.find(o => o.value === value);
        
            if (fromLocation) {
                document.getElementById("pickup_city").value =
                    fromLocation.city + ", " +
                    fromLocation.state + " " +
                    fromLocation.zip;
            }
        
            console.log("FROM:", fromLocation);
            console.log("Pickup submitted value:",
                document.getElementById("pickup_city").value);
        
            updateMap();
        
        }

    });


    const to = new TomSelect("#toCity", {

        options: options,
        valueField: "value",
        labelField: "text",
        searchField: "text",
        score: function(search) {
            const query = search.toLowerCase();
        
            return function(item) {
                const text = item.text.toLowerCase();
        
                if (text.startsWith(query)) {
                    return 1;
                }
        
                if (text.includes(query)) {
                    return 0.5;
                }
        
                return 0;
            };
        },
    
        maxItems: 1,
        create: false,
        persist: false,
        maxOptions: 50,

        onChange(value) {

            toLocation = options.find(o => o.value === value);
        
            if (toLocation) {
                document.getElementById("delivery_city").value =
                    toLocation.city + ", " +
                    toLocation.state + " " +
                    toLocation.zip;
            }
        
            console.log("TO:", toLocation);
            console.log("Delivery submitted value:",
                document.getElementById("delivery_city").value);
        
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

document.addEventListener("DOMContentLoaded", function () {

    const pickupOption = document.getElementById("pickupOption");
    const customDateContainer = document.getElementById("customDateContainer");
    const customDate = document.getElementById("customDate");

    if (pickupOption && customDateContainer && customDate) {

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

    }

});