import { search } from './buscador.js';
import { profundidad } from './profundidad.js';

document.addEventListener('DOMContentLoaded', (e) => {
  handlePresion();
  profundidad();
  // handleForms();

  // validateInputList('#llanta', 'llanta');
  validateInputList('#producto', 'producto');
  // noDoubleValues();

  manualObserver('data-check-id');
  vehiculoManual('data-vehiculo-item');

  search('#vehiculo-search', '#vehiculo-observaciones', '.search-item');
});

const handlePresion = () => {
  const input = document.querySelector('input[name="presion"]');
  const tag = document.querySelector('.tire__top span');

  input.addEventListener('input', (e) => {
    let minPresion = parseFloat(input.getAttribute('data-presion-min'));
    let maxPresion = parseFloat(input.getAttribute('data-presion-max'));

    tag.textContent = input.value;

    if (tag.textContent.length === 0) {
      tag.textContent = 0;
    }

    if (
      parseFloat(tag.textContent) >= minPresion &&
      parseFloat(tag.textContent) <= maxPresion
    ) {
      tag.parentElement.classList.remove('bad');
      tag.parentElement.classList.add('good');
    } else {
      tag.parentElement.classList.remove('good');
      tag.parentElement.classList.add('bad');
    }

    let container = document.querySelector(`.observations__container`);
    if (parseFloat(tag.textContent) > maxPresion) {
      container
        .querySelector('[data-icon-presion="Alta presion"]')
        .classList.add('visible');
      container
        .querySelector('[data-icon-presion="Baja presión"]')
        .classList.remove('visible');
    } else if (parseFloat(tag.textContent) < minPresion) {
      container
        .querySelector('[data-icon-presion="Alta presion"]')
        .classList.remove('visible');
      container
        .querySelector('[data-icon-presion="Baja presión"]')
        .classList.add('visible');
    } else if (
      parseFloat(tag.textContent) >= minPresion &&
      parseFloat(tag.textContent) <= maxPresion
    ) {
      container
        .querySelector('[data-icon-presion="Alta presion"]')
        .classList.remove('visible');
      container
        .querySelector('[data-icon-presion="Baja presión"]')
        .classList.remove('visible');
    }
  });
};

const vehiculoManual = (item = '') => {
  const observations = document.querySelectorAll(`[${item}]`);

  observations.forEach((observation) => {
    observation.addEventListener('input', () => {
      let container = document.querySelector('.observations__container');
      if (observation.checked) {
        container
          .querySelector(`[data-icon-type="${observation.value}"]`)
          .classList.add('visible');
      } else {
        container
          .querySelector(`[data-icon-type="${observation.value}"]`)
          .classList.remove('visible');
      }
    });
  });
};

const manualObserver = (item = '') => {
  const observations = document.querySelectorAll(`[${item}]`);

  observations.forEach((observation) => {
    observation.addEventListener('input', () => {
      let container = document.querySelector(`.observations__container`);
      if (observation.checked) {
        container
          .querySelector(`[data-icon-type="${observation.value}"]`)
          .classList.add('visible');
      } else {
        container
          .querySelector(`[data-icon-type="${observation.value}"]`)
          .classList.remove('visible');
      }
    });
  });
};

const validateInputList = (listItem = '', inputName = '') => {
  const list = document.querySelector(listItem)?.options;

  // Si ya se inspecciono
  if (!list) return;

  let listValues = [];

  for (let i = 0; i < list.length; i++) {
    listValues.push(list[i].value);
  }

  // Traemos todos los inputs para modificar el numero econimico
  const inputs = document.querySelectorAll(`input[name="${inputName}"]`);

  // Le asignamos el evento al escribir
  inputs.forEach((input) => {
    let isValid = false;

    input.addEventListener('keyup', (e) => {
      if (listValues.indexOf(input.value) > -1) {
        input.parentNode
          .querySelector('.alert__error')
          .classList.remove('active');
        input.parentNode
          .querySelector('.alert__warn')
          .classList.remove('active');
        document.querySelector('.btn-info').classList.remove('disabled');
        isValid = true;
      } else {
        input.parentNode.querySelector('.alert__error').classList.add('active');
        input.focus();
        document.querySelector('.btn-info').classList.add('disabled');
        isValid = false;
      }

      if (input.value === '') {
        input.parentNode.querySelector('.alert__warn').classList.add('active');
        document.querySelector('.btn-info').classList.add('disabled');
        isValid = false;
      }
    });

    input.addEventListener('keypress', (e) => {
      if (!isValid) {
        if (e.key === 'Enter') e.preventDefault();
      }
    });
  });
};