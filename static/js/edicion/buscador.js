export const search = (input = '', container = '', selector = '') => {
  document.addEventListener('keyup', (e) => {
    if (e.target.matches(input)) {
      if (e.key === 'Esc') e.target.value = '';

      document
        .querySelectorAll(`${container} > ${selector}`)
        .forEach((item) =>
          item.textContent.toLowerCase().includes(e.target.value.toLowerCase())
            ? item.classList.remove('filter')
            : item.classList.add('filter')
        );
    }
  });
};
