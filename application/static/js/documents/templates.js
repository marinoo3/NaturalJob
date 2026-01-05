import { createResumePopup, createCoverletterPopup, createEmailPopup, deleteTemplate, templates } from '../_helpers/file_manager.js';


const section = document.querySelector('#documents');
const view = section.querySelector('.view');
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
                deleteTemplate(uuid);
                li.remove();
            });
            documents.appendChild(li);
        });
        documents.parentElement.classList.remove('folded');
    } else {
        documents.innerHTML = '<p class="third">Aucun documents</p>';
        documents.parentElement.classList.add('folded');
    }

}

function initTemplates() {
    // Render all templates templates
    categoryContainers.forEach(category => {
        const documents = category.querySelector('.docs');
        renderTemplate(documents);
    });
}







document.addEventListener('templateLoaded', () => {
    initTemplates();
});

document.addEventListener('templateCreated', (e) => {
    // Render template
    const documents = categoryContainers[0].parentElement.querySelector(`.category .docs[data-category='${e.detail.category}']`);
    documents.parentElement.classList.remove('folded');
    renderTemplate(documents);
    // Load template in editor
    switchTab(editorTab).then(module => {
        module.loadTemplate(e.detail.uuid);
    });
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





// Foldable categories
categoryContainers.forEach(category => {
    const title = category.querySelector('.foldable');
    title.addEventListener('click', () => {
        category.classList.toggle('folded');
    });
});

initTemplates()