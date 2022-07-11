import { getCounter } from './getCounter.js';
import getTires from './getData.js';

const template = document.getElementById('card-template').content;
const container = document.querySelector('.cards__container');
const fragment = document.createDocumentFragment();
const loader = document.querySelector('.icon-spinner2');
const productList = document.querySelector('select[name="producto"]');

let pageSearch = 1;

export const getFilters = async (querys = '') => {
  const origin = window.location.origin,
    api = `${origin}/api`,
    tires = `${api}/tiresearch`,
    apiSearch = `${tires}${
      querys || '?'
    }&inventario=Servicio&size=24&page=${pageSearch}`;

  loader.style.display = 'block';

  try {
    const resp = await fetch(apiSearch);
    const { result, pagination, productos } = await resp.json();

    if (!resp.ok) throw new Error('Algo sucedió mal');

    if (result.length === 0) {
      loader.style.display = 'none';
      container.innerHTML = `
        <div>No se encontro ningun item</div>
      `;
      return;
    }

    if (pagination.next === null) {
      document.querySelector('.next').style.display = 'none';
    } else {
      document.querySelector('.next').style.display = 'block';
    }

    if (pagination.prev === null) {
      document.querySelector('.prev').style.display = 'none';
    } else {
      document.querySelector('.prev').style.display = 'block';
    }

    result.forEach((item) => {
      template.querySelector('a').href = `/tireDetail/${item.id}`; // Poner el id del nueva

      if (item.color === 'good') {
        template
          .querySelector('.tire__status')
          .classList.remove('bad', 'yellow');
        template.querySelector('.tire__status').classList.add('good');
      } else if (item.color === 'bad') {
        template
          .querySelector('.tire__status')
          .classList.remove('good', 'yellow');
        template.querySelector('.tire__status').classList.add('bad');
      } else if (item.color === 'yellow') {
        template.querySelector('.tire__status').classList.remove('good', 'bad');
        template.querySelector('.tire__status').classList.add('yellow');
      }

      template.querySelector('.economic').textContent = item.numero_economico;
      template.querySelector('.profundidad').textContent =
        item.min_profundidad || 'Sin profundidad';
      template.querySelector('.product').textContent = item.producto__producto;
      template.querySelector('.date').textContent =
        item.fecha_de_entrada_inventario;

      template.querySelector('.add-item').dataset.id = item.id;
      // ? El inventario se pone manual según el inventario
      template.querySelector('.add-item').dataset.inventario = 'Servicio';

      let clone = document.importNode(template, true);
      fragment.appendChild(clone);
    });

    productList.innerHTML = '';
    productos.forEach((producto) => {
      let option = `<option value="">Selecciona un producto</option>`;
      productos.forEach((producto) => {
        option += `<option value="${producto.product}">${producto.product}</option>`;

        productList.innerHTML = option;
      });
    });

    let params = new URLSearchParams(window.location.search);

    if (params.has('producto')) {
      productList.querySelector(`option[value="${params.get('producto')}"]`).selected = true;
    }

    container.innerHTML = '';
    loader.style.display = 'none';
    container.appendChild(fragment);

    document.querySelectorAll('.add-item').forEach((button) => {
      button.addEventListener('click', (e) => {
        const id = button.dataset.id;
        const inventario = button.dataset.inventario;

        fetch(
          `${window.location.origin}/api/carritollantasapi?llanta=${id}&inventario=${inventario}`
        )
          .then((res) => (res.ok ? res.json() : Promise.reject(res)))
          .then((res) => {
            getTires(window.location.search);
            getCounter();
            document.querySelector('.alert__success').classList.add('active');

            setTimeout(
              () =>
                document
                  .querySelector('.alert__success')
                  .classList.remove('active'),
              2000
            );
          })
          .catch((err) => console.error(err));
      });
    });
  } catch (error) {
    console.error(error);
  }
};

export const setFilters = () => {
  const params = new URLSearchParams(window.location.search);

  document.addEventListener('input', (e) => {
    if (e.target.name === 'producto') {
      params.set('producto', e.target.value);

      let newPath = window.location.pathname + '?' + params.toString();

      history.pushState(null, '', newPath);
      getFilters(window.location.search);
    }

    if (e.target.matches('input') && e.target.name !== 'producto') {
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

export const removeFilters = () => {
  const inputs = document.querySelectorAll('input, select');
  let params = new URLSearchParams(window.location.search);

  document.addEventListener('click', (e) => {
    if (e.target.matches('#remove-filters')) {      
      inputs.forEach((input) => {
        input.value = '';
        params.delete(input.name);
      });

      let newPath = window.location.pathname + '?' + params.toString();
      history.pushState(null, '', newPath);
      getFilters(window.location.search);
    }
  });
};
