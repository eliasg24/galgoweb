document.addEventListener('DOMContentLoaded', () => search('#vehiculo', '.vehicle-card__img', 'h3'));

const search = (input = '', container = '', selector = '') => {
  document.addEventListener('keyup', (e) => {
    if (e.target.matches(input)) {
      if (e.key === 'Esc') e.target.value = '';

      document
        .querySelectorAll(`${container} > ${selector}`)
        .forEach((item) =>
          item.textContent.toLowerCase().includes(e.target.value.toLowerCase())
            ? item.parentElement.parentElement.parentElement.classList.remove('filter')
            : item.parentElement.parentElement.parentElement.classList.add('filter')
        );
    }
  });
};
