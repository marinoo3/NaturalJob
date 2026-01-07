const section = document.querySelector('section#console');
const clusterPlot = section.querySelector('#cluster-plot');


function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function loadPlot() {
    const res = await fetch('/ajax/cluster_plot');
    const content = await res.json();
    const fig = JSON.parse(content);
    await Plotly.newPlot(clusterPlot, fig.data, fig.layout, { responsive: true });
}

function relayoutPlot() {
    Plotly.relayout(clusterPlot, {
        width: clusterPlot.clientWidth,
        height: clusterPlot.clientHeight
    });
}

function highlightOffer(offerId, color = '#73ef88') {
    const gd = clusterPlot;

    for (let traceIdx = 0; traceIdx < gd.data.length; traceIdx++) {
        const trace = gd.data[traceIdx];
        const custom = trace.customdata;
        if (!custom) continue;

        // locate the point whose customdata (offer_id) matches
        let pointIdx = -1;
        for (let i = 0; i < custom.length; i++) {
            const value = Array.isArray(custom[i]) ? custom[i][0] : custom[i];
            if (String(value) === String(offerId)) {
                pointIdx = i;
                break;
            }
        }
        if (pointIdx === -1) continue;

        const count = trace.x.length;

        // build color array for this trace
        let colors;
        if (Array.isArray(trace.marker.color) && trace.marker.color.length === count) {
            colors = trace.marker.color.slice();
        } else {
            const baseColor = trace.marker.color || trace.marker.color?.[0] || '#ffffff';
            colors = Array(count).fill(baseColor);
        }

        colors[pointIdx] = color;

        Plotly.restyle(gd, { 'marker.color': [colors] }, traceIdx);
        return;
    }

    console.warn(`Offer id ${offerId} not found in plot.`);
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
    highlightOffer(1);
});