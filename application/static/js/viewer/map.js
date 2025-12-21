// Init the map
let map = L.map('map', {maxZoom: 14}).setView([46.603354, 1.888334], 6);
var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png').addTo(map);
// Elements
const footer = document.querySelector('footer');
const cooElement = footer.querySelector('.coo');
const zoomElement = footer.querySelector('.zomm');
// Hexbin
const palette = ['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'];




// Add hexbin to map
var hexLayer = L.hexbinLayer({
  radiusRange: [1, 6],
  radius: 6,
  opacity: 1
}).addTo(map);






// Request data
async function requestData() {
    const response = await fetch('ajax/get_offers');
    const content = await response.json();

    const points = content['offers'].filter(
        d => d.longitude != null && d.latitude != null
    );

    // quantile color scale (≈20% of bins per color)
    const colorScale = d3.scaleQuantile().range(palette);

    // bind log transforms when needed
    const binders = {
    count: bins => bins.length,
    weight: bins => bins.reduce((sum, { data }) => sum + (data.weight ?? 0), 0)
    };
    const logWrapper = fn => bins => {
    const value = fn(bins);
    return value > 0 ? Math.log(value) : 0;
    };
    const colorBinding = logWrapper(binders.count);   // log(count)

    hexLayer
        .lng(d => d.longitude)
        .lat(d => d.latitude)
        .colorValue(colorBinding)
        .colorScale(colorScale)
        .data(points)
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