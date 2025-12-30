

async function loadPlot() {
    const res = await fetch('/ajax/cluster_plot');
    const content = await res.json();  // already an object
    const fig = JSON.parse(content);
    Plotly.newPlot('main-plot', fig.data, fig.layout, { responsive: true });
}




loadPlot();