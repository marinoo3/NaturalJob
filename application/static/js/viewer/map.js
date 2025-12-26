// Init the map
let map = L.map('map', {maxZoom: 14}).setView([46.603354, 1.888334], 6);
var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                maxZoom: 20
            }).addTo(map);
// Elements
const footer = document.querySelector('footer');
const cooElement = footer.querySelector('.coo');
const zoomElement = footer.querySelector('.zomm');
// Hexbin
const palette = ['#A167F280', '#7e03a8', '#cc4778', '#f89540', '#f0f921']




// Add hexbin to map
var hexLayer = L.hexbinLayer({
  radiusRange: [1, 6],
  radius: 6,
  opacity: 1
}).addTo(map);


// Tooltip on hover
const tooltipHandler = L.HexbinHoverHandler.tooltip({
    tooltipContent: bin => {
        if (!bin || !bin.length) return 'No offer';

        // Titles
        const lines = bin
            .map(point => {
                const offer = point.o; // original data object you supplied
                return `<div style="color: var(--accent-color)">${offer.title}</div>`;
            })

        // Average salary (ignore offers without salary)
        const salaries = bin
            .map(point => point.o.salary_max)
            .filter(s => typeof s === 'number' && !Number.isNaN(s));

        if (salaries.length) {
            const avgSalary = salaries.reduce((sum, s) => sum + s, 0) / salaries.length;
            lines.push(`<div style="color: var(--accent-color); margin-top: 1rem;">Salaire moyen: €${avgSalary.toFixed(0)}</div>`);
        }

        return lines.join('');
    }
});

hexLayer.hoverHandler(tooltipHandler);

hexLayer.dispatch().on('click', bin => {
  const offers = bin.map(point => point.o); // original offer objects
  console.log('Clicked bin contains:', offers);
});





// Request data
async function requestData() {
    const response = await fetch('ajax/get_offers');
    const content = await response.json();

    const points = content['offers'].filter(
        d => d.longitude != null && d.latitude != null
    );

    // quantile color scale (≈20% of bins per color)    
    const counts = hexLayer
        .data()              // or recompute
        .map(bins => bins.length);
    const maxCount = d3.max(counts);
    const colorScale = d3.scaleLog()         // log compression
                        .domain([1, maxCount])
                        .range(palette);

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