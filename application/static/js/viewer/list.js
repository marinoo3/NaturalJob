const section = document.querySelector('section#viewer');
const salarySlider = section.querySelector('#salary-slider');








noUiSlider.create(salarySlider, {
    start: [0, 100],
    connect: true,
    range: {
        'min': 0,
        'max': 100
    }
});