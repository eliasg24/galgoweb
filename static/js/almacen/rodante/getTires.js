import { getCounter } from './getCounter.js';

const template = document.getElementById('card-template').content;
const container = document.querySelector('.cards__container');
const fragment = document.createDocumentFragment();
const loader = document.querySelector('.icon-spinner2');
const productList = document.querySelector('select[name="producto"]');

let page = 1,
  size = 24;

const getTires = async (querys = '') => {
  const origin = window.location.origin,
    api = `${origin}/api`,
    tires = `${api}/tiresearch`,
    apiSearch = `${tires}${
      querys || '?'
    }&inventario=Rodante&size=${size}&page=${page}`;

  loader.style.display = 'block';

  try {
    const resp = await fetch(apiSearch);
    const { result, pagination, productos } = await resp.json();

    if (!resp.ok) throw new Error('Algo sucedió mal');

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

    if (result.length === 0) {
      loader.style.display = 'none';
      container.innerHTML = `
        <div>No se encontro ningun item</div>
      `
      return;
    }

    result.forEach((item) => {
      template.querySelector('a').href = `/tireDetail/${item.id}`; // Poner el id del rodante

      template.querySelector('.economic').textContent = item.numero_economico;
      template.querySelector('.economic').textContent = item.numero_economico;

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

      template.querySelector('.profundidad').textContent =
        item.min_profundidad || 'Sin profundidad';
      template.querySelector('.product').textContent = item.producto__producto;
      template.querySelector('.date').textContent =
        item.fecha_de_entrada_inventario;

      template.querySelector('.add-item').dataset.id = item.id;
      // ? El inventario se pone manual según el inventario
      template.querySelector('.add-item').dataset.inventario = 'Rodante';

      let clone = document.importNode(template, true);
      fragment.appendChild(clone);
    });

    let option = `<option value="">Selecciona un producto</option>`;
    productos.forEach((producto) => {
      option += `<option value="${producto.product}">${producto.product}</option>`;

      productList.innerHTML = option;
    });

    let params = new URLSearchParams(window.location.search);

    if (params.has('producto')) {
      productList.querySelector(`option[value="${params.get('producto')}"]`).selected = true;
    }

    container.innerHTML = '';
    loader.style.display = 'none';
    container.appendChild(fragment);
    
    document.querySelectorAll('.add-item').forEach(button => {
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
                document.querySelector('.alert__success').classList.remove('active'),
              2000
            );
          })
          .catch((err) => console.error(err));
      });
    })

  } catch (error) {
    console.error(error);
  }

};

document.addEventListener('click', (e) => {
  if (e.target.matches('.next')) {
    page += 1;
    getTires(window.location.search);
  }

  if (e.target.matches('.prev')) {
    page -= 1;
    getTires(window.location.search);
  }
});

export default getTires;
