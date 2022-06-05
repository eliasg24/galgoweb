const multiForm = document.querySelector('.context__form'),
  formSteps = [...document.querySelectorAll('.context__wrapper')];

let currentStep = formSteps.findIndex((step) =>
  step.classList.contains('active')
);

if (currentStep < 0) {
  currentStep = 0;

  formSteps[currentStep].classList.add('active');
}

multiForm.addEventListener('click', (e) => {
  const showCurrentStep = () => {
    formSteps.forEach((step, index) => {
      step.classList.toggle('active', index === currentStep);
    });
  };

  let increment;

  if (e.target.matches('.btn-next')) {
    increment = 1;
  } else if (e.target.matches('.btn-prev')) {
    increment = -1;
  }

  if (increment == null) return;

  const inputs = [...formSteps[currentStep].querySelectorAll('input, select')];
  let allValid = inputs.every((input) => input.reportValidity());

  // Checa si al menos hay un input checkbox
  const haveChecked = inputs.some((input) => input.type === 'checkbox');

  // Verifica si al menos un checkbox esta seleccionado
  if (haveChecked) {
    if (inputs.some((input) => input.checked)) {
      document
        .querySelectorAll('.context__error')
        .forEach((alert) => alert.remove());
        
      allValid = true;
    } else {
      document
        .querySelectorAll('.context__error')
        .forEach((alert) => alert.remove());

      document
        .querySelectorAll('.context__wrapper')
        [currentStep].insertAdjacentHTML(
          'beforeend',
          '<div class="context__error">Debe seleccionar al menos una opción</div>'
        );
      allValid = false;
    }
  }

  if (allValid) {
    currentStep += increment;
    showCurrentStep();
  }
});
