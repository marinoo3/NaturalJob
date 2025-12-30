const section = document.querySelector('section#viewer');
const view = section.querySelector('.view');
const resultsContainer = section.querySelector('ul.results');
const searchForm = section.querySelector('form#search-form');
const salarySlider = searchForm.querySelector('.salary-slider[name="salary"]');
const attachResumeButton = searchForm.querySelector('#attach-resume');
const resumeValueInput = searchForm.querySelector('input[name="resume"]');

let likes = [];
let dislikes = [];


// Create sliders
noUiSlider.create(salarySlider, {
    start: [0, 70000],
    connect: true,
    step: 500,
    tooltips: [wNumb({decimals: 0}), wNumb({decimals: 0})],
    range: {
        'min': 0,
        'max': 70000
    }
});


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
            console.log(offerId);
            const index = likes.indexOf(offerId);
            console.log(index);
            if (index == -1) {
                offer.classList.add('liked');
                likes.push(offerId);
                const _index = dislikes.indexOf(offerId);
                if (_index != -1) {
                    dislikes.slice(index, 1);
                }
            } else {
                offer.classList.remove('liked');
                likes.splice(index, 1);
            }
        });
        // Dislike button
        offer.querySelector('.actions .icon-button.dislike').addEventListener('click', () => {
            const index = dislikes.indexOf(offerId)
            if (index == -1) {
                offer.classList.add('disliked');
                dislikes.push(offerId);
                const _index = likes.indexOf(offerId);
                if (_index != -1) {
                    likes.slice(index, 1);
                }
            } else {
                offer.classList.remove('disliked');
                dislikes.splice(index, 1);
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
        const selected = popup.querySelector('input[name="resume"]:checked');
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

function buildParamsURL() {
    const data = new FormData(searchForm);
    const refine = [
        ...likes.map(offer_id => ({ type: 'like', offer_id })),
        ...dislikes.map(offer_id => ({ type: 'dislike', offer_id })),
    ];
    data.append('refine', JSON.stringify(refine));
    data.append('salary', JSON.stringify(salarySlider.noUiSlider.get()));
    const query = new URLSearchParams(data); 
    return query
}

async function search(paramsURL) {
    resultsContainer.innerHTML = '';
    resultsContainer.classList.add('waiting');
    const response = await fetch(`/ajax/search_offer?${paramsURL}"`);
    const content = await response.json();
    renderResults(content);
    resultsContainer.classList.remove('waiting');
}



// Attach resume
attachResumeButton.addEventListener('click', async () => {
    const response = await fetch('/ajax/attach_resume_popup');
    const html = await response.text();
    // Create popup
    const popup = createPopup(html);
    view.appendChild(popup);
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
    console.log(paramsURL.toString());
    search(paramsURL);
});
searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
});