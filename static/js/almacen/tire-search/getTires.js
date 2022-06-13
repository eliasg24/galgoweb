const template = document.getElementById('tire-template').content,
  fragment = document.createDocumentFragment(),
  container = document.querySelector('.search__list'),
  loader = document.getElementById('loader');

let currentPage = 1,
  size = 3;

const input = document.getElementById('search');

const getTires = async (query) => {
  const origin = window.location.origin,
    api = `${origin}/api`,
    tires = `${api}/tiresearchalmacen`,
    apiSearch = `${ tires }${ query || '?' }&size=${size}&page=${currentPage}`;

  loader.style.display = 'block';    
  try {
    const resp = await fetch(apiSearch);
    const { pagination, result } = await resp.json();

    if (!resp.ok) throw new Error('Algo salió mal');

    if (result.length === 0) {
      loader.style.display = 'none';
      container.innerHTML = `
        <p>No hay resultados</p>
      `
      return;
    }

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

    result.forEach((tire) => {
      template.querySelector('a').href = `${tire.url}?eco=${ tire.numero_economico }`;
      template.querySelector('.economico').textContent =
        tire.numero_economico;
      template.querySelector('.producto').textContent =
        tire.producto__producto;
      template.querySelector('.fecha').textContent =
        tire.fecha_de_entrada_inventario;

      let clone = document.importNode(template, true);

      fragment.appendChild(clone);
    });

    loader.style.display = 'none';
    container.innerHTML = '';
    container.appendChild(fragment);
  } catch (error) {
    console.error(error);
  }
};

document.addEventListener('input', async (e) => {
  if (e.target.matches('#search')) {
    const params = new URLSearchParams(window.location.search);
    params.set(e.target.name, e.target.value.toLowerCase());

    if (e.target.value == '') {
      params.delete(e.target.name);
      let newPath = window.location.pathname + params.toString();
      history.pushState(null, '', newPath);
      getTires(window.location.search);
    }

    let newPath = window.location.pathname + '?' + params.toString();

    history.pushState(null, '', newPath);

    console.log(location.search)

    getTires(location.search);
  }
});

document.addEventListener('click', (e) => {
  if (e.target.matches('.btn-next')) {
    currentPage += 1;
    getTires(location.search);
  }

  if (e.target.matches('.btn-prev')) {
    currentPage -= 1;
    getTires(location.search);
  }
});
