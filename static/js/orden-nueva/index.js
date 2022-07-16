import { form } from './form.js';
import { getData } from './getData.js';

document.addEventListener('DOMContentLoaded', (e) => {
  getData();
  form();
});

/* Form */

const container = document.querySelector('.list__inputs .absolute');
let options = '';

const getProducts = async () => {
  try {
    const resp = await fetch('/api/ordenllantanueva');
    const { productos } = await resp.json();

    const selectFirstRow = document.querySelector('.order-item select');
    productos.forEach((producto) => {
      options += `
        <option value="${producto.producto}" >${producto.producto}</option>
      `;
    });
    selectFirstRow.innerHTML += options;
  } catch (error) {
    console.error(error);
  }
};

getProducts();

const addItem = () => {
  const rowId = Math.floor(Math.random() * 1000000);

  container.insertAdjacentHTML(
    'beforeend',
    `
  <div class="order-item" id="${rowId}">
    <select name="producto" required>
      <option value="">Seleccione un producto...</option>
      ${options}
    </select>

    <input type="number" name="cantidad" placeholder="Cantidad" required>

    <button type="button" class="btn delete" data-id="${rowId}">
      Eliminar
    </button>
  </div>
  `
  );
};

const deleteItem = (id) => {
  document.getElementById(id).remove();
};

document.addEventListener('click', (e) => {
  if (e.target.matches('.add')) {
    addItem();
  }

  if (e.target.matches('.delete')) {
    const currentRows = document.querySelectorAll('.order-item');

    if (currentRows.length <= 1) {
      Swal.fire(
        'Error al eliminar item',
        'Debe haber al menos un item para enviar',
        'info'
      );
      return;
    }

    deleteItem(e.target.dataset.id);
  }
});

/* Get date */

const date = document.getElementById('date');
let dateNow = new Date();

dateNow.toISOString().split('T')[0];

const offset = dateNow.getTimezoneOffset();
dateNow = new Date(dateNow.getTime() - offset * 60 * 1000);
date.value = dateNow.toISOString().split('T')[0];
