document.addEventListener('DOMContentLoaded', (e) => {
  handleMenu();
});

const handleMenu = () => {
  const btn = document.querySelector('.btn-menu');

  if (localStorage.getItem('menu')) {
    if (window.matchMedia('(min-width: 1024px)').matches)
      document.querySelector('.menu').classList.add('active');
  }

  btn.addEventListener('click', (e) => {
    document.querySelector('.menu').classList.toggle('active');

    document.querySelector('.menu').classList.contains('active')
      ? localStorage.setItem('menu', 'active')
      : localStorage.removeItem('menu');
  });
};
