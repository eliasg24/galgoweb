const colorProf = (tag, puntoRetiro, container) => {
  if (parseFloat(tag.textContent) <= puntoRetiro) {
    tag.parentElement.classList.remove('yellow', 'bad', 'good');
    tag.parentElement.classList.add('bad');
    container
      .querySelector('[data-icon-profundidad="Baja profundidad"]')
      .classList.add('visible');
  } else if (parseFloat(tag.textContent) >= puntoRetiro) {
    container
      .querySelector('[data-icon-profundidad="Baja profundidad"]')
      .classList.remove('visible');
  }

  if (
    parseFloat(tag.textContent) >= puntoRetiro + 0.01 &&
    parseFloat(tag.textContent) <= puntoRetiro + 1
  ) {
    tag.parentElement.classList.remove('bad', 'good', 'yellow');
    tag.parentElement.classList.add('yellow');
  } else if (parseFloat(tag.textContent) > puntoRetiro + 1) {
    tag.parentElement.classList.remove('yellow', 'bad', 'good');
    tag.parentElement.classList.add('good');
  }

  if (parseFloat(tag.textContent) === puntoRetiro + 0.6) {
    container
      .querySelector('[data-icon-retiro="En punto de retiro"]')
      .classList.add('visible');
  } else {
    container
      .querySelector('[data-icon-retiro="En punto de retiro"]')
      .classList.remove('visible');
  }
};

const desdualizacion = (tire = document.documentElement, mm) => {
  const shaft = tire.parentElement?.parentElement?.parentElement;

  // Validando si es un dual o no
  if (!shaft.classList.contains('double-tire')) return;

  const dual = shaft?.querySelectorAll('.tire');

  const ids = [
    dual[0].getAttribute('data-tire-id'),
    dual[1].getAttribute('data-tire-id'),
  ];
  const tire1 = parseFloat(
    dual[0].querySelector('[data-prof-tag]').textContent
  );
  const tire2 = parseFloat(
    dual[1].querySelector('[data-prof-tag]').textContent
  );

  if (tire1 - tire2 >= mm || tire2 - tire1 >= mm) {
    ids.forEach((id) => {
      let content = document.querySelector(`[data-container-id="${id}"]`);
      content
        .querySelector('[data-icon-dual="Desdualización"]')
        .classList.add('visible');
    });
  } else {
    ids.forEach((id) => {
      let content = document.querySelector(`[data-container-id="${id}"]`);

      content
        .querySelector('[data-icon-dual="Desdualización"]')
        .classList.remove('visible');
    });
  }
};

const tresProfundidades = ({
  rightValue,
  leftValue,
  centerValue,
  container,
  tag,
  puntoRetiro,
}) => {
  if (
    (rightValue < leftValue && rightValue < centerValue) ||
    (rightValue < leftValue && rightValue === centerValue)
  ) {
    container
      .querySelectorAll('[data-icon-desgaste]')
      .forEach((icon) => icon.classList.remove('visible'));
    container
      .querySelector('[data-icon-desgaste="Desgaste inclinado a la derecha"]')
      .classList.add('visible');
    colorProf(tag, puntoRetiro, container);
  }

  if (
    (leftValue < centerValue && leftValue < rightValue) ||
    (leftValue < rightValue && leftValue === centerValue)
  ) {
    container
      .querySelectorAll('[data-icon-desgaste]')
      .forEach((icon) => icon.classList.remove('visible'));
    container
      .querySelector('[data-icon-desgaste="Desgaste inclinado a la izquierda"]')
      .classList.add('visible');
    colorProf(tag, puntoRetiro, container);
  }

  if (leftValue < centerValue && centerValue > rightValue) {
    container
      .querySelectorAll('[data-icon-desgaste]')
      .forEach((icon) => icon.classList.remove('visible'));
    container
      .querySelector('[data-icon-desgaste="Desgaste  costilla interna"]')
      .classList.add('visible');
    colorProf(tag, puntoRetiro, container);
  }

  if (leftValue > centerValue && centerValue < rightValue) {
    container
      .querySelectorAll('[data-icon-desgaste]')
      .forEach((icon) => icon.classList.remove('visible'));
    container
      .querySelector('[data-icon-desgaste="Desgaste alta presión"]')
      .classList.add('visible');
    colorProf(tag, puntoRetiro, container);
  }

  if (leftValue === centerValue && leftValue === rightValue) {
    container
      .querySelectorAll('[data-icon-desgaste]')
      .forEach((icon) => icon.classList.remove('visible'));
  }
};

