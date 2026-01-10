import { savedOffers, unsaveOffer, displayOffer } from '../_helpers/offer_manager.js';

const section = document.querySelector('section#documents');
const offersContainer = section.querySelector('ul.offers');



// Render offer on list
async function renderOffers(offerIds) {
    if (offerIds.length == 0) {
        return
    }
    // Request HTMLs
    const params = new URLSearchParams();
    offerIds.forEach(id => params.append('id', id));
    const response = await fetch(`ajax/render_offers?${params}`);
    const content = await response.json();
    // Render offers
    content.forEach(html => {
        const li = document.createElement('li');
        li.innerHTML = html;
        const offerId = li.querySelector('.offer').dataset.offerId;
        li.querySelector('button.save').addEventListener('click', () => {
            unsaveOffer(offerId);
        });
        li.addEventListener('click', (event) => {
            if (!event.target.closest('button')) {
                displayOffer(offerId);
            }
        });
        offersContainer.appendChild(li);
    });   
}

function removeOffer(offerId) {
    const offer = offersContainer.querySelector(`.offer[data-offer-id='${offerId}']`);
    offer.parentElement.remove();
}




// Render and load offers when saved
document.addEventListener('offerSaved', async (e) => {
    renderOffers([e.detail.offerId]);
});
document.addEventListener('offerUnsaved', async (e) => {
    removeOffer(e.detail.offerId);
});

// Render initial saved offers
renderOffers(savedOffers);