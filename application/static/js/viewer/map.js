// Init the map
let map = L.map('map', {maxZoom: 14}).setView([46.603354, 1.888334], 6);
var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png').addTo(map);
// Elements
const footer = document.querySelector('footer');
const cooElement = footer.querySelector('.coo');
const zoomElement = footer.querySelector('.zomm');


// Create hexbin layer
var hexLayer = L.hexbinLayer({
  radiusRange: [1, 10],
  radius: 10,
  opacity: 1
}).addTo(map);






// Request data
async function requestData() {
    const response = await fetch('ajax/get_offers');
    const content = await response.json();

    const cleanPoints = content['offers'].filter(
        d => d.longitude != null && d.latitude != null
    );

    const maxCount = Math.max(1, d3.max(cleanPoints, d => d.count));

    const logColor = d3.scaleLog()
        .domain([1, maxCount])
        .range(['#f7fbff', '#08306b']);

    hexLayer
        .lng(d => d.longitude)
        .lat(d => d.latitude)
        .colorScale(logColor)
        .colorValue(bin => Math.max(1, bin.length)) // avoid log(0)
        .data(cleanPoints);
}


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
requestData();