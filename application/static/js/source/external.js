import { displayOffer } from '../_helpers/offer_manager.js';

const section = document.querySelector('section#source');
const container = section.querySelector('.content');
const dropArea = container.querySelector('.drop-area');
const editorForm = container.querySelector('form.offer-editor');




function bindInput() {
    const fileInput = dropArea.querySelector('input[type="file"]');
    const setFile = (files) => {
        if (!files || files.length === 0) return;
        dropArea.querySelector('p').textContent = files[0].name;
    };

    dropArea.addEventListener('click', (e) => {
        if (!e.target.closest('input[name="url"]')) {
            fileInput.click();
        }
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
    });
}

function resetInput() {
    container.classList.replace('edit', 'input');
    dropArea.querySelector('p').textContent = "Déposer un fichier";
    dropArea.querySelector('input[name="url"]').value = ""

}

async function addOffer() {
    const data = new FormData(editorForm);
    const params = new URLSearchParams(data);
    const response = await fetch(`ajax/add_offer?${params}`, {
        method: 'POST'
    });
    const content = await response.json();
    await fetch('ajax/process_nlp/custom');
    displayOffer(content['offer_id']);
    // Send custom event
    const event = new Event('dataUpdate');
    document.dispatchEvent(event);
    resetInput();
}

async function processOffer(formData) {
    // init UI
    const fieldset = editorForm.querySelector('fieldset');
    container.classList.replace('input', 'edit');
    container.classList.remove('error');
    editorForm.classList.add('waiting');
    fieldset.disabled = true;
    // Request processed offer
    const response = await fetch(`ajax/process_offer`, {
        method: 'POST',
        body: formData
    });
    editorForm.classList.remove('waiting');
    fieldset.disabled = false;
    if (!response.ok) {
        container.classList.replace('edit', 'input');
        container.classList.add('error');
        return
    }
    const content = await response.json();
    // Update editor form
    Object.keys(content).forEach(key => {
        editorForm.elements[key].value = content[key];
    });
}



// On upload file
dropArea.querySelector('input[name="file"]').addEventListener('input', (e) => {
    const formData = new FormData();
    formData.append('file', e.target.files[0]);
    processOffer(formData);
});
// On enter URL
dropArea.querySelector('input[name="url"]').addEventListener('change', (e) => {
    const formData = new FormData();
    formData.append('url', e.target.value);
    processOffer(formData);
});

// On edit form submit
editorForm.addEventListener('submit', (e) => {
    e.preventDefault();
    addOffer()
});



bindInput();