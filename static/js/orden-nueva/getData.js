export const getData = async () => {
  const destino = document.getElementById('destino');
  const user = document.getElementById('user');

  try {
    const resp = await fetch(`/api/ordenllantanueva`);
    const json = await resp.json();
    const { talleres, usuario } = json;

    if (!resp.ok) throw new Error(resp.statusText || 'Algo salió mal');

    talleres.forEach((taller) => {
      destino.innerHTML += `
        <option value="${taller.id}">${taller.nombre}</option>
      `;
    });

    user.value = usuario;

  } catch (error) {
    console.error(error);
  }
};
