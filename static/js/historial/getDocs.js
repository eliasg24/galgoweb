let page = 1;

export const getDocs = async (url) => {
  const template = document.getElementById('order-template').content,
    fragment = document.createDocumentFragment();

  const container = document.getElementById('created-orders');

  container.innerHTML = `
  <tr>
    <td colspan="4">
      <div class="icon-spinner2"></div>
    </td>
  </tr>
  `;

  try {
    const resp = await fetch(url);
    const json = await resp.json();

    if (!resp.ok)
      throw new Error(
        `Error ${resp.status}: ${resp.statusText || 'Algo salió mal'}`
      );

    if (json.pagination.next === null) {
      document.querySelector('.next').style.display = 'none';
    } else {
      document.querySelector('.next').style.display = 'block';
    }

    if (json.pagination.prev === null) {
      document.querySelector('.prev').style.display = 'none';
    } else {
      document.querySelector('.prev').style.display = 'block';
    }

    json.datos.forEach((item) => {
      template.querySelector('a').href = `/redireccionOrden/${item.id}`;
      template.querySelector('.folio').textContent = item.folio;
      template.querySelector('.fecha').textContent = item.fecha;
      template.querySelector('.accion').textContent = item.status;

      let clone = document.importNode(template, true);
      fragment.appendChild(clone);
    });

    container.innerHTML = '';
    container.appendChild(fragment);
  } catch (error) {
    container.innerHTML = '';
    container.innerHTML = `
      <tr>
        <td colspan="4">
          ${error}
        </td>
      </tr>
    `;
  }
};

document.addEventListener('click', (e) => {
  if (e.target.matches('.next')) {
    page += 1;
    getDocs(
      `${window.location.origin}/api/historicodeorden?page=${page}&size=10`
    );
  }

  if (e.target.matches('.prev')) {
    page -= 1;
    getDocs(
      `${window.location.origin}/api/historicodeorden?page=${page}&size=10`
    );
  }
});
