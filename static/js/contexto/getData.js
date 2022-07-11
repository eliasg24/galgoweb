document.addEventListener('DOMContentLoaded', (e) => {
  getCompany(API_URL);
});

const DOMAIN = window.location.origin,
  API_URL = `${DOMAIN}/api/contextoapi`;

const form = document.querySelector('.context__form'),
  container = [...document.querySelectorAll('.context__wrapper')],
  buttons = document.querySelectorAll('.btn-next');

const template = document.getElementById('check-temp').content,
  fragment = document.createDocumentFragment();

const getCompany = async (url) => {
  const select = document.getElementById('company');

  if (!select) return;

  try {
    const resp = await fetch(url);
    const { companias } = await resp.json();

    if (!resp.ok) throw new Error('Error en la petición');

    companias.forEach((item) => {
      const option = document.createElement('option');
      option.value = item.compania;
      option.text = item.compania;
      select.appendChild(option);
    });
  } catch (error) {
    console.error(error);
  }
};

buttons[0]?.addEventListener('click', async (e) => {
  const formData = new FormData(form);
  const data = {
    company: formData.get('company'),
  };

  try {
    const resp = await fetch(`${API_URL}?compania_select=${data.company}`);
    const json = await resp.json();

    if (!resp.ok) throw new Error('Error en la petición');

    json.ubicaciones.forEach((item) => {
      template.querySelector('label').textContent = item.ubicacion;
      template.querySelector('label').setAttribute('for', item.ubicacion);
      template.querySelector('input').value = item.ubicacion;
      template.querySelector('input').id = item.ubicacion;
      template.querySelector('input').name = 'sucursal';

      let clone = document.importNode(template, true);

      fragment.appendChild(clone);
    });

    container[1].querySelector('.context__options').innerHTML = '';
    container[1].querySelector('.context__options').appendChild(fragment);
  } catch (error) {
    console.error(error);
  }
});

buttons[1]?.addEventListener('click', async (e) => {
  const formData = new FormData(form);
  let checks = [];
  let checked = container[1].querySelectorAll('input[name="sucursal"]:checked');

  checked.forEach((value) => {
    checks.push(value.value);
  });

  const data = {
    company: formData.get('company'),
    sucursal: checks,
  };

  try {
    const resp = await fetch(
      `${API_URL}?compania_select=${data.company}&ubicaciones_select=${data.sucursal}`
    );
    const json = await resp.json();

    if (!resp.ok) throw new Error('Error en la petición');

    json.aplicaciones.forEach((item) => {
      let div = document.createElement('div');
      div.textContent = '';
      div.innerHTML += `<h3>${item.ubicacion}</h3>`;
      item.aplicaciones.forEach((app) => {
        template.querySelector('label').textContent = app.aplicacion;
        template.querySelector('label').setAttribute('for', app.aplicacion);
        template.querySelector('input').value = app.aplicacion;
        template.querySelector('input').id = app.aplicacion;
        template.querySelector('input').name = 'aplicacion';

        let clone = document.importNode(template, true);

        div.appendChild(clone);
      });
      fragment.appendChild(div);
    });

    container[2].querySelector('.context__options').innerHTML = '';
    container[2].querySelector('.context__options').appendChild(fragment);
  } catch (error) {
    console.error(error);
  }
});

buttons[1]?.addEventListener('click', async (e) => {
  const formData = new FormData(form);

  const data = {
    company: formData.get('company'),
  };

  try {
    const resp = await fetch(`${API_URL}?compania_select=${data.company}`);
    const json = await resp.json();

    if (!resp.ok) throw new Error('Error en la petición');

    json.talleres.forEach((item) => {
      template.querySelector('label').textContent = item.taller;
      template.querySelector('label').setAttribute('for', item.taller);
      template.querySelector('input').value = item.taller;
      template.querySelector('input').id = item.taller;
      template.querySelector('input').name = 'taller';

      let clone = document.importNode(template, true);

      fragment.appendChild(clone);
    });

    container[3].querySelector('.context__options').innerHTML = '';
    container[3].querySelector('.context__options').appendChild(fragment);
  } catch (error) {
    console.error(error);
  }
});
