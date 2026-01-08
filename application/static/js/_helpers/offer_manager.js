export let savedOffers = [];
export let appliedOffers = [];
let map = null;




function createPopup(html, form) {
    const popup = document.createElement('div');
    popup.classList.add('popup');
    popup.innerHTML = html;
    // Bind save button
    const saveButton = popup.querySelector('button.submit');
    saveButton.addEventListener('click', async () => {
        const selected = popup.querySelector('input[name="template"]:checked');
        form.querySelector('.custom-select input').value = selected.value;
        form.querySelector('.custom-select p').textContent = selected.dataset.templateName;
        form.querySelector('button').disabled = false;
        form.parentElement.classList.remove('succeed');
        popup.remove();
    });
    // Close popup
    popup.addEventListener('click', (event) => {
        if (event.target === popup || event.target.closest('button.cancel')) {
            popup.remove();
        }
    });

    return popup
}

// Util functions
function bindOfferPopup(popup, offerId) {
    const offer = popup.querySelector('.offer-fullview');
    const applyForm = popup.querySelector('form#apply');
    const generateForms = popup.querySelectorAll('.generate form');
    // Check offer status
    if (savedOffers.includes(offerId)) {
        offer.classList.add('saved');
    }
    // Bind saving
    popup.querySelector('button.save').addEventListener('click', () => {
        if (savedOffers.includes(offerId)) {
            unsaveOffer(offerId);
            offer.classList.remove('saved');
        } else {
            saveOffer(offerId);
            offer.classList.add('saved');
        }
    });
    // Bind generating
    generateForms.forEach(form => {
        const generateContainer = form.parentElement;
        const templateCategory = generateContainer.dataset.category;
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            generateContainer.classList.remove('error');
            generateContainer.classList.add('waiting');
            // Request generation
            const data = new FormData(form);
            data.append('offer_id', offerId);
            const params = new URLSearchParams(data);
            const response = await fetch(`ajax/generate_template?${params}`);
            generateContainer.classList.remove('waiting');
            if (!response.ok) {
                generateContainer.classList.add('error');
            } else {
                generateContainer.classList.add('succeed');
            }
            const content = await response.json();
            applyForm.querySelector(`input[name="${templateCategory}"]`).value = content['template'];
        });
        form.querySelector('.custom-select').addEventListener('click', async () => {
            const response = await fetch(`/ajax/attach_template_popup/${templateCategory}`);
            const html = await response.text();
            // Create popup
            const popup = createPopup(html, form);
            document.body.appendChild(popup);
        });
    });
    // Bind apply
    applyForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        // Ask server to apply
        const data = new FormData(applyForm);
        const params = new URLSearchParams(data);
        const response = await fetch(`ajax/apply_offer/${offerId}?${params}`);
        const isFile = response.headers.get('X-Is-File') === 'yes';
        // Download coverletter if exists
        if (isFile) {
            let filename = 'Lettre de motivation.pdf';

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();

            a.remove();
            window.URL.revokeObjectURL(url);
        }
        // Open email exists
        if (data.get('email')) {
            const offerTitle = popup.querySelector('.header .title');
            const emailUrl = `mailto:?subject=Candidature spontanée - ${offerTitle.textContent}&body=${data.get('email')}`;
            window.open(emailUrl, '_blank');
        }
    });
    // Close popup
    popup.addEventListener('click', (event) => {
        if (event.target === popup) {
            popup.remove();
        }
    });
}






// Saved offers

export async function loadSavedOffers() {
    const response = await fetch('ajax/get_saved_offers');
    const content = await response.json();
    savedOffers = content;
    return savedOffers
}

export function saveOffer(id) {
    savedOffers.push(id);
    fetch(`ajax/save_offer/${id}`, {method: 'POST'});

    // Dispatch event
    const event = new CustomEvent('offerSaved', {
        detail: {
            offerId: id
        },
        bubbles: true,
        cancelable: false
    });

    document.dispatchEvent(event);
}

export function unsaveOffer(id) {
    const index = savedOffers.indexOf(id);
    if (index != -1) {
        savedOffers.splice(index, 1);
        fetch(`ajax/unsave_offer/${id}`, {method: 'DELETE',});

        // Dispatch event
        const event = new CustomEvent('offerUnsaved', {
            detail: {
                offerId: id
            },
            bubbles: true,
            cancelable: false
        });

        document.dispatchEvent(event);
    }
}


// Applied offers

export async function loadAppliedOffers() {
    const response = await fetch('ajax/get_applied_offers');
    const content = await response.json();
    appliedOffers = content;
    return appliedOffers
}

export function applyOffer(id) {
    appliedOffers.push(id);
    fetch(`ajax/apply_offer/${id}`, {method: 'POST'});
}


// Display offers

export async function displayOffer(offerId) {
    // Request HTML
    const response = await fetch(`ajax/offer_fullview_popup/${offerId}`);
    const html = await response.text();
    // Create popup
    const popup = document.createElement('div');
    popup.classList.add('popup');
    popup.innerHTML = html;
    offerId = offerId.toString();
    bindOfferPopup(popup, offerId);
    // Add popup to DOM
    document.body.appendChild(popup);
    // Init the map
    const mapElement = popup.querySelector('#offer-map');
    map = L.map(mapElement, {maxZoom: 14, scrollWheelZoom: false}).setView([mapElement.dataset.lat, mapElement.dataset.lon], 11);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {maxZoom: 20}).addTo(map);
    L.circleMarker([mapElement.dataset.lat, mapElement.dataset.lon], {color: 'var(--accent-color)', radius: 20}).addTo(map);
}

// Init arrays arrays

savedOffers = await loadSavedOffers();
appliedOffers = await loadAppliedOffers();