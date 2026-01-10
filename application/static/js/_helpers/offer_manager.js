export let savedOffers = [];
export let appliedOffers = [];
let map = null;




async function createPopup(container, title, category) {
    // Request HTML
    const params = new URLSearchParams({ title: title });
    const response = await fetch(`/ajax/attach_template_popup/${category}?${params}`);
    const html = await response.text();
    // Create popup
    const popup = document.createElement('div');
    popup.classList.add('popup');
    popup.innerHTML = html;
    // Bind save button
    const saveButton = popup.querySelector('button.submit');
    saveButton.addEventListener('click', async () => {
        const selected = popup.querySelector('input[name="template"]:checked');
        const input = container.querySelector(`.custom-select input[name="${category}"]`);
        const label = container.querySelector('.custom-select p');
        input.value = selected.value;
        label.textContent = selected.dataset.templateName;
        popup.remove();
        if (category == 'coverletter') {
            const secondPopup = await createPopup(container, "Joindre un CV", 'resume');
            document.body.appendChild(secondPopup);
            return
        }
        const event = new Event('change', { bubbles: true });
        input.dispatchEvent(event);
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
    const generateConatiners = applyForm.querySelectorAll('.generate')
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
    generateConatiners.forEach(container => {
        const templateCategory = container.dataset.category;
        const customSelect = container.querySelector('.custom-select');
        customSelect.addEventListener('click', async () => {
            const popup = await createPopup(container, customSelect.title, templateCategory);
            document.body.appendChild(popup);
        });
        customSelect.addEventListener('change', async () => {
            container.classList.add('waiting');
            container.classList.remove('succeed');
            container.classList.remove('error');
            // Create progress background
            let progress = container.querySelector('.progress');
            if (!progress) {
                progress = document.createElement('div');
                progress.classList.add('progress');
                progress.style.width = "0px";
                container.appendChild(progress);
            }
            // Generate adapted template
            const params = new URLSearchParams()
            customSelect.querySelectorAll('input').forEach(input => {
                params.append(input.name, input.value);
            });
            params.append('offer_id', offerId);
            const response = await fetch(`ajax/generate_template?${params}`);
            container.classList.remove('waiting');
            if (!response.ok) {
                container.classList.add('error');
            } else {
                const content = await response.json();
                console.log(content['type']);
                console.log(content['template']);
                applyForm.querySelector(`textarea[name="${content['type']}"]`).value = content['template'];
                container.classList.add('succeed');
            }
        });
    });
    // Bind apply
    applyForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const coverletterContent = applyForm.elements['generated_coverletter'].value;
        const emailContent = applyForm.elements['generated_email'].value;
        applyForm.classList.add('waiting');
        // Ask server to apply
        const response = await fetch(`ajax/apply_offer/${offerId}`, {
            method: 'POST',
            body: coverletterContent
        });
        applyForm.classList.remove('waiting');
        if (!response.ok) {
            applyForm.classList.add('error');
        }
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
        if (emailContent) {
            const subject = encodeURIComponent(`Candidature spontanée - ${popup.querySelector('.header .title').textContent}`);
            const body = encodeURIComponent(emailContent);
            const emailUrl = `mailto:?subject=${subject}&body=${body}`;
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
    const coordinates = [mapElement.dataset.lat, mapElement.dataset.lon];
    if (!coordinates.includes('None')) {
        mapElement.classList.remove('hidden');
        map = L.map(mapElement, {maxZoom: 14, scrollWheelZoom: false}).setView(coordinates, 11);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {maxZoom: 20}).addTo(map);
        L.circleMarker(coordinates, {color: 'var(--accent-color)', radius: 20}).addTo(map);
    }
}

// Init arrays arrays

savedOffers = await loadSavedOffers();
appliedOffers = await loadAppliedOffers();