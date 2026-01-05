export let savedOffers = [];
export let appliedOffers = [];




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


// Public arrays

savedOffers = await loadSavedOffers();
appliedOffers = await loadAppliedOffers();