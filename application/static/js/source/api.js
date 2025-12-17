const section = document.querySelector('#source');
const view = section.querySelector('.view')



function startUpdate(source, database) {
    const countLabel = database.querySelector('.status #label');
    const progress = view.querySelector('.database .progress');
    const evt = new EventSource(`/ajax/update_bdd_stream/${source}`);

    evt.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        if (payload.count !== undefined) {
            console.log(payload.progress);
            progress.style.width = payload.progress + "%";
            countLabel.textContent = `Collecting ${payload.count} jobs`;
        }
        if (payload.status === 'done') {
            countLabel.textContent = payload.total + ' offres'
            evt.close();
        }
    };

    evt.addEventListener('error', (event) => {
        countLabel.textContent = "Erreur de chargement"
        database.classList.add('error');
        console.error('SSE error', event);
        evt.close();
    });

    evt.addEventListener('end', () => evt.close());
}



export function update() {
    const database = view.querySelector('.database');
    const source = database.dataset.source;
    const updateButton = database.querySelector('button#update');
    

    // Create progress background
    let progress = view.querySelector('.database .progress');
    if (!progress) {
        progress = document.createElement('div');
        progress.classList.add('progress');
        progress.style.width = "0px";
        database.appendChild(progress);
    }
    
    updateButton.addEventListener('click', async () => {
        startUpdate(source, database);
    });
}