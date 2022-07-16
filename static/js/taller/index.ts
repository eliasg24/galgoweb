interface Servicio {
  almacen_desmontaje: string;
  balancear: string;
  costado: string;
  id_servicio: string;
  inflar: string;
  llantaId: string;
  llantaOrigen: string;
  nuevaLlanta: string;
  otroVehiculo: string;
  razon: string;
  reparar: string;
  rotar: string;
  stock: string;
  taller_desmontaje: string;
  tipoServicio: string;
  valvula: string;
  numero_economico: string;
  posicion: string;
}

// * Modal

(() => {
  const tires = document.querySelectorAll('.tire');

  tires.forEach((tire) => {
    tire.addEventListener('click', (e) => {
      let tireTs = tire as unknown as HTMLInputElement;
      const id: string | undefined = tireTs.dataset.id;

      const modal = document.querySelector(`[data-modal="${id}"]`);
      modal?.classList.add('active');

      document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        if (target.matches('.close-modal')) {
          modal?.classList.remove('active');
        }
      });
    });
  });
})();

// * Manejo de información

(() => {
  let saveData: any[] = [];

  /*
   * Methods
   */

  const eventList = document.querySelector('.tire-list') as HTMLElement;
  const formHidden = document.getElementById(
    'data-taller'
  ) as unknown as HTMLInputElement;

  const addEvent = (servicio: Servicio) => {
    eventList.insertAdjacentHTML(
      'afterbegin',
      `
    <div class="tire-item" data-servicioid="${servicio.id_servicio}" >
        <span class="delete" data-delete="${
          servicio.id_servicio
        }" data-tireown="${servicio.llantaId}">
            &times;
          </span>
          <div class="service__img">
            <span class="icon-llanta-outline"></span>
          </div>
          <div class="service__body">
          ${
            servicio.tipoServicio === 'desmontaje'
              ? `
              <h3 class="service__title">
              Desmontaje
            </h3>
          `
              : ''
          }
              ${servicio.inflar !== '' ? `
              <h3 class="service__title">
                Inflado
              </h3>
              ` : ''}
              ${servicio.balancear !== '' ? `
              <h3 class="service__title">
              Balanceo
            </h3>
              ` : ''}
              ${servicio.reparar !== '' ? `
              <h3 class="service__title">
                Reparación
              </h3>
              ` : ''}
              ${servicio.valvula !== '' ? `
              <h3 class="service__title">
                Reparación de valvula
              </h3>
              ` : ''}
              ${servicio.costado !== '' ? `
              <h3 class="service__title">
                Reparación de costado
              </h3>
              ` : ''}
            <p><strong>Llanta:</strong> ${servicio.numero_economico}</p>
            <p><strong>Posición:</strong> ${servicio.posicion}</p>
            ${
              servicio.razon.length >= 1
                ? `
            <p>
              <strong>Razón de desmontaje:</strong> 
              ${servicio.razon}
            </p>
            `
                : ''
            }
            ${
              servicio.nuevaLlanta.length >= 1
                ? `<p><strong>Nueva llanta</strong>: ${servicio.nuevaLlanta}</p>`
                : ''
            }
            ${
              servicio.stock.length >= 1
                ? `<p><strong>Stock origen</strong>: ${servicio.stock}</p>`
                : ''
            }
            ${
              servicio.almacen_desmontaje.length >= 1
                ? `<p><strong>Stock origen</strong>: ${servicio.almacen_desmontaje}</p>`
                : ''
            }
          </div>
      </div>
      `
    );
  };

  type DeleteEvent = {
    serviceId: string | undefined;
    tireId: string | undefined;
  };

  const deleteEvent = ({ serviceId, tireId }: DeleteEvent) => {
    if (serviceId === undefined || tireId === undefined) return;

    const card = document.querySelector(
      `[data-servicioid="${serviceId}"]`
    ) as HTMLDivElement;
    const modal = document.querySelector(
      `[data-modal="${tireId}"] form`
    ) as HTMLDivElement;

    // * Clean
    saveData = saveData.filter((item) => item.id_servicio !== serviceId);
    card?.remove();
    modal
      ?.querySelectorAll<HTMLSelectElement | HTMLInputElement>(
        'input, select, button'
      )
      .forEach((item) => {
        item.disabled = false;
      });

    modal
      ?.querySelectorAll<HTMLInputElement>('.form__services input')
      .forEach((item) => {
        item.checked = false;
      });

    modal
      ?.querySelectorAll<HTMLInputElement>('.card__config-modal input')
      .forEach((item) => {
        if (item.type === 'radio') {
          item.checked = false;
        }
        const tires = document.querySelector(
          `[data-rotar-id="${tireId}"] input[value="${tireId}"]`
        ) as HTMLInputElement;
        tires.disabled = true;
      });

    modal
      ?.querySelectorAll<HTMLSelectElement>('.form__view-body select')
      .forEach((item) => {
        item.value = '';
      });

    formHidden.value = JSON.stringify(saveData);
  };

  // * Events

  document.addEventListener('submit', (e) => {
    const target = e.target as HTMLFormElement;

    if (target.matches('#taller-form')) {
      const date = document.querySelector(
          'input[type="date"]'
        ) as unknown as HTMLInputElement,
        time = document.querySelector(
          'input[type="time"]'
        ) as unknown as HTMLInputElement;

      if (date.value === '' || time.value === '') {
        e.preventDefault();
        Swal.fire({
          title: 'Error',
          text: 'Los campos de fecha y/o hora estan vacíos',
          icon: 'error',
          backdrop: true,
          showDenyButton: false,
          allowOutsideClick: true,
          allowEscapeKey: true,
        });
        return;
      }

      return;
    }

    if (target.matches('.service-page')) {
      e.preventDefault();
      const form: HTMLFormElement = e.target as HTMLFormElement;
      const data = Object.fromEntries(new FormData(form));

      const formHidden = document.getElementById(
        'hoja-servicio'
      ) as unknown as HTMLInputElement;
      formHidden.value = JSON.stringify(data);

      document
        .querySelector('.alert__success')
        ?.classList.add('active') as unknown as HTMLDivElement;

      setTimeout(
        () =>
          document.querySelector('.alert__success')?.classList.remove('active'),
        2000
      );
      return;
    }

    e.preventDefault(); // prevenimos el evento

    const form: HTMLFormElement = e.target as HTMLFormElement;
    const dataForm = new FormData(form);
    dataForm.append('id_servicio', String(Math.floor(Math.random() * 10000)));
    const data = Object.fromEntries(dataForm) as unknown as Servicio;

    addEvent(data);

    form
      .querySelectorAll<HTMLInputElement>('input, select, .btn-taller')
      .forEach((input) => (input.disabled = true));

    saveData.push(data);

    formHidden.value = JSON.stringify(saveData);

    document
      .querySelector('.alert__success')
      ?.classList.add('active') as unknown as HTMLDivElement;

    setTimeout(
      () =>
        document.querySelector('.alert__success')?.classList.remove('active'),
      2000
    );
  });

  document.addEventListener('change', (e) => {
    const target = e.target as HTMLInputElement;

    if (
      target.type === 'date' ||
      target.type === 'time' ||
      target.name === 'usuario'
    ) {
      const form = document.querySelector('.service-page') as HTMLFormElement;
      const data = Object.fromEntries(new FormData(form));

      const formHidden = document.getElementById(
        'hoja-servicio'
      ) as unknown as HTMLInputElement;
      formHidden.value = JSON.stringify(data);

      document
        .querySelector('.alert__success')
        ?.classList.add('active') as unknown as HTMLDivElement;

      setTimeout(
        () =>
          document.querySelector('.alert__success')?.classList.remove('active'),
        2000
      );
    }

    if (target.matches('[data-vehicleFix]')) {
      const formHidden = document.getElementById(
        'vehiculo-data'
      ) as unknown as HTMLInputElement;

      const form = document.getElementById('vehicle-form') as HTMLFormElement;
      const formData = Object.fromEntries(new FormData(form));

      if (target.checked) {
        target.value = 'on';
      } else {
        target.value = '';
      }

      formHidden.value = JSON.stringify(formData);
    }

    if (target.name === 'rotar') {
      switch (target.value) {
        case 'no':
          document
            .querySelectorAll<HTMLInputElement>(
              `[data-rotar-id="${target.dataset.radioid}"]`
            )
            .forEach((label) => (label.style.display = 'none'));
          break;

        case 'mismo':
          document.querySelectorAll<HTMLInputElement>(
            `[data-rotar-id="${target.dataset.radioid}"]`
          )[0].style.display = 'none';
          document.querySelectorAll<HTMLInputElement>(
            `[data-rotar-id="${target.dataset.radioid}"]`
          )[1].style.display = 'flex';
          break;

        case 'otro':
          document.querySelectorAll<HTMLInputElement>(
            `[data-rotar-id="${target.dataset.radioid}"]`
          )[0].style.display = 'block';
          document.querySelectorAll<HTMLInputElement>(
            `[data-rotar-id="${target.dataset.radioid}"]`
          )[1].style.display = 'none';
          break;

        default:
          break;
      }
    }

    if (target.dataset.nav) {
      if (target.value === 'desmontaje') {
        document
          .querySelectorAll(`[data-view="${target.dataset.nav}"]`)
          .forEach((item) => item.classList.remove('active'));

        target.classList.add('active');
        document
          .querySelectorAll<HTMLDivElement>(
            `[data-view="${target.dataset.nav}"]`
          )
          .forEach((view) => (view.style.display = 'none'));

        document.querySelectorAll<HTMLDivElement>(
          `[data-view="${target.dataset.nav}"]`
        )[1].style.display = 'block';
      } else {
        document
          .querySelectorAll<HTMLDivElement>(
            `[data-view="${target.dataset.nav}"]`
          )
          .forEach((item) => item.classList.remove('active'));

        target.classList.add('active');
        document
          .querySelectorAll<HTMLDivElement>(
            `[data-view="${target.dataset.nav}"]`
          )
          .forEach((view) => (view.style.display = 'none'));

        document.querySelectorAll<HTMLDivElement>(
          `[data-view="${target.dataset.nav}"]`
        )[0].style.display = 'block';
      }
    }

    if (target.name === 'inflarVehiculo') {
      if (target.value.length >= 0) {
        const inflar =
        document.querySelectorAll<HTMLInputElement>('[name="inflar"]');

        inflar.forEach((item) => {
          if (item.type === 'checkbox') {
            item.checked = true;
            saveData = [
              ...saveData,
              {
                id: item.dataset.tireid,
                inflar: 'on',
              },
            ];
          }
        });
      }
    }
  });

  document.addEventListener('input', (e) => {
    const target = e.target as HTMLInputElement;

    const form = document.querySelector('.service-page') as HTMLFormElement;
    const data = Object.fromEntries(new FormData(form));

    const formHidden = document.getElementById(
      'hoja-servicio'
    ) as unknown as HTMLInputElement;
    formHidden.value = JSON.stringify(data);
  });

  // * Eliminar evento
  document.addEventListener('click', (e) => {
    const event = e.target as HTMLElement;

    if (event.matches('.delete')) {
      deleteEvent({
        serviceId: event.dataset.delete,
        tireId: event.dataset.tireown,
      });
    }
  });
})();

