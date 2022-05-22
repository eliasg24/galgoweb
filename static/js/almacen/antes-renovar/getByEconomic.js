export const getByEconomic = () => {
  const template = document.getElementById('card-template').content;
  const container = document.querySelector('.cards__container');
  const fragment = document.createDocumentFragment();

  document.addEventListener('keypress', (e) => {
    if (e.key === 'Esc') e.target.value = '';
  });

  document.addEventListener('input', async (e) => {
    if (e.target.matches('#economico')) {
      const query = e.target.value.toLowerCase();

      container.innerHTML = `
        <span class="icon-spinner2"></span>
      `;
      try {
        const resp = await fetch(
          `${window.location.origin}/api/tiresearch?inventario=Antes%20de%20Renovar&eco=${query}`
        );
        const { result } = await resp.json();

        if (!resp.ok)
          throw new Error({
            status: resp.status,
            statusMessage: resp.statusText,
          });

        if (result.length === 0) {
          container.innerHTML = `
            <div>
              No hay resultados :(
            </div>
          `;
          return;
        } else {
          result.forEach((item) => {
            template.querySelector('a').href = `/tireDetail/${item.id}`; // Poner el id del rodante
            template.querySelector('input').id = item.id;
            template.querySelector('input').value = item.id;
            template.querySelector('label').setAttribute('for', item.id);

            template.querySelector('.economic').textContent =
              item.numero_economico;
            template.querySelector('.profundidad').textContent =
              item.min_profundidad || 'Sin profundidad';
            template.querySelector('.product').textContent =
              item.producto__producto;
            template.querySelector('.date').textContent =
              item.fecha_de_entrada_inventario;

            let clone = document.importNode(template, true);
            fragment.appendChild(clone);
          });

          container.innerHTML = '';
          container.appendChild(fragment);
        }
      } catch (error) {
        console.error(`Error ${error.status}: ${error.statusMessage}`);
      }
    }
  });
};