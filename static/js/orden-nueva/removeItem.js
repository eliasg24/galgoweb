export const removeItem = () => {
  document.addEventListener('click', (e) => {
    if ( e.target.matches('.delete') ) {
      document.getElementById(e.target.getAttribute('data-id')).remove();
    }
  })
}