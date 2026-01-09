import { saveOffer, unsaveOffer, savedOffers, displayOffer } from '../_helpers/offer_manager.js';

const section = document.querySelector('section#viewer');
const view = section.querySelector('.view');
const resultWrapper = section.querySelector('.result-wrapper');
const resultsContainer = section.querySelector('ul.results');
const searchForm = section.querySelector('form#search-form');
const salarySlider = searchForm.querySelector('.salary-slider[name="salary"]');
const attachResumeButton = searchForm.querySelector('#attach-resume');
const resumeValueInput = searchForm.querySelector('input[name="resume"]');
const refineWindow = section.querySelector('.refine');
const lottieContainer = section.querySelector('#lottie-container');

let likes = [];
let dislikes = [];


// Create sliders
noUiSlider.create(salarySlider, {
    start: [0, 0],
    connect: true,
    step: 500,
    tooltips: [wNumb({decimals: 0}), wNumb({decimals: 0})],
    range: {
        'min': 0,
        'max': 0
    }
});

// Create animation
const loadingAnimation = lottie.loadAnimation({
    container: lottieContainer,
    renderer: 'svg', // or 'canvas', 'html'
    loop: true,
    autoplay: false,
    path: lottieContainer.dataset.url
});



// Populate filters
async function populateFilters() {
    const response = await fetch('ajax/get_offers_bounds');
    const content = await response.json();
    console.log(content);
    // Populate silder
    salarySlider.noUiSlider.updateOptions({
        range: { 
            'min': content['salary'][0],
            '80%': (content['salary'][1] - content['salary'][0]) / 5,
            'max': content['salary'][1] 
        }
    })
    salarySlider.noUiSlider.set(content['salary'])
    // Populate city input
    const city = searchForm.elements['city'];
    city.options.length = 1;
    content['cities'].forEach(e => {
        const option = new Option(e[1], e[0]);
        city.add(option); // append the option to the select
    });
    // Populate city input
    const contract = searchForm.elements['contract'];
    contract.options.length = 1;
    content['contract_types'].forEach(e => {
        const option = new Option(e);
        contract.add(option); // append the option to the select
    });
    // Populate category input
    const category = searchForm.elements['category'];
    category.options.length = 1;
    content['clusters'].forEach(e => {
        const option = new Option(e[1], e[0]);
        category.add(option); // append the option to the select
    });
    // Populate source input
    const source = searchForm.elements['source'];
    source.options.length = 1;
    content['sources'].forEach(e => {
        const option = new Option(e);
        source.add(option); // append the option to the select
    });
}


// Update refine window
function updateRefine() {
    const count = likes.length + dislikes.length;
    refineWindow.querySelector('.count').textContent = likes.length + dislikes.length;
    refineWindow.querySelector('.likes .count').textContent = likes.length;
    refineWindow.querySelector('.dislikes .count').textContent = dislikes.length;
    if (count == 0) {
        refineWindow.classList.remove('active');
    } else {
        refineWindow.classList.add('active');
    }
}


// Render results
function renderResults(results) {
    results.forEach(html => {
        const li = document.createElement('li');
        li.innerHTML = html;
        const offer = li.querySelector('.offer');
        const offerId = offer.dataset.offerId;
        // Init state
        if (likes.includes(offerId)) {
            offer.classList.add('liked');
        } else if (dislikes.includes(offerId)) {
            offer.classList.add('dislike');
        }
        // Like button
        offer.querySelector('.actions .icon-button.like').addEventListener('click', () => {
            const index = likes.indexOf(offerId);
            if (index == -1) {
                offer.classList.add('liked');
                likes.push(offerId);
                const _index = dislikes.indexOf(offerId);
                if (_index != -1) {
                    dislikes.splice(_index, 1);
                    offer.classList.remove('disliked');
                }
            } else {
                offer.classList.remove('liked');
                likes.splice(index, 1);
            }
            updateRefine();
        });
        // Dislike button
        offer.querySelector('.actions .icon-button.dislike').addEventListener('click', () => {
            const index = dislikes.indexOf(offerId)
            if (index == -1) {
                offer.classList.add('disliked');
                dislikes.push(offerId);
                const _index = likes.indexOf(offerId);
                if (_index != -1) {
                    likes.splice(_index, 1);
                    offer.classList.remove('liked');
                }
            } else {
                offer.classList.remove('disliked');
                dislikes.splice(index, 1);
            }
            updateRefine();
        });
        // Save button
        offer.querySelector('.actions .icon-button.save').addEventListener('click', () => {
            if (!savedOffers.includes(offerId)) {
                offer.classList.add('saved');
                saveOffer(offerId);
            } else {
                offer.classList.remove('saved');
                unsaveOffer(offerId);
            }
        });
        // Display offer
        offer.addEventListener('click', (event) => {
            if (!event.target.closest('ul.actions')) {
                displayOffer(offerId);
            }
        });
        resultsContainer.appendChild(li);
    });
}


