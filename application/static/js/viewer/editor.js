let easyMDE = null;
let templateUUID = null;


function loadEditor() {
    easyMDE = new EasyMDE({
        element: document.querySelector('#md-content'),
        sideBySideFullscreen: false,
        hideIcons: ["image", "preview", "side-by-side", "fullscreen", "guide", "|"]
    });
    EasyMDE.toggleSideBySide(easyMDE);
}

function createActions(uuid) {
    const toolbar = document.querySelector('.editor-toolbar');
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
    saveButton.addEventListener('click', async () => {
        const response = await fetch(`ajax/update_template/${uuid}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 'content': easyMDE.value() })
        });
    });
    actions.appendChild(cancelButton);
    actions.appendChild(saveButton);
    toolbar.appendChild(actions);
}

export async function loadTemplate(uuid) {
    // Reads template content
    const response = await fetch(`ajax/read_template/${uuid}`);
    const content = await response.json();
    // Display content
    easyMDE.value(content.content);
    // Update action buttons
    createActions(uuid);
}


loadEditor();
