document.addEventListener('DOMContentLoaded', (e) => {
  searchTire();
  filterModal();
});

const filterModal = () => {
  const activeBtn = document.getElementById('filter-btn');
  const closeBtn = document.getElementById('close-modal');
  const filter = document.querySelector('.filter__container');

  activeBtn.addEventListener('click', (e) => {
    filter.classList.add('active');
  });

  closeBtn.addEventListener('click', (e) => {
    filter.classList.remove('active');
  });
};

const searchTire = () => {
  const tires = document.querySelectorAll('.card__wrapper #tire-name');

  document.addEventListener('keyup', (e) => {
    if (e.target.matches('input[type="search"]')) {
      if (e.key === 'Esc') e.target.value = '';

      tires.forEach((item) =>
        item.textContent
          .replace('#', '')
          .toLowerCase()
          .includes(e.target.value.toLowerCase())
          ? item.parentElement.parentElement.parentElement.classList.remove('filter')
          : item.parentElement.parentElement.parentElement.classList.add('filter')
      );
    }
  });
};
