import { createResumePopup, createCoverletterPopup, createEmailPopup, templates } from '../_helpers/file_manager.js';

const section = document.querySelector('section#viewer');
const wrapper = section.querySelector('.wrapper');
const fileManager = wrapper.querySelector('.file-manager');
const loadContainer = fileManager.querySelector('.load');
const createContainer = fileManager.querySelector('.create');
let easyMDE = null;
let savedContent = null;


function loadEditor() {
    easyMDE = new EasyMDE({
        element: wrapper.querySelector('#md-content'),
        sideBySideFullscreen: false,
        hideIcons: ["image", "preview", "side-by-side", "fullscreen", "guide", "|"]
    });
    EasyMDE.toggleSideBySide(easyMDE);
}

function createActions(uuid) {
    const toolbar = wrapper.querySelector('.editor-toolbar');
    let actions = toolbar.querySelector('.actions');
    if(actions) actions.remove();
    actions = document.createElement('div');
    actions.classList.add('actions');
    // Cancel button
    const cancelButton = document.createElement('button');
    cancelButton.textContent = "Annuler";
    cancelButton.classList.add('second-button');
    cancelButton.addEventListener('click', () => {
        loadTemplate(uuid);
    });
    // Save button
    const saveButton = document.createElement('button');
    saveButton.textContent = "Enregistrer";
    saveButton.classList.add('main-button');
    saveButton.addEventListener('click', () => {
        fetch(`ajax/update_template/${uuid}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 'content': easyMDE.value() })
        }).then(savedContent = easyMDE.value());
    });
    actions.appendChild(cancelButton);
    actions.appendChild(saveButton);
    toolbar.appendChild(actions);
}

export async function loadTemplate(uuid) {
    // Reads template content
    const response = await fetch(`ajax/read_template/${uuid}`);
    const content = await response.json();
    if(content.category == 'resume') {
        wrapper.dataset.fileType = 'pdf';
        const embed = wrapper.querySelector('embed');
        embed.src = content.content;
    } else {
        wrapper.dataset.fileType = 'md';
        // Display content
        easyMDE.value(content.content);
        // Update action buttons
        createActions(uuid);
    }
}

function renderTemplate(html) {
    const li = document.createElement('li');
    li.innerHTML = html;
    const uuid = li.querySelector('.wrapper').dataset.uuid;

    const actions = li.querySelector('.more');
    actions.remove();

    li.querySelector('.template.wrapper').addEventListener('click', () => {
        // Preview template content
        loadTemplate(uuid);
    });

    loadContainer.querySelector('ul').appendChild(li);
}


async function displayTemplates() {
    let count = 0
    Object.values(templates).forEach(category => {
        category.forEach(html => {
            renderTemplate(html)
            count += 1;
        });
    });

    if(count == 0) {
        loadContainer.classList.add('hidden');
    } else {
        loadContainer.classList.remove('hidden');
    }

}


createContainer.querySelector('.action.create-resume').addEventListener('click', async () => {
    const popup = await createResumePopup();
    document.body.appendChild(popup);
});
createContainer.querySelector('.action.create-coverletter').addEventListener('click', async () => {
    const popup = await createCoverletterPopup();
    document.body.appendChild(popup);
});
createContainer.querySelector('.action.create-email').addEventListener('click', async () => {
    const popup = await createEmailPopup();
    document.body.appendChild(popup);
});


loadEditor();
displayTemplates();
