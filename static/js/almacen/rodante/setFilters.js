const template = document.getElementById('card-template').content;
const container = document.querySelector('.cards__container');
const fragment = document.createDocumentFragment();
const loader = document.querySelector('.icon-spinner2');

const getFilters = async (querys = '') => {
  const origin = window.location.origin,
    api = `${origin}/api`,
    tires = `${api}/tiresearch`,
    apiSearch = `${tires}${
      querys || '?'
    }&inventario=Rodante`;

  loader.style.display = 'block';

  try {
    const resp = await fetch(apiSearch);
    const { result } = await resp.json();

    if (!resp.ok) throw new Error('Algo sucedió mal');

    result.forEach((item) => {
      template.querySelector('a').href = `/tireDetail/${item.id}`; // Poner el id del rodante
      template.querySelector('input').id = item.id;
      template.querySelector('input').value = item.id;
      template.querySelector('label').setAttribute('for', item.id);

      template.querySelector('.economic').textContent = item.numero_economico;
      template.querySelector('.profundidad').textContent =
        item.min_profundidad || 'Sin profundidad';
      template.querySelector('.product').textContent = item.producto__producto;
      template.querySelector('.date').textContent =
        item.fecha_de_entrada_inventario;

      let clone = document.importNode(template, true);
      fragment.appendChild(clone);
    });

    container.innerHTML = '';
    loader.style.display = 'none';
    container.appendChild(fragment);
  } catch (error) {
    console.error(error);
  }
};

export const setFilters = () => {
  const params = new URLSearchParams(window.location.search);

  document.addEventListener('input', (e) => {
    if (e.target.matches('input[type="checkbox"]')) return;
    if (e.target.matches('input')) {
      let value = e.target.value.toLowerCase();

      params.set(e.target.name, value);

      if (value == '') {
        params.delete(e.target.name);
        let newPath = window.location.pathname + params.toString();
        history.pushState(null, '', newPath);
        getFilters(window.location.search);
      }

      let newPath = window.location.pathname + '?' + params.toString();

      history.pushState(null, '', newPath);
      getFilters(window.location.search);
    }
  });
};

// Mantener los valores que tiene el usuario
export const setValues = () => {
  const inputs = document.querySelectorAll('input');
  const selects = document.querySelectorAll('select');
  let params = new URLSearchParams(window.location.search);

  inputs.forEach((input) => {
    input.value = params.get(input.name);
  });

  selects.forEach((select) => {
    select.value = params.get(select.name);
  });
};