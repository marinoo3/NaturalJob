

async function loadPlot() {
    const res = await fetch('/ajax/cluster_plot');
    const content = await res.json();
    const fig = JSON.parse(content);
    Plotly.newPlot('main-plot', fig.data, fig.layout, { responsive: true });
}




loadPlot();