let pickupMarker = null;
let deliveryMarker = null;
let routeLine = null;


const map = L.map('map')
.setView(
[39.8283,-98.5795],
4
);


L.tileLayer(
'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
)
.addTo(map);