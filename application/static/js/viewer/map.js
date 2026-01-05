import { saveOffer, unsaveOffer, savedOffers } from '../_helpers/offer_manager.js';

// Init the map
let map = L.map('map', {maxZoom: 14}).setView([46.603354, 1.888334], 6);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {maxZoom: 20}).addTo(map);
// Elements
const section = document.querySelector('#viewer');
const mapContainer = section.querySelector('#map');
const footer = section.querySelector('footer');
const cooElement = footer.querySelector('.coo');
const zoomElement = footer.querySelector('.zomm');
const searchInput = section.querySelector('#search-input');
const resultsContainer = section.querySelector('.search-container ul.offers');
const countText = section.querySelector('.search-container .footer .count');
const lottieContainer = section.querySelector('#lottie-container');
// Hexbin palette
const palette = ['#A167F280', '#7e03a8', '#cc4778', '#f89540', '#f0f921']





// Move controls to bottom right
map.zoomControl.setPosition('bottomright');

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
            .map(point => point.o.salary_min)
            .filter(s => typeof s === 'number' && !Number.isNaN(s));

        if (salaries.length) {
            const avgSalary = salaries.reduce((sum, s) => sum + s, 0) / salaries.length;
            lines.push(`<div style="color: var(--accent-color); margin-top: 1rem;">Salaire moyen: €${avgSalary.toFixed(0)}</div>`);
        }

        return lines.join('');
    }
});





// Create animation
const loadingAnimation = lottie.loadAnimation({
    container: lottieContainer,
    renderer: 'svg', // or 'canvas', 'html'
    loop: true,
    autoplay: false,
    path: lottieContainer.dataset.url
});





function renderResults(results) {
    results.forEach(html => {
        const li = document.createElement('li');
        li.innerHTML = html;
        const offer = li.querySelector('.offer');
        const offerId = offer.dataset.offerId;
        if (savedOffers.includes(offerId)) {
            offer.classList.add('saved');
        }
        li.querySelector('button.save').addEventListener('click', () => {
            if (!savedOffers.includes(offerId)) {
                offer.classList.add('saved');
                saveOffer(offerId);
            } else {
                offer.classList.remove('saved');
                unsaveOffer(offerId);
            }
        });
        resultsContainer.appendChild(li);
    });
    countText.textContent = results.length + ' résultats';
}

function displayData(offers) {
    const points = offers.filter(
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
        .data(points);
}


// Request data
async function requestMapData() {
    loadingAnimation.goToAndPlay(0, true);
    mapContainer.classList.add('waiting');

    const response = await fetch('ajax/get_offers');
    const content = await response.json();

    displayData(content.offers);

    mapContainer.classList.remove('waiting');
    loadingAnimation.stop();
}

//Select map data
async function selectMapData(ids) {
    const response = await fetch('ajax/select_offers', {
        method: 'POST',
        headers: {
            "Content-Type": 'application/json'
        },
        body: JSON.stringify(ids)
    });
    const content = await response.json();
    resultsContainer.innerHTML = '';
    renderResults(content);
}

// Search offers
async function search(query) {
    loadingAnimation.goToAndPlay(0, true);
    mapContainer.classList.add('waiting');
    // Request offers
    const params = new URLSearchParams({
        query: query,
        style: 'preview'
    });
    const response = await fetch(`/ajax/search_offer?${params}`);
    const content = await response.json();
    resultsContainer.innerHTML = '';
    renderResults(content.html);
    displayData(content.data);
    mapContainer.classList.remove('waiting');
    loadingAnimation.stop();
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

document.addEventListener('dataUpdate', () => {
    requestMapData();
});

const observer = new ResizeObserver(() => {
    map.invalidateSize();
});
observer.observe(mapContainer);


// Hexbin events
hexLayer.hoverHandler(tooltipHandler);
hexLayer.dispatch().on('click', bin => {
    const ids = bin.map(point => point.o.offer_id);
    selectMapData(ids);
});

// On search
searchInput.addEventListener('change', (e) => {
    search(e.target.value);
});






export function update() {
    map.invalidateSize();
    searchInput.focus();
}




// Init

setZoom();
setCoo();
requestMapData();
searchInput.focus();