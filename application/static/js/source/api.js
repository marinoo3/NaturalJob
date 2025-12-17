const section = document.querySelector('#source');
const view = section.querySelector('.view')


function buildTable(content) {
    const summaryTable = view.querySelector('table.summary');
    summaryTable.innerHTML = '';
    const summaryHeaders = document.createElement('thead');
    const headerRow = document.createElement('tr');
    summaryHeaders.appendChild(headerRow);

    // Get keys and ensure 'name' is first
    const keys = Object.keys(content.summary[0]).sort((a, b) =>
    a === 'name' ? -1 : b === 'name' ? 1 : 0
    );

    // Build header
    keys.forEach(key => {
    const cell = document.createElement('th');
    cell.textContent = key;
    cell.classList.add(key);
    headerRow.appendChild(cell);
    });

    const summaryBody = document.createElement('tbody');

    // Build rows using the sorted keys
    content.summary.forEach(row => {
    const rowElement = document.createElement('tr');
    keys.forEach(key => {
        const cell = document.createElement('td');
        cell.textContent = row[key];
        cell.classList.add(key);
        rowElement.appendChild(cell);
    });
    summaryBody.appendChild(rowElement);
    });

    summaryTable.appendChild(summaryHeaders);
    summaryTable.appendChild(summaryBody);
}


async function initDB(source, database) {
    const countLabel = database.querySelector('.status #label');
    const dateLabel = database.querySelector('.actions .date');

    // Request DB info
    const response = await fetch(`/ajax/bdd_info/${source}`);
    if (!response.ok) {
        database.classList.add('error');
        countLabel.textContent = 'Erreur de chargement';
        dateLabel.textContent = 'NA';
        return
    }
    // Set UI
    const content = await response.json();
    countLabel.textContent = content.total + ' offres';
    dateLabel.textContent = content.date;
    // Create summary table
    buildTable(content);
}


function startUpdate(source, database) {
    const progress = view.querySelector('.database .progress');
    const countLabel = database.querySelector('.status #label');
    // Reset progress bar
    database.classList.remove('error');
    database.classList.add('waiting');
    countLabel.textContent = `Initialization`;
    // Send SSE request
    const evt = new EventSource(`/ajax/update_bdd_stream/${source}`);

    evt.onmessage = (event) => {
        database.classList.remove('waiting');
        progress.style.left = '0px';
        progress.style.width = '0px';
        const payload = JSON.parse(event.data);
        if (payload.count !== undefined) {
            progress.style.width = payload.progress + "%";
            countLabel.textContent = `Collecting ${payload.count} jobs`;
        }
        if (payload.status === 'done') {
            progress.style.width = '100%';
            initDB(source, database);
            evt.close();
        }
    };

    evt.addEventListener('error', (event) => {
        countLabel.textContent = "Erreur de chargement"
        database.classList.remove('waiting');
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
    
    initDB(source, database);
    
    updateButton.addEventListener('click', async () => {
        // Create progress background
        let progress = view.querySelector('.database .progress');
        if (!progress) {
            progress = document.createElement('div');
            progress.classList.add('progress');
            progress.style.width = "0px";
            database.appendChild(progress);
        }
        // Start SSE
        startUpdate(source, database);
    });
}