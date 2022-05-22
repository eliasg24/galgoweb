export const getVehicles = async () => {
  const template = document.getElementById('card-template').content,
    fragment = document.createDocumentFragment();
  const container = document.querySelector('.vehicle__list');

  try {
    const resp = await fetch(`${ window.location.origin }/api/vehicle_list/`);
    const json = await resp.json();
    const { vehiculos } = json;

    if (!resp.ok) throw new Error(`Error ${resp.status}: ${resp.statusText}`);

    vehiculos.forEach((item) => {
      template.querySelector('.card__economic').textContent =
        item.numero_economico;

      // Set ID
      template.querySelector('a').href = `/${item.id}`;

      // Set date
      template.querySelector('.card__date').textContent =
        item.ultima_fecha_de_inflado || 'Sin fecha';

      // Set icon
      if (item.color !== 'rojo') {
        template.getElementById('icon').classList.remove('icon-cross');
        template.getElementById('icon').classList.add('icon-checkmark');
      } else {
        template.getElementById('icon').classList.remove('icon-checkmark');
        template.getElementById('icon').classList.add('icon-cross');
      }

      // Set color

      if (item.color === 'verde') {
        template
          .querySelector('.status')
          .classList.remove('suspicious', 'yellow', 'bad');
        template.querySelector('.status').classList.add('ok');
      }

      if (item.color === 'rojo') {
        template
          .querySelector('.status')
          .classList.remove('suspicious', 'yellow', 'ok');
        template.querySelector('.status').classList.add('bad');
      }
      if (item.color === 'amarillo') {
        template
          .querySelector('.status')
          .classList.remove('suspicious', 'bad', 'ok');
        template.querySelector('.status').classList.add('yellow');
      }

      if (item.color === 'sospechoso') {
        template
          .querySelector('.status')
          .classList.remove('yellow', 'bad', 'ok');
        template.querySelector('.status').classList.add('suspicious');
      }

      let clone = document.importNode(template, true);

      fragment.appendChild(clone);
    });

    container.innerHTML = ''
    container.appendChild(fragment);
  } catch (error) {
    console.error(error);
  }
};