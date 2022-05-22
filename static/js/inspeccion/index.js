import { search } from './buscador.js';
import { profundidad } from './profundidad.js';

document.addEventListener('DOMContentLoaded', (e) => {
  onSelectTire();
  profundidad();
  // handleForms();
  handleTire();

  // validateInputList('#llanta', 'llanta');
  validateInputList('#producto', 'producto');
  // noDoubleValues();

  manualObserver('data-check-id');
  vehiculoManual('data-vehiculo-item');

  search('#vehiculo-search', '#vehiculo-observaciones', '.search-item');
  dual();
});

const diferenciaDual = (duales = document.documentElement) => {
  let tires = duales.querySelectorAll('.tire');

  tires.forEach((tire) => {
    const input = document.querySelector(
      `input[data-input-id="${tire.getAttribute('data-tire-id')}"]`
    );

    input.addEventListener('input', (e) => {
      let presion1 = tires[0].querySelector('[data-tag-id]').textContent;
      let presion2 = tires[1].querySelector('[data-tag-id]').textContent;

      if (presion1 === 0 && presion2 === 0) return;

      presion1 = parseFloat(presion1);
      presion2 = parseFloat(presion2);

      let container1 = tires[0].getAttribute('data-tire-id');
      let container2 = tires[1].getAttribute('data-tire-id');

      let ids = [container1, container2];

      console.log(presion1, presion2);

      let porcentajeDif1 = (presion1 - presion2) / presion1;
      let porcentajeDif2 = (presion2 - presion1) / presion2;

      if (
        porcentajeDif1 > 0.1 ||
        porcentajeDif1 < 0 ||
        porcentajeDif2 > 0.1 ||
        porcentajeDif2 < 0
      ) {
        ids.forEach((id) => {
          let content = document.querySelector(`[data-container-id="${id}"]`);
          content
            .querySelector(
              '[data-icon-dual="Diferencia de presión entre los duales"]'
            )
            .classList.add('visible');
        });
      } else {
        ids.forEach((id) => {
          let content = document.querySelector(`[data-container-id="${id}"]`);
          content
            .querySelector(
              '[data-icon-dual="Diferencia de presión entre los duales"]'
            )
            .classList.remove('visible');
        });
      }
    });
  });
};

const dual = () => {
  const duales = document.querySelectorAll('.double-tire');
  const mmDiferencia = document
    .querySelector('.double-tire')
    .getAttribute('data-mm-dif');

  duales.forEach((dual) => {
    diferenciaDual(dual);
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

    input.addEventListener('input', (e) => {
      if (input.value === '') {
        input.parentElement
          .querySelector('.alert__warn')
          .classList.add('active');
        document.querySelector('.btn-info').classList.add('disabled');
        isValid = false;
        return;
      }

      if (listValues.indexOf(input.value) > -1) {
        input.parentElement
          .querySelector('.alert__error')
          .classList.remove('active');
        input.parentElement
          .querySelector('.alert__warn')
          .classList.remove('active');
        document.querySelector('.btn-info').classList.remove('disabled');
        isValid = true;
      } else {
        input.parentElement
          .querySelector('.alert__error')
          .classList.add('active');
        input.focus();
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

const handleTire = () => {
  const buttons = document.querySelectorAll('.tire');
  const items = document.querySelectorAll('.form__wrapper');

  buttons.forEach((button) => {
    button.addEventListener('click', (e) => {
      const id = button.getAttribute('data-tire-id');

      items.forEach((item) => {
        const itemId = item.getAttribute('data-item-id');
        if (id === itemId) {
          items.forEach((item) => item.classList.remove('select'));

          item.classList.add('select');
        }
      });
    });
  });
};

const onSelectTire = () => {
  const tires = document.querySelectorAll('.tire');
  const hidden = document.querySelector("input[type='hidden']");

  tires.forEach((tire) => {
    tire.addEventListener('click', (e) => {
      tires.forEach((tire) => tire.classList.remove('select'));

      hidden.value = tire.getAttribute('id');

      tire.classList.add('select');
    });
  });
};
