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
      try {
        const resp = await fetch(
          `${ window.location.origin }/api/tiresearch?inventario=Rodante&eco=${query}&limit=16`
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
            template.querySelector('.economic').textContent =
              item.numero_economico;
            template.querySelector('.product').textContent =
              item.producto__producto;
            console.log(typeof item.fecha_de_entrada_inventario);
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
