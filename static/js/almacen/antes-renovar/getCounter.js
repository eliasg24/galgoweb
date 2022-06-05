export const getCounter = () => {
  const counter = document.querySelector('.cart__counter');

  fetch(`${window.location.origin}/api/carritocountapi?inventario=Antes%20de%20Renovar`)
    .then(res => res.json())
    .then((data) => {

      if (data.numm_llantas === 0) {
        counter.style.display = 'none'
      } else {
        counter.style.display = 'flex'
      }

      if (data.numm_llantas >= 99) {
        counter.textContent = '+99';
      }

      counter.innerHTML = data.numm_llantas;
    })
    .catch(err => console.error(err))
}