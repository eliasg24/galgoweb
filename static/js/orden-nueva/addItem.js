export const addItem = () => {
  const container = document.querySelector('.list__inputs');
  let i = 0;

  document.addEventListener('click', async (e) => {

    if (e.target.matches('.add')) {

      let div = document.createElement('div');

      i++;

      div.id = i;
      div.innerHTML += `
          <div class = "product__item">
            <div class= "label__group"> 
              <label class="label__item">
                Producto
                <select class="select__item" name="productos" required>
                  <option value="" selected></option>
                </select>
              </label>
              <label class="label__item">
                Cantidad
                <input class="input__item" type="number" name="cantidad" required />
              </label>
            </div>
            <button type="button" class="delete" data-id="${i}">Eliminar</button>
          </div>
        `;
      container.append(div);

      try {
        const resp = await fetch(`${window.location.origin}/api/ordenllantanueva`);
        const json = await resp.json();
        const { productos } = json;
    
        if (!resp.ok) throw new Error(resp.statusText || 'Algo salió mal');
    
        document.querySelectorAll('[name="productos"]').forEach(item => {
          item.innerHTML = '' 
          item.innerHTML = `
            <option value="" selected></option>
          ` 
        })
        productos.forEach((producto) => {
          document.querySelectorAll('[name="productos"]').forEach(item => {
            item.innerHTML += `
              <option value="${ producto.producto }">${ producto.producto }</option>
            `
          })
        });
    
      } catch (error) {
        console.error(error);
      }
    }
  });
};
