const section = document.querySelector('#source');
const updateButton = section.querySelector('button#update');




updateButton.addEventListener('click', async () => {
    const response = await fetch('/ajax/update_ntne');
    const content = await response.json();
});