(() => {
  document.addEventListener('change', (e) => {
    const target = e.target as HTMLInputElement;
    if (target.name === 'stock') {
      const llanta = target.nextElementSibling
        ?.nextElementSibling as HTMLInputElement;

      switch (target.value) {
        case 'nueva':
          fetch('/api/tiresearchtaller?inventario=Nueva')
            .then((res) => res.json())
            .then((json) => {
              let options = `<option value="">Seleccione una llanta</option>`;

              json.result.forEach((item: any) => {
                options += `<option value="${item.numero_economico}">${item.numero_economico} - ${item.producto__dimension}</option>`;
              });

              llanta.innerHTML = options;
            })
            .catch((error) => console.error(error));

          break;
        case 'renovada':
          fetch('/api/tiresearchtaller?inventario=Renovada')
            .then((res) => res.json())
            .then((json) => {
              let options = `<option value="">Seleccione una llanta</option>`;

              json.result.forEach((item: any) => {
                options += `<option value="${item.numero_economico}">${item.numero_economico} - ${item.producto__dimension}</option>`;
              });

              llanta.innerHTML = options;
            })
            .catch((error) => console.error(error));

          break;
        case 'servicio':
          fetch('/api/tiresearchtaller?inventario=Servicio')
            .then((res) => res.json())
            .then((json) => {
              let options = `<option value="">Seleccione una llanta</option>`;

              json.result.forEach((item: any) => {
                options += `<option value="${item.numero_economico}">${item.numero_economico} - ${item.producto__dimension}</option>`;
              });

              llanta.innerHTML = options;
            })
            .catch((error) => console.error(error));

          break;

        default:
          break;
      }
    }
  });
})();

