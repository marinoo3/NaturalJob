const section = document.querySelector('#console');
const modelContainers = section.querySelectorAll('.model-container');





modelContainers.forEach(container => {
    const modelName = container.dataset.modelName;
    const model = container.querySelector('.model');
    const button = model.querySelector('.main-button');
    const label = model.querySelector('.label');

    button.addEventListener('click', async (event) => {
        event.preventDefault();

        // Create progress background
        let progress = model.querySelector('.progress');
        if (!progress) {
            progress = document.createElement('div');
            progress.classList.add('progress');
            model.appendChild(progress);
        }

        model.classList.remove('error');
        model.classList.add('waiting');
        label.textContent = "Entrainement du model";

        const response = await fetch(`/ajax/fit_${modelName}`, {method: 'POST'});
        if (!response.ok) {
            model.classList.remove('waiting');
            model.classList.add('error');
            label.textContent = "Erreur";
        }

        const data = await response.json();
        label.textContent = data['model_name'];
        model.classList.remove('waiting');
        progress.remove();
    });
});