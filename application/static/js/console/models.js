const section = document.querySelector('#console');
const modelContainers = section.querySelectorAll('.model-container');

console.log('hello there');

modelContainers.forEach(container => {
    const modelName = container.dataset.modelName;
    const button = container.querySelector('.main-button');
    button.addEventListener('click', async (event) => {
        event.preventDefault();
        const response = await fetch(`/ajax/fit_${modelName}`, {
            method: 'POST'
        });
        console.log(response.ok);
    });
});