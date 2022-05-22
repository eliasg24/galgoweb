export const form = () => {
  document.addEventListener('submit', async (e) => {
    if (e.target.matches('#form')) {
      e.preventDefault();

      const productos = document.querySelectorAll('[name="productos"]');
      const cantidades = document.querySelectorAll('[name="cantidad"]');
      
      let valuesP = [];
      let valuesC = [];
      
      productos.forEach(value => {
        valuesP.push(value.value);
      })

      cantidades.forEach(c => {
        valuesC.push(c.value);
      })

      try {
        const resp = await fetch(
          `${window.location.origin}/api/generacionllantanueva`,
          {
            method: 'POST',
            headers: {
              'Content-type': 'application/json;charset=utf-8',
            },
            body: JSON.stringify({
              usuario: e.target.usuario.value,
              destino: e.target.destino.value,
              producto: [valuesP],
              cantidad: valuesC,
              fecha: e.target.date.value
            })
          }
        );

        if (!resp.ok) throw new Error(resp.statusText || 'Algo ocurrió mal');

        window.location.replace(`${ window.location.origin }/vistaordenes`)
      } catch (error) { 
        console.error(error);
      }
    }
  });
};
