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

const validaciones = (
  target,
  left,
  center,
  right,
  tag,
  puntoRetiro,
  container
) => {
  const leftValue = parseFloat(left.value);
  const centerValue = parseFloat(center.value);
  const rightValue = parseFloat(right.value);

  if (target === left) {
    // ! Si es solo la izquierda
    if (center.value === '' && right.value === '') {
      // ! Si la izquierda deja de tener valor
      if (left.value === '') {
        tag.parentElement.classList.remove('bad', 'yellow', 'good');
        tag.textContent = '-';
        colorProf(tag, puntoRetiro, container);
        return;
      }

      tag.textContent = leftValue;
      colorProf(tag, puntoRetiro, container);
    }
    colorProf(tag, puntoRetiro, container);
  }

  if (target === center) {
    if (left.value === '' && right.value === '') {
      if (center.value === '') {
        tag.parentElement.classList.remove('bad', 'yellow', 'good');
        tag.textContent = '-';
        colorProf(tag, puntoRetiro, container);
        return;
      }
      tag.textContent = centerValue;

      colorProf(tag, puntoRetiro, container);
      return;
    }
    colorProf(tag, puntoRetiro, container);
  }

  if (target === right) {
    if (left.value === '' && center.value === '') {
      if (right.value === '') {
        tag.parentElement.classList.remove('bad', 'yellow', 'good');
        tag.textContent = '-';
        colorProf(tag, puntoRetiro, container);
        return;
      }

      tag.textContent = rightValue;

      colorProf(tag, puntoRetiro, container);
      return;
    }
    colorProf(tag, puntoRetiro, container);
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
      return;
    }

    // * Evaluación de los 3 ejes

    // ! Si no tiene los tres valores no aplican los desgastes siguientes

    if (left.value === '' || center.value === '' || right.value === '') {
      container
        .querySelectorAll('[data-icon-desgaste]')
        .forEach((icon) => icon.classList.remove('visible'));
      return;
    }

    if (left.value !== '' && center.value !== '' && right.value !== '') {
      const minValue = Math.min(...values);

      tag.textContent = minValue;

      colorProf(tag, puntoRetiro, container);

      if (
        (rightValue < leftValue && rightValue < centerValue) ||
        (rightValue < leftValue && rightValue === centerValue)
      ) {
        container
          .querySelectorAll('[data-icon-desgaste]')
          .forEach((icon) => icon.classList.remove('visible'));
        container
          .querySelector(
            '[data-icon-desgaste="Desgaste inclinado a la derecha"]'
          )
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
          .querySelector(
            '[data-icon-desgaste="Desgaste inclinado a la izquierda"]'
          )
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
    }
  }
};

export const profundidad = () => {
  const profundidades = document.querySelectorAll('[data-profundidad-id]');

  profundidades.forEach((profundidad) => {
    const inputs = profundidad.querySelectorAll('input');

    const [left, center, right] = inputs;

    let tag = document.querySelector(`.tire__bottom span`);
    let puntoRetiro = parseFloat(profundidad.getAttribute('data-punto-retiro'));
    let container = document.querySelector(`.observations__container`);

    document.addEventListener('input', ({ target }) =>
      validaciones(target, left, center, right, tag, puntoRetiro, container)
    );
  });
};
