const section = document.querySelector('#console');
const modelContainers = section.querySelectorAll('.model-container');



function buildParamsURL(form) {
    const formData = new FormData(form);
    return new URLSearchParams(formData)
}


// Create settings popup

async function createSettingsPopup(form) {
    const paramsURL = buildParamsURL(form);
    const response = await fetch(`/ajax/model_settings_popup?${paramsURL}`);
    const html = await response.text();

    const popup = document.createElement('div');
    popup.classList.add('popup');
    popup.innerHTML = html;
    const inputs = popup.querySelectorAll('input');
    const saveButton = popup.querySelector('button.main-button');
    // Change input value
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            const allFilled = [...inputs].every(input => input.value.trim() !== '');
            if (allFilled) {
                saveButton.classList.remove('disabled');
            } else {
                saveButton.classList.add('disabled');
            }
        })
    });
    // Bind save button    
    saveButton.addEventListener('click', () => {
        inputs.forEach(input => {
            form.elements[input.name].value = input.value;
        });
        popup.remove();
    });
    // Close popup
    popup.addEventListener('click', (event) => {
        if (event.target === popup || event.target.closest('button.cancel')) {
            popup.remove();
        }
    });

    // TODO: 
    // [html]: create a settings_popup element, it loops with Jinja on the inputs parametter to create inputs
    // [pyhton]: render the popup html with a list of each param names
    // [js]: loop through inputs in the popup and bind there values to the .actions hidden inputs values on submit

    return popup;
}


// Update model features

function updateMetadata(container, data) {
    // Features
    const featuresContainer = container.querySelector('ul.features');
    featuresContainer.innerHTML = '';
    for (const feature of Object.values(data.features)) {
        const li = document.createElement('li');
        li.title = feature.label;
        const img = document.createElement('img');
        img.height = 12;
        img.src = feature.icon;
        const p = document.createElement('p');
        p.textContent = feature.value;
        li.appendChild(img);
        li.appendChild(p);
        featuresContainer.appendChild(li);
    };
    // Model name / data
    const modelContainer = container.querySelector('.model');
    modelContainer.querySelector('.label').textContent = `${data.prefix}${data.version}_s${data.shape}`;
    modelContainer.querySelector('.date').textContent = data.date;
}








async function initModels() {
    const response = await fetch('/ajax/get_models_metadata');
    const content = await response.json();

    modelContainers.forEach(container => {
        const modelName = container.dataset.modelName;
        const model = container.querySelector('.model');
        const label = model.querySelector('.label');
        const form = model.querySelector('form.actions');
        const settingsButton = form.querySelector('.settings');

        form.addEventListener('submit', async (event) => {
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

            const formData = new FormData(form);
            const response = await fetch(`/ajax/fit_${modelName}`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                model.classList.remove('waiting');
                model.classList.add('error');
                label.textContent = "Erreur de traitement";
                return
            }

            const data = await response.json();
            model.classList.remove('waiting');
            progress.remove();

            updateMetadata(container, data);
        });

        settingsButton.addEventListener('click', async () => {
            const popup = await createSettingsPopup(form);
            container.appendChild(popup);
        });

        if (Object.hasOwn(content, modelName)){
            updateMetadata(container, content[modelName]);
        }
    });
}

initModels()