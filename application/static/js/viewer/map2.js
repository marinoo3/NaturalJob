let map = L.map('map', { maxZoom: 14 }).setView([46.603354, 1.888334], 6);
var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png').addTo(map);



// Create hexbin layer
var hexLayer = L.hexbinLayer({
  radiusRange: [1, 10],
  radius: 10,
  opacity: 0.5,
  colorRange: ['#f7fbff', '#08306b']
}).addTo(map);

hexLayer
  .lng(d => d.longitude)
  .lat(d => d.latitude)
  .data([
    { longitude: 0.1, latitude: 45.1 }
  ]);



