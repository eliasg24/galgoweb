(() => {
  const tires = document.querySelectorAll('.tire');

  tires.forEach((tire) => {
    tire.addEventListener('click', (e) => {
      const id: string = tire.dataset.id;

      document.querySelector(`[data-modal="${id}"]`)?.classList.add('active');

      document.addEventListener('click', (e) => {
        if (e.target.matches('.close-modal')) {
          document
            .querySelector(`[data-modal="${id}"]`)
            ?.classList.remove('active');
        }
      });
    });
  });
})();

(() => {
  interface Form {
    balancear: string;
    inflar: string;
    llantaId: string;
    nuevaLlanta: string;
    razon: string;
    reparar: string;
    rotar: string;
    stock: string;
  }

  interface Event {}

  const saveData: Form[] = [];

  document.addEventListener('submit', (e) => {
    if (e.target.matches('#taller-form')) return;

    e.preventDefault();
    const form: HTMLFormElement = e.target as HTMLFormElement;
    const data: Form = Object.fromEntries(new FormData(form));

    form
      .querySelectorAll('input, select, .btn-submit')
      .forEach((input) => input.setAttribute('disabled', ''));

    saveData.push(data);

    const formHidden = document.getElementById(
      'data-taller'
    ) as unknown as HTMLInputElement;
    formHidden.value = JSON.stringify(saveData);
  });

  document.addEventListener('change', (e) => {
    if (e.target.name === 'rotar') {
      switch (e.target.value) {
        case 'no':
          document
            .querySelectorAll(`[data-rotar-id="${e.target.dataset.radioid}"]`)
            .forEach((label) => (label.style.display = 'none'));
          break;

        case 'mismo':
          document.querySelectorAll(
            `[data-rotar-id="${e.target.dataset.radioid}"]`
          )[0].style.display = 'none';
          document.querySelectorAll(
            `[data-rotar-id="${e.target.dataset.radioid}"]`
          )[1].style.display = 'block';
          break;

        case 'otro':
          document
            .querySelectorAll(`[data-rotar-id="${e.target.dataset.radioid}"]`)
            .forEach((label) => (label.style.display = 'block'));
          break;

        default:
          break;
      }
    }
  });

  document.addEventListener('click', (e) => {
    if (e.target.dataset.nav) {
      if (e.target.value === 'desmontaje') {
        document
          .querySelectorAll('[data-nav]')
          .forEach((item) => item.classList.remove('active'));

        e.target.classList.add('active');
        document
          .querySelectorAll(`[data-view]`)
          .forEach((view) => (view.style.display = 'none'));

        document.querySelectorAll(
          `[data-view="${e.target.dataset.nav}"]`
        )[1].style.display = 'block';
      } else {
        document
          .querySelectorAll('[data-nav]')
          .forEach((item) => item.classList.remove('active'));

        e.target.classList.add('active');
        document
          .querySelectorAll(`[data-view]`)
          .forEach((view) => (view.style.display = 'none'));
          
        document.querySelectorAll(
          `[data-view="${e.target.dataset.nav}"]`
        )[0].style.display = 'block';
      }
    }
  });
})();
