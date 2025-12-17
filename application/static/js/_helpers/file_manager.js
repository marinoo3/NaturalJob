export function createPopup(html) {
    // Create popup
    const popup = document.createElement('div');
    popup.classList.add('popup');
    popup.innerHTML = html;
    // Any input change
    const form = popup.querySelector('form');
    form.addEventListener('input', () => {
        let allFilled = true;
        form.querySelectorAll('input').forEach(input => {
            if (input.value.trim() == '') {
                allFilled = false;
            }
        });

        if (allFilled) {
            form.querySelector('button.main-button').classList.remove('disabled');
        } else {
            form.querySelector('button.main-button').classList.add('disabled');
        }
    });
    // Close popup
    popup.addEventListener('click', (event) => {
        if (event.target === popup || event.target.closest('button.cancel')) {
            popup.remove();
        }
    });

    return { popup, form };
}