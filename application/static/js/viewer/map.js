// Init the map
let map = L.map('map', {maxZoom: 14}).setView([46.603354, 1.888334], 6);
var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png').addTo(map);
// Elements
const footer = document.querySelector('footer');
const cooElement = footer.querySelector('.coo');
const zoomElement = footer.querySelector('.zomm');


// Set footer values

function setZoom() {
    zoomElement.textContent = 'Zoom : ' + map.getZoom();
}

function setCoo() {
    cooElement.textContent = map.getCenter().lat.toFixed(4) + ' ; ' + map.getCenter().lng.toFixed(4);
}

// Map listeners

map.on('move', function () {
    setCoo();
});

map.on('zoomend', function () {
    setZoom();
});


// Init

setZoom();
setCoo();