(() => {
  /* Listening for a change event on the radio buttons. */
  document.addEventListener('change', (e) => {
    const target = e.target as HTMLInputElement;
    const origen = document.getElementById(
      `origen-llanta-${target.dataset.radioid}`
    ) as HTMLInputElement;
    const vehiculoOrigen = document.getElementById(
      `origen-vehiculo-${target.dataset.radioid}`
    ) as HTMLInputElement;

    /* Filtering the array of objects and returning the objects that do not have the same id as the
    target.dataset.radioid. */
    if (target.value === 'mismo') {
      const tires = document.querySelector(
        `[data-rotar-id="${target.dataset.radioid}"] input[value="${target.dataset.radioid}"]`
      ) as HTMLInputElement;
      tires.disabled = true;
    }

    /* Fetching data from an API and populating a select element with the data. */
    if (target.value === 'otro') {
      origen.innerHTML = `<option value="">Seleccione una llanta</option>`;

      fetch('/api/vehicleandtiresearchtaller')
        .then((res) => (res.ok ? res.json() : Promise.reject(res)))
        .then((json) => {
          vehiculoOrigen.innerHTML = `<option value="">Seleccione un vehiculo</option>`;
          vehiculoOrigen.innerHTML += json.vehiculos_list.map((item: any) => {
            return `<option value="${item.id}">${item.numero_economico}</option>`;
          });
        })
        .catch((error) => console.error(error));

      vehiculoOrigen.addEventListener('change', (e) => {
        if (vehiculoOrigen.value === '') return;

        fetch(
          '/api/vehicleandtiresearchtaller?id_select=' +
            vehiculoOrigen.value.toLocaleLowerCase()
        )
          .then((res) => (res.ok ? res.json() : Promise.reject(res)))
          .then((json) => {
            origen.innerHTML = `<option value="">Seleccione un vehiculo</option>`;
            origen.innerHTML += json.llantas.map((item: any) => {
              return `<option value="${item.id}">${item.posicion}</option>`;
            });
          })
          .catch((error) => console.error(error));
      });
    }
  });
})();
