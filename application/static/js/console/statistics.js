const section = document.querySelector('section#console');
const topJobContainer = section.querySelector('#top-offers-plot');
const contractContainer = section.querySelector('#contract-plot');



async function loadStatPlots() {
    // Request plot jsons
    const res = await fetch('/ajax/stat_plots');
    const content = await res.json();
    // Extract data
    const topJobsFig = JSON.parse(content.topJobs);
    const contractsFig = JSON.parse(content.contracts);
    await Plotly.react(topJobContainer, topJobsFig.data, topJobsFig.layout, { responsive: true });
    await Plotly.react(contractContainer, contractsFig.data, contractsFig.layout, { responsive: true });
}

// Relayout on resize
const observer = new ResizeObserver(() => {
    Plotly.relayout(topJobContainer, {
        width: topJobContainer.clientWidth,
        height: topJobContainer.clientHeight
    });
    Plotly.relayout(contractContainer, {
        width: contractContainer.clientWidth,
        height: contractContainer.clientHeight
    });
});



loadStatPlots().then(() => {
    observer.observe(section);
});



