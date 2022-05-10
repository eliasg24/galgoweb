document.addEventListener('DOMContentLoaded', (e) => {
  handleOptions();

  dropdown('d-clase', 'menu-clase');
  dropdown('d-ubicacion', 'menu-ubicacion');
  dropdown('d-app', 'menu-app');

  handleSelectAll({ container: 'menu-clase', selectAll: 'all-clase' });
  handleSelectAll({ container: 'menu-ubicacion', selectAll: 'all-ubicacion' });
  handleSelectAll({ container: 'menu-app', selectAll: 'all-app' });

  handleCheckbox();
});

const handleOptions = () => {
  const dashList = ['inspeccion', 'vida', 'desecho', 'cpk'];
  const cards = document.querySelectorAll('.card');

  cards.forEach((card) => {
    card.addEventListener('click', (e) => {
      cards.forEach((card) => card.classList.remove('active'));

      card.classList.add('active');

      if (dashList.includes(card.id)) {
        document
          .querySelectorAll('[data-view]')
          .forEach((view) => view.classList.remove('on'));
        document.querySelector(`[data-view="${card.id}"]`).classList.add('on');
      }
    });
  });
};

const handleSelectAll = ({ container = '', selectAll = 'all' }) => {
  const selector = document.querySelector(`#${container} #${selectAll}`);
  const checkboxs = document.querySelectorAll(
    `#${container} input[type="checkbox"]`
  );

  selector.addEventListener('change', (e) => {
    selector.checked
      ? checkboxs.forEach((check) => (check.checked = true))
      : checkboxs.forEach((check) => (check.checked = false));
  });

  checkboxs.forEach((item) => {
    item.addEventListener('change', (e) => {
      let notAll = false;

      checkboxs.forEach((item) => {
        if (!item.checked) notAll = true;
        if (notAll) selector.checked = false;
      });
    });
  });
};

const handleCheckbox = () => {
  const inputs = document.querySelectorAll('.input-check');
  const form = document.querySelector('.form-head');
  const dates = document.querySelectorAll('input[data-fecha]');

  dates.forEach((input) => {
    input.addEventListener('input', (e) => {
      if (!dates[0].value) {
        alert('Selecciona una fecha inicial');
        dates[0].focus();
        return;
      }
      if (dates[0].value && dates[1].value) {
        if (dates[0].value > dates[1].value) {
          alert('La fecha inicial no puede ser mayor a la fecha final');
          dates[0].focus();
          return;
        }

        form.submit();
      }
    });
  });
};

const dropdown = (button = '', menu = '') => {
  const dropBtn = document.getElementById(button);
  const dropMenu = document.getElementById(menu);

  dropBtn.addEventListener('click', (e) => {
    e.preventDefault();
    dropMenu.classList.toggle('active');
    if (dropMenu.classList.contains('active')) {
      dropBtn.querySelector('.indicator').classList.add('active');
    } else {
      dropBtn.querySelector('.indicator').classList.remove('active');
    }
  });
};
