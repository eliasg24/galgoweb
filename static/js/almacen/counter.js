export const counter = () => {
  const cards = document.querySelectorAll('.tire-input');
  let counter = 0;

  cards.forEach((item) => {
    item.querySelector('input').addEventListener('input', (e) => {
      if (e.target.checked) {
        counter++;
      } else {
        counter--;
      }

      document.querySelector('h1').textContent = counter;

      if (counter > 0) {
        document
          .querySelectorAll('button[disabled]')
          .forEach((item) => item.removeAttribute('disabled'));
      } else {
        document
          .querySelectorAll('button[type="submit"]')
          .forEach((item) => item.setAttribute('disabled', 'disabled'));
      }
    });
  });
};
