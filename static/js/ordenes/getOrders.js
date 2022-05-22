export const getOrders = async () => {
  const template = document.getElementById('order-template').content,
        fragment = document.createDocumentFragment();

  const wait = document.getElementById('pending-orders');
  const created = document.getElementById('created-orders');

  try {
    const resp = await fetch(`${ window.location.origin }/api/ordersearch`);
    const { en_espera, historial } = await resp.json();

    if (!resp.ok) throw new Error(`${resp.status}: ${ resp.statusText || 'Algo salió mal' }`);

    if( en_espera.length === 0 ) {
      wait.innerHTML = `
        <tr>
          <td colspan="3">No hay ordenes en espera</td>
        </tr>
      `;
    } else {

      wait.innerHTML = '';

      en_espera.forEach(item => {
        template.querySelector('.folio').textContent = item.folio;
        template.querySelector('.fecha').textContent = item.fecha;
        template.querySelector('a').href = `/ordenLlanta/${item.id}`;

        let clone = document.importNode(template, true);

        fragment.appendChild(clone);
      })

      wait.appendChild(fragment);
    }

    if( historial.length === 0 ) {
      created.innerHTML = `
        <tr>
          <td colspan="3">No hay ordenes creadas</td>
        </tr>
      `;
    } else {

      created.innerHTML = '';

      historial.forEach(item => {
        template.querySelector('.folio').textContent = item.folio;
        template.querySelector('.fecha').textContent = item.fecha;
        template.querySelector('a').href = `/ordenLlanta/${item.id}`;

        let clone = document.importNode(template, true);

        fragment.appendChild(clone);
      })

      created.appendChild(fragment);
    }

  } catch (error) {
    
  }
  
}