const section = document.querySelector('section#console');
const topJobContainer = section.querySelector('#top-offers-plot');
const contractContainer = section.querySelector('#contract-plot');
const experienceCOntainer = section.querySelector('#experience-plot');


function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function loadStatPlots(ids=[]) {
    // Request plot jsons
    const params = new URLSearchParams();
    ids.forEach(id => params.append('id', id));
    const res = await fetch(`/ajax/stat_plots?${params}`);
    const content = await res.json();
    // Extract data
    const topJobsFig = JSON.parse(content.topJobs);
    const contractsFig = JSON.parse(content.contracts);
    const experienceFig = JSON.parse(content.experiences);
    await Plotly.react(topJobContainer, topJobsFig.data, topJobsFig.layout, { responsive: true });
    await Plotly.react(contractContainer, contractsFig.data, contractsFig.layout, { responsive: true });
    await Plotly.react(experienceCOntainer, experienceFig.data, experienceFig.layout, { responsive: true });
}

function relayoutPlots() {
    Plotly.relayout(topJobContainer, {
        width: topJobContainer.clientWidth,
        height: topJobContainer.clientHeight
    });
    Plotly.relayout(contractContainer, {
        width: contractContainer.clientWidth,
        height: contractContainer.clientHeight
    });
    Plotly.relayout(experienceCOntainer, {
        width: experienceCOntainer.clientWidth,
        height: experienceCOntainer.clientHeight
    });
}




// Relayout on resize
const observer = new ResizeObserver(() => {
    relayoutPlots();
});

document.addEventListener('searchOffers', (e) => {
    loadStatPlots(e.detail.ids);
});





export function update() {
    wait(5).then(() => {
        relayoutPlots();
    });
}

loadStatPlots().then(() => {
    observer.observe(section);
});
