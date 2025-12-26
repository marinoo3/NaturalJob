

async function loadPlot() {
    const res = await fetch('/ajax/cluster_plot');
    const content = await res.json();  // already an object
    const fig = JSON.parse(content);
    Plotly.newPlot('main-plot', fig.data, fig.layout, { responsive: true });

    gd.on('plotly_relayout', function(eventData) {
    if (eventData['scene.camera']) {
      const cam = eventData['scene.camera'];   // {eye:{x,y,z}, center:{...}, up:{...}}
      console.log('Current camera:', cam);

      // save it somewhere: send to server, localStorage, etc.
      // localStorage.setItem('clusterCamera', JSON.stringify(cam));
    }
  });
}

loadPlot();