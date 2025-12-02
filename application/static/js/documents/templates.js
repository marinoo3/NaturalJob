const section = document.querySelector('#documents');
const categoryContainers = section.querySelectorAll('.category');
let templates = {};



function renderTemplate(category) {
    const documents = category.querySelector('.docs');
    documents.innerHTML = '';
    const key = documents.dataset.category;
    if (templates[key]) {
        templates[key].forEach(template => {
            const li = document.createElement('li');
            li.dataset.templateId = template.id;
            li.innerHTML = template.html;
            documents.appendChild(li);
        });
    } else {
        documents.innerHTML = '<p class="third">Aucun documents</p>';
        category.classList.add('folded');
    }

}

async function loadTemplates() {
    const response = await fetch('ajax/get_templates');
    templates = await response.json();
    
    categoryContainers.forEach(category => {
        renderTemplate(category);
    });
}



// Foldable categories
categoryContainers.forEach(category => {
    const title = category.querySelector('.foldable');
    title.addEventListener('click', () => {
        category.classList.toggle('folded');
    });
});

// Load and render templates
loadTemplates();