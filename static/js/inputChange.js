document.addEventListener('DOMContentLoaded', (e) => {
  handleInputs();
});

const handleInputs = () => {
  const inputs = document.querySelectorAll('input');
  const form = document.querySelector('form');

  inputs.forEach((input) => {
    input.addEventListener('keyup', (e) => {
      const submitBtn = document.querySelector('.btn-success');
      if (input.value === '') submitBtn.classList.add('disabled');
      submitBtn.classList.remove('disabled');
    });
  });
};
