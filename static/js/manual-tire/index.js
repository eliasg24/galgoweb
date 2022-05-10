import { search } from './buscador.js';
import { profundidad } from './profundidad.js';

document.addEventListener('DOMContentLoaded', (e) => {
  confirmAlert();
  handlePresion();
  profundidad();
  // handleForms();

  // validateInputList('#llanta', 'llanta');
  // validateInputList('#producto', 'producto');
  // noDoubleValues();

  // manualObserver('data-check-id');
  // vehiculoManual('data-vehiculo-item');

  // search('#vehiculo-search', '#vehiculo-observaciones', '.search-item');
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

    let container = document.querySelector(`[data-container-id="${id}"]`);
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
      let container = document.querySelector(
        `[data-container-id="${observation.getAttribute(item)}"]`
      );
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

const noDoubleValues = (inputName = '') => {
  const elements = document.querySelectorAll(`input[name="${inputName}"]`);
  let values = [];

  elements.forEach((value) => {
    values.push(value.value);
  });

  const tempArray = [...values].sort();
  let duplicate = [];

  for (let i = 0; i < tempArray.length; i++) {
    if (tempArray[i + 1] === tempArray[i]) {
      duplicate.push(tempArray[i]);
    }
  }

  if (duplicate.length > 0) {
    const alert = Swal.fire({
      title: 'Error',
      text: 'No puede haber elementos duplicados',
      icon: 'error',
      backdrop: true,
      allowOutsideClick: false,
      allowEscapeKey: false,
    });
    return true; // Si hay elementos duplicados retorna true para la validación con sweetalert
  }

  return false; // Si no hay elementos duplicados
};

const handleForms = () => {
  const forms = document.querySelectorAll('form');

  forms[0].addEventListener('submit', (e) => {
    if (forms[0].querySelector('input').value === '') {
      e.preventDefault();
      alert('El campo no puede estar vacío');
      forms[0].querySelector('input').focus();
    }
  });
};

// ! Empty profs

const emptyProfs = () => {
  const inputs = document.querySelectorAll('.form__prof');
  let counter = 0;

  inputs.forEach((el) => {
    let inputCounter = 0;
    el.querySelectorAll('input').forEach((input) => {
      if (input.value !== '') {
        inputCounter++;
      }
    });
    if (inputCounter >= 1) {
      counter++;
    }
  });

  console.log(counter);

  if (counter >= inputs.length) {
    return true;
  }

  return false;
};

const confirmAlert = () => {
  const form = document.getElementById('tire-form');

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const duplicate = noDoubleValues('llanta');
    const empty = emptyProfs();

    if (duplicate) return;

    if (!empty) {
      const alert = Swal.fire({
        title: 'Error',
        text: 'Todas las llantas al menos tienen que tener una profundidad',
        icon: 'error',
        backdrop: true,
        allowOutsideClick: false,
        allowEscapeKey: false,
      });
      return;
    }

    const alert = Swal.fire({
      title: 'Confirmación',
      text: '¿Seguro que desea continuar?',
      icon: 'question',
      confirmButtonText: 'Si',
      backdrop: true,
      showDenyButton: true,
      allowOutsideClick: false,
      allowEscapeKey: false,
    }).then((res) => {
      res.value && form.submit();
    });
  });
};
