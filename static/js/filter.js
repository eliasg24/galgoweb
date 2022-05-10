document.addEventListener('DOMContentLoaded', (e) => {
  searchFilters('#search-ubicacion', '#menu-ubicacion', '.search-item');
  searchFilters('#search-clase', '#menu-clase', '.search-item');
  searchFilters('#search-flota', '#menu-flota', '.search-item');
  searchFilters('#search-sucursal', '#menu-sucursal', '.search-item');
  searchFilters('#search-company', '#menu-company', '.search-item');
  searchFilters('#search-app', '#menu-app', '.search-item');
  searchFilters('#search-eje', '#menu-eje', '.search-item');
  searchFilters('#search-vehiculo', '#menu-vehiculo', '.search-item');
  searchFilters('#search-pos', '#menu-pos', '.search-item');
  searchFilters('#search-producto', '#menu-producto', '.search-item');
});

/**
 * It takes an input, a container, and a selector, and then adds an event listener to the input that
 * filters the selector based on the input's value.
 * @param [input] - The input field that will be used to search.
 * @param [container] - the parent element of the elements you want to filter
 * @param [selector] - The input element that will be used to filter the list.
 */

const searchFilters = (input = '', container = '', selector = '') => {
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
