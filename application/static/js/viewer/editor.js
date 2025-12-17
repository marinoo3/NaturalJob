import { createPopup } from '../_helpers/file_manager.js';

const wrapper = document.querySelector('section#viewer .wrapper');
const fileManager = wrapper.querySelector('.file-manager');
const loadContainer = fileManager.querySelector('.load');
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
        console.log(content.content);
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


async function loadTemplates() {
    const response = await fetch('ajax/get_templates');
    const content = await response.json();

    console.log(content);

    
}


loadContainer.querySelectorAll('button').forEach(button => {

});


loadEditor();
loadTemplates();
