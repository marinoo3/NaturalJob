const section = document.querySelector('#documents');
const categoryContainers = section.querySelectorAll('.category');
const uploadResumeButton = document.querySelector('#create-resume-button');
const createCoverLetterButton = document.querySelector('#create-coverletter-button');
const createEmailButton = document.querySelector('#create-email-button');
let templates = {
    'resume': [],
    'coverletter': [],
    'email': []
};



function renderTemplate(documents) {
    documents.innerHTML = '';
    const key = documents.dataset.category;
    if (templates[key].length != 0) {
        templates[key].forEach(html => {
            const li = document.createElement('li');
            li.innerHTML = html;
            documents.appendChild(li);
        });
    } else {
        documents.innerHTML = '<p class="third">Aucun documents</p>';
        documents.parentElement.classList.add('folded');
    }

}

async function loadTemplates() {
    const response = await fetch('ajax/get_templates');
    const content = await response.json();

    console.log(content);

    // Empty all templates and set updated ones
    Object.values(templates).forEach(arr => arr.length = 0);
    for (const [key, value] of Object.entries(content)) {
        templates[key] = value;
    }

    
    categoryContainers.forEach(category => {
        const documents = category.querySelector('.docs');
        renderTemplate(documents);
    });
}

function createPopup(html) {
    // Create popup
    const popup = document.createElement('div');
    popup.classList.add('popup');
    popup.innerHTML = html;
    // Any input change
    const form = popup.querySelector('form');
    form.addEventListener('input', () => {
        let allFilled = true;
        form.querySelectorAll('input').forEach(input => {
            if (input.value.trim() == '') {
                allFilled = false;
            }
        });

        if (allFilled) {
            form.querySelector('button.main-button').classList.remove('disabled');
        } else {
            form.querySelector('button.main-button').classList.add('disabled');
        }
    });
    // Close popup
    popup.addEventListener('click', (event) => {
        if (event.target === popup || event.target.closest('button.cancel')) {
            popup.remove();
        }
    });

    return { popup, form };
}

async function createTemplate(formData) {
    // Send file creation request
    const response = await fetch('ajax/create_template', {
        method: 'POST',
        body: formData
    })
    // Show message on error
    if (!response.ok) {
        // TODO: Custom error message
        alert('Erreur lors de la création de la template');
        return;
    }
    const content = await response.json()
    // Add to file manager and preview the template content
    templates[content.category].push(content.html);
    const documents = document.querySelector(`.category .docs[data-category='${content.category}']`);
    renderTemplate(documents);
}



// Foldable categories
categoryContainers.forEach(category => {
    const title = category.querySelector('.foldable');
    title.addEventListener('click', () => {
        category.classList.toggle('folded');
    });
});

// Upload resume button
uploadResumeButton.addEventListener('click', async () => {
    const title = 'Ajouter un CV';
    const response = await fetch(`ajax/upload_file_popup/${title}`);
    const html = await response.text();

    // Create popup element
    const { popup, form } = createPopup(html);

    // File input
    const fileInput = popup.querySelector('input[type="file"]');
    const dropArea = popup.querySelector('.drop-area');
    const setFile = (files) => {
        if (!files || files.length === 0) return;
        dropArea.querySelector('p').textContent = files[0].name;
    };

    dropArea.addEventListener('click', () => {
        fileInput.click();
    });
    fileInput.addEventListener('change', () => {
        setFile(fileInput.files);
    });
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault(); // Necessary to allow drop
        dropArea.classList.add('dragover');
    });
    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('dragover');
    });
    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (!files || files.length === 0) return;

        fileInput.files = files;
        fileInput.dispatchEvent(new Event('input', { bubbles: true }));

        setFile(files);
        popup.remove();
    });

    // Submit form
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const file = form.querySelector('input[type="file"]').files[0];
        const name = form.querySelector('input[name="name"]').value.trim();
        const description = form.querySelector('input[name="description"]').value.trim();

        const formData = new FormData();
        formData.append('file', file);
        formData.append('name', name);
        formData.append('description', description);
        formData.append('category', 'resume');

        createTemplate(formData);
        popup.remove();
    });

    document.body.appendChild(popup);
});

// Create cover letter button
createCoverLetterButton.addEventListener('click', async () => {
    const title = 'Créer une lettre de motivation';
    const response = await fetch(`ajax/create_file_popup/${title}`);
    const html = await response.text();

    // Create popup element
    const { popup, form } = createPopup(html);

    // Submit form
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = form.querySelector('input[name="name"]').value.trim();
        const description = form.querySelector('input[name="description"]').value.trim();

        const formData = new FormData();
        formData.append('name', name);
        formData.append('description', description);
        formData.append('category', 'coverletter');

        createTemplate(formData);
        popup.remove();
    });

    document.body.appendChild(popup);
});

// Create email button
createEmailButton.addEventListener('click', async () => {
    const title = 'Créer un email';
    const response = await fetch(`ajax/create_file_popup/${title}`);
    const html = await response.text();

    // Create popup element
    const { popup, form } = createPopup(html);

    // Submit form
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = form.querySelector('input[name="name"]').value.trim();
        const description = form.querySelector('input[name="description"]').value.trim();

        const formData = new FormData();
        formData.append('name', name);
        formData.append('description', description);
        formData.append('category', 'coverletter');

        createTemplate(formData);
    });

    document.body.appendChild(popup);
});



// Load and render templates
loadTemplates();