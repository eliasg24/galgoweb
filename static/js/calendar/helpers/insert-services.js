export const insertServices = (servicios, body = document.documentElement) => {
  servicios.forEach((servicio) => {
    const serviceContainer = document.createElement('div');
    serviceContainer.classList.add('service-done');
  
    /* It's converting the object into an array of arrays. */
    const list = Object.entries(servicio);
    /* It's filtering the array of arrays, removing the empty values. */
    let servicesDone = list.filter((item = []) => {
      if (!item.some((item) => item === false || item === null)) {
        return item;
      }
    });
  
    servicesDone.forEach((serviceDone = []) => {
      let taskDone = serviceDone[0];
      switch (taskDone) {
        case 'llanta_cambio':
          taskDone = 'Llanta destino';
          break;
  
        case 'rotar_mismo':
          taskDone = 'Rotación en dentro del vehículo';
          break;
  
        case 'rotar_otro':
          taskDone = 'Rotación a otro vehículo';
          break;
  
        default:
          taskDone =
            taskDone.slice(0, 1).toUpperCase() +
            taskDone.slice(1, taskDone.length).replace('_', ' ');
          break;
      }
  
      serviceContainer.innerHTML += `
        <div>
          <span class="service-title">
            ${taskDone}: 
          </span>
          <span class="service-desc">
            ${serviceDone[1] === true ? 'Hecho' : serviceDone[1]}
          </span>
        </div>
      `;
    });
  
    body.appendChild(serviceContainer);
  });
};
