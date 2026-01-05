const section = document.querySelector('section#console');
const clusterPlot = section.querySelector('#cluster-plot')


function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function loadPlot() {
    const res = await fetch('/ajax/cluster_plot');
    const content = await res.json();
    const fig = JSON.parse(content);
    Plotly.newPlot(clusterPlot, fig.data, fig.layout, { responsive: true });
}

function relayoutPlot() {
    Plotly.relayout(clusterPlot, {
        width: clusterPlot.clientWidth,
        height: clusterPlot.clientHeight
    });
}



// Relayout on resize
const observer = new ResizeObserver(() => {
    relayoutPlot();
});

document.addEventListener('kmeansUpdated', () => {
    loadPlot().then(() => {
        relayoutPlot();
    })
});





export function update() {
    wait(5).then(() => {
        relayoutPlot();
    });
}

loadPlot().then(() => {
    observer.observe(section);
});