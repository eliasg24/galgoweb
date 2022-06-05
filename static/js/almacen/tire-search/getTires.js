const template = document.getElementById('tire-template').content,
  fragment = document.createDocumentFragment(),
  container = document.querySelector('.search__list'),
  loader = document.getElementById('loader');
  
  document.addEventListener('input', async (e) => {
    if (e.target.matches('#search')) {
    loader.style.display = 'block';

    try {
      const resp = await fetch(
        `${location.origin}/api/tiresearch?eco=${e.target.value.toLowerCase()}&size=3`
      );
      const { pagination, result } = await resp.json();

      if (!resp.ok) throw new Error('Algo salió mal');

      if (pagination.next === null) {
        document.querySelector('.btn-next').disabled = true;
      } else {
        document.querySelector('.btn-next').disabled = false;
      }
  
      if (pagination.prev === null) {
        document.querySelector('.btn-prev').disabled = true;
      } else {
        document.querySelector('.btn-prev').disabled = false;
      }

      result.forEach(tire => {
        template.querySelector('.economico').textContent = tire.numero_economico;
        template.querySelector('.producto').textContent = tire.producto__producto;
        template.querySelector('.fecha').textContent = tire.fecha_de_entrada_inventario;

        let clone = document.importNode(template, true);

        fragment.appendChild(clone);
      });

      loader.style.display = 'none';
      container.innerHTML = '';
      container.appendChild(fragment);
    
    } catch (error) {
      console.error(error);
    }
  }
});