function createPopup(html) {
    const popup = document.createElement('div');
    popup.classList.add('popup');
    popup.innerHTML = html;
    // Bind save button
    const saveButton = popup.querySelector('button.submit');
    saveButton.addEventListener('click', async () => {
        const selected = popup.querySelector('input[name="template"]:checked');
        resumeValueInput.value = selected.value;
        const event = new Event('change', { bubbles: true });
        resumeValueInput.dispatchEvent(event);
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

function buildParamsURL(includeRefines=false) {
    const data = new FormData(searchForm);
    data.append('style', 'result');
    data.append('salary', JSON.stringify(salarySlider.noUiSlider.get()));
    if (includeRefines) {
        const refine = [
            ...likes.map(offer_id => ({ type: 'like', offer_id })),
            ...dislikes.map(offer_id => ({ type: 'dislike', offer_id })),
        ];
        data.append('refine', JSON.stringify(refine));
    }
    const query = new URLSearchParams(data);
    return query
}

async function search(paramsURL) {
    // Dispatch event
    const eventPrepare = new CustomEvent('prepareSearchOffers', {
        bubbles: true,
        cancelable: false
    });
    document.dispatchEvent(eventPrepare);
    // Init search and UI
    if (!paramsURL.get('query') && !paramsURL.get('resume')) {
        resultsContainer.innerHTML = '';
        resultWrapper.classList.add('empty');
        // Dispatch event
        const event = new CustomEvent('searchOffers', {
            detail: {
                ids: []
            },
            bubbles: true,
            cancelable: false
        });
        document.dispatchEvent(event);
        return
    }
    loadingAnimation.goToAndPlay(0, true);
    resultWrapper.classList.add('waiting');
    resultWrapper.classList.remove('empty');
    resultWrapper.classList.remove('error');
    // Request offers
    const response = await fetch(`/ajax/search_offer?${paramsURL}`);
    if (!response.ok) {
        resultsContainer.innerHTML = '';
        resultWrapper.classList.remove('waiting');
        resultWrapper.classList.add('error');
        loadingAnimation.stop();
        return
    }
    const content = await response.json();
    // Dispatch event
    const event = new CustomEvent('searchOffers', {
        detail: {
            ids: content['ids']
        },
        bubbles: true,
        cancelable: false
    });
    document.dispatchEvent(event);
    // Render offers
    resultsContainer.innerHTML = '';
    renderResults(content.html);
    resultWrapper.classList.remove('waiting');
    loadingAnimation.stop();
}



// Attach resume
attachResumeButton.addEventListener('click', async () => {
    const response = await fetch('/ajax/attach_template_popup/resume');
    const html = await response.text();
    // Create popup
    const popup = createPopup(html);
    view.appendChild(popup);
});

// Open refines
refineWindow.querySelector('.head').addEventListener('click', () => {
    refineWindow.classList.toggle('active');
});
// Clear likes / dislikes
refineWindow.querySelector('.likes button').addEventListener('click', () => {
    likes = [];
    resultsContainer.querySelectorAll('.offer.liked').forEach(offer => {
        offer.classList.remove('liked');
    });
    updateRefine();
});
refineWindow.querySelector('.dislikes button').addEventListener('click', () => {
    dislikes = [];
    resultsContainer.querySelectorAll('.offer.disliked').forEach(offer => {
        offer.classList.remove('disliked');
    });
    updateRefine();
});


// Form change - submit
salarySlider.noUiSlider.on('change.one', function () {
    const event = new Event('change', { bubbles: true });
    searchForm.dispatchEvent(event);  
});
resumeValueInput.addEventListener('change', (e) => {
    const parentElement = e.currentTarget.parentElement;
    if (e.currentTarget.value != "") {
        parentElement.classList.add('active');
    } else {
        parentElement.classList.remove('active');
    }
});
searchForm.addEventListener('change', () => {
    const paramsURL = buildParamsURL();
    search(paramsURL);
});
searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
});

// Refine submit
refineWindow.querySelector('button.refine-button').addEventListener('click', () => {
    const paramsURL = buildParamsURL(true);
    search(paramsURL);
    refineWindow.classList.remove('active');
});




export function update() {
    searchForm.querySelector('input[name="query"]').focus();
}





// Create filter slider and inputs
populateFilters()


// Update filters on Kmeans update
document.addEventListener('kmeansUpdated', () => {
    populateFilters();
});