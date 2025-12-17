const section = document.querySelector('#source');



export function update() {
    const updateButton = section.querySelector('button#update');
    updateButton.addEventListener('click', async () => {
        const source = updateButton.dataset.source;
        const response = await fetch('/ajax/update_bdd/' + source, {
            method: 'POST'
        });
        const content = await response.json();
    });
}