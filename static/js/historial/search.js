export const search = () => {
  const historialList = document.getElementById('created-orders'),
    template = document.getElementById('order-template').content,
    fragment = document.createDocumentFragment();

  let page = 1,
    size = 10;

  document.addEventListener('submit', (e) => {
    if (e.target.matches('form')) {
      e.preventDefault();

      const formData = new FormData(e.target),
        data = Object.fromEntries(formData),
        { folio, start_date, end_date } = data;

      let url = `${location.origin}/api/historicodeorden?size=${size}&page=${page}${ folio && `&folio=${folio}` }${ start_date && `&start_date=${start_date}` }${ end_date && `&end_date=${end_date}` }`
      console.log(url)

      fetch(url)
        .then(resp => resp.ok ? resp.json() : Promise.reject(resp))
        .then(json => {
          if (json.datos.length === 0) {
            historialList.innerHTML = `
              <tr>
                <td colSpan="4">
                  No hay resultados :(
                </td>
              </tr>
            `;
            return;
          }

          if (json.pagination.next === null) {
            document.querySelector('.next').disabled = true;
          } else {
            document.querySelector('.next').disabled = false;
          }
      
          if (json.pagination.prev === null) {
            document.querySelector('.prev').disabled = true;
          } else {
            document.querySelector('.prev').disabled = false;
          }
      
          json.datos.forEach((item) => {
            template.querySelector('a').href = `/redireccionOrden/${item.id}`;
            template.querySelector('.folio').textContent = item.folio;
            template.querySelector('.fecha').textContent = item.fecha;
            template.querySelector('.accion').textContent = item.status;
      
            let clone = document.importNode(template, true);
            fragment.appendChild(clone);
          });
      
          historialList.innerHTML = '';
          historialList.appendChild(fragment);
        })
        .catch(error => console.error(error));
    }
  });
};


