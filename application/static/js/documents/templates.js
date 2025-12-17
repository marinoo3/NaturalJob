import { createResumePopup, createCoverletterPopup, createEmailPopup, templates } from '../_helpers/file_manager.js';


const section = document.querySelector('#documents');
const editorTab = document.querySelector('#viewer li[data-tab-id="editor"]');
const categoryContainers = section.querySelectorAll('.category');
const uploadResumeButton = document.querySelector('#create-resume-button');
const createCoverLetterButton = document.querySelector('#create-coverletter-button');
const createEmailButton = document.querySelector('#create-email-button');





function renderTemplate(documents) {
    documents.innerHTML = '';
    const key = documents.dataset.category;
    if (templates[key].length != 0) {
        templates[key].forEach(html => {
            const li = document.createElement('li');
            li.innerHTML = html;
            const wrapper = li.querySelector('.wrapper');
            const uuid = wrapper.dataset.uuid;
            
            wrapper.addEventListener('click', async (e) => {
                // Open editor and preview template content
                if (e.target.parentElement.tagName != 'BUTTON') {
                    const module = await switchTab(editorTab);
                    module.loadTemplate(uuid);
                }
            });

            const editButton = wrapper.querySelector('.actions #edit');
            editButton.addEventListener('click', async (e) => {
                // Open editor and preview template content
                const module = await switchTab(editorTab);
                module.loadTemplate(uuid);
            });
            
            const deleteButton = wrapper.querySelector('.actions #delete');
            deleteButton.addEventListener('click', () => {
                li.remove();
                fetch(`ajax/delete_template/${uuid}`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' }
                }).then(loadTemplates);
            });
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




// Foldable categories
categoryContainers.forEach(category => {
    const title = category.querySelector('.foldable');
    title.addEventListener('click', () => {
        category.classList.toggle('folded');
    });
});

// Render and load document when created
document.addEventListener('templateCreated', async (e) => {
    // Render template and preview content
    const documents = document.querySelector(`.category .docs[data-category='${e.detail.category}']`);
    renderTemplate(documents);
    const module = await switchTab(editorTab);
    module.loadTemplate(e.detail.uuid);
});

// Upload resume button
uploadResumeButton.addEventListener('click', async () => {
    const popup = await createResumePopup();
    document.body.appendChild(popup);
});

// Create cover letter button
createCoverLetterButton.addEventListener('click', async () => {
    const popup = await createCoverletterPopup();
    document.body.appendChild(popup);
});

// Create email button
createEmailButton.addEventListener('click', async () => {
    const popup = await createEmailPopup()
    document.body.appendChild(popup);
});


// Load and render templates
loadTemplates();