const validaciones = (tireObject, target) => {
  const {
    left,
    center,
    right,
    tag,
    puntoRetiro,
    container,
    max,
    min,
    desgasteCompany,
    anteriorLlanta,
  } = tireObject;
  const leftValue = parseFloat(left.value);
  const centerValue = parseFloat(center.value);
  const rightValue = parseFloat(right.value);
  const mm = parseFloat(
    document.querySelector('.double-tire')?.getAttribute('data-mm-dif')
  );

  switch (target) {
    case left:
      // ! Si es solo la izquierda
      if (center.value === '' && right.value === '') {
        // ! Si la izquierda deja de tener valor
        if (left.value === '') {
          tag.parentElement.classList.remove('bad', 'yellow', 'good');
          tag.textContent = '-';
          desdualizacion(tag, mm);
          colorProf(tag, puntoRetiro, container);
          return;
        }

        tag.textContent = leftValue;
        desdualizacion(tag, mm);
        colorProf(tag, puntoRetiro, container);
      }
      colorProf(tag, puntoRetiro, container);
      break;

    case center:
      if (left.value === '' && right.value === '') {
        if (center.value === '') {
          tag.parentElement.classList.remove('bad', 'yellow', 'good');
          tag.textContent = '-';
          desdualizacion(tag, mm);
          colorProf(tag, puntoRetiro, container);
          return;
        }
        tag.textContent = centerValue;

        colorProf(tag, puntoRetiro, container);
        desdualizacion(tag, mm);
        return;
      }
      colorProf(tag, puntoRetiro, container);
      break;

    case right:
      if (left.value === '' && center.value === '') {
        if (right.value === '') {
          tag.parentElement.classList.remove('bad', 'yellow', 'good');
          tag.textContent = '-';
          colorProf(tag, puntoRetiro, container);
          desdualizacion(tag, mm);
          return;
        }

        tag.textContent = rightValue;

        colorProf(tag, puntoRetiro, container);
        desdualizacion(tag, mm);
        return;
      }
      colorProf(tag, puntoRetiro, container);
      break;

    default:
      break;
  }

  if (target === left || target === center || target === right) {
    const values = [
      parseFloat(left.value),
      parseFloat(center.value),
      parseFloat(right.value),
    ];

    if (left.value === '' && center.value !== '' && right.value !== '') {
      container
        .querySelectorAll('[data-icon-desgaste]')
        .forEach((icon) => icon.classList.remove('visible'));
      const newValue = values.filter((value) => !isNaN(value));

      const minValue = Math.min(...newValue);

      tag.textContent = minValue;
      colorProf(tag, puntoRetiro, container);
      desdualizacion(tag, mm);
      return;
    }

    if (left.value !== '' && center.value !== '' && right.value === '') {
      container
        .querySelectorAll('[data-icon-desgaste]')
        .forEach((icon) => icon.classList.remove('visible'));
      const newValue = values.filter((value) => !isNaN(value));

      const minValue = Math.min(...newValue);

      tag.textContent = minValue;
      colorProf(tag, puntoRetiro, container);
      desdualizacion(tag, mm);
      return;
    }

    if (left.value !== '' && center.value === '' && right.value !== '') {
      container
        .querySelectorAll('[data-icon-desgaste]')
        .forEach((icon) => icon.classList.remove('visible'));
      const newValue = values.filter((value) => !isNaN(value));

      const minValue = Math.min(...newValue);

      tag.textContent = minValue;
      colorProf(tag, puntoRetiro, container);
      desdualizacion(tag, mm);
      return;
    }

    if (left.value !== '' && center.value === '' && right.value === '') {
      container
        .querySelectorAll('[data-icon-desgaste]')
        .forEach((icon) => icon.classList.remove('visible'));
      const newValue = values.filter((value) => !isNaN(value));

      const minValue = Math.min(...newValue);

      tag.textContent = minValue;
      colorProf(tag, puntoRetiro, container);
      desdualizacion(tag, mm);
      return;
    }

    if (left.value === '' && center.value !== '' && right.value === '') {
      container
        .querySelectorAll('[data-icon-desgaste]')
        .forEach((icon) => icon.classList.remove('visible'));
      const newValue = values.filter((value) => !isNaN(value));

      const minValue = Math.min(...newValue);

      tag.textContent = minValue;
      colorProf(tag, puntoRetiro, container);
      desdualizacion(tag, mm);
      return;
    }

    if (left.value === '' && center.value === '' && right.value !== '') {
      container
        .querySelectorAll('[data-icon-desgaste]')
        .forEach((icon) => icon.classList.remove('visible'));
      const newValue = values.filter((value) => !isNaN(value));

      const minValue = Math.min(...newValue);

      tag.textContent = minValue;
      colorProf(tag, puntoRetiro, container);
      desdualizacion(tag, mm);
      return;
    }

    // ! Si no tiene los tres valores no aplican los desgastes siguientes

    if (left.value === '' || center.value === '' || right.value === '') {
      container
        .querySelectorAll('[data-icon-desgaste]')
        .forEach((icon) => icon.classList.remove('visible'));
      return;
    }

    // * Evaluación de los 3 ejes

    if (left.value !== '' && center.value !== '' && right.value !== '') {
      const minValue = Math.min(...values);
      const maxValue = Math.max(...values);
      let dif,
        companyFloat = parseFloat(desgasteCompany),
        anteriorFloat;

      tag.textContent = minValue;

      colorProf(tag, puntoRetiro, container);
      desdualizacion(tag, mm);

      dif = maxValue - minValue;

      console.log({ dif, companyFloat });

      if (dif > companyFloat) {
        if (anteriorLlanta === 'None') {
          tresProfundidades({
            rightValue,
            leftValue,
            centerValue,
            container,
            tag,
            puntoRetiro,
          });
        } else {
          return;
        }

        if (!isNaN(anteriorLlanta)) {
          anteriorFloat = parseFloat(anteriorLlanta);

          if (dif > anteriorFloat) {
            tresProfundidades({
              rightValue,
              leftValue,
              centerValue,
              container,
              tag,
              puntoRetiro,
            });
          } else {
            return;
          }
        } else {
          return;
        }
      } else {
        // tresProfundidades({
        //   rightValue,
        //   leftValue,
        //   centerValue,
        //   container,
        //   tag,
        //   puntoRetiro,
        // });
        return;
      }
    }
  }
};

export const profundidad = () => {
  const profundidades = document.querySelectorAll('[data-profundidad-id]');

  profundidades.forEach((profundidad) => {
    const id = profundidad.getAttribute('data-profundidad-id');
    const inputs = profundidad.querySelectorAll('input');

    const [left, center, right] = inputs;

    let tag = document.querySelector(`[data-prof-tag="profundidad-${id}"]`);
    let puntoRetiro = parseFloat(profundidad.getAttribute('data-punto-retiro'));
    let max = profundidad.getAttribute('data-max-profundidad-act');
    let min = profundidad.getAttribute('data-min-profundidad-act');
    let desgasteCompany = profundidad.getAttribute(
      'data-mm-de-desgaste-compania'
    );

    let anteriorLlanta = profundidad.getAttribute(
      'data-desgaste-anterior-llanta'
    );

    let container = document.querySelector(`[data-container-id="${id}"]`);

    const tire = {
      left,
      center,
      right,
      tag,
      puntoRetiro,
      container,
      max,
      min,
      desgasteCompany,
      anteriorLlanta,
    };

    document.addEventListener('input', ({ target }) =>
      validaciones(tire, target)
    );
  });
};
