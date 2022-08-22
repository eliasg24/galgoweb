import { insertServices } from './helpers/insert-services.js';

(async () => {
  const getEvents = async () => {
    try {
      const resp = await fetch('api/calendario');
      const json = await resp.json();

      if (!resp.ok) throw new Error('Algo salió mal');

      let newEvents = [];

      for (const event of json.calendarios) {
        const { horario_start_str, horario_end_str, ...restEvent } = event;
        newEvents = [
          ...newEvents,
          {
            ...restEvent,
            start: event.horario_start_str,
            end: event.horario_end_str,
          },
        ];
      }

      return newEvents;
    } catch (error) {
      console.error(error);
    }
  };

  let calendarEvents = await getEvents();

  const modal = (event) => {
    const modalContainer = document.querySelector('.modal__container'),
      modalBody = modalContainer.querySelector('.modal__body');
    const anchor = modalContainer.querySelector('#reporte');
    const closeBtn = document.querySelector('.btn.close');
    const { extendedProps } = event;

    modalBody.innerHTML = '';

    modalContainer.classList.add('active');
    modalContainer.querySelector('.modal-title').textContent = event.title;

    if (extendedProps.servicio__alineacion) {
      modalBody.innerHTML = `
        <div class="service-done">
          <span class="service-title">
            Servicio de Alineación: 
          </span>
          <span class="service-desc">
            Hecho
          </span>
        </div>
      `;
    }

    const hoja = extendedProps.hoja ? Object.values(extendedProps.hoja) : null;

    const servicios = extendedProps.servicio__hoja
      ? Object.values(extendedProps.servicio__hoja)
      : null;

    if (hoja) {
      insertServices(hoja, modalBody);
    } else if (servicios) {
      insertServices(servicios, modalBody);
    }

    closeBtn.addEventListener('click', (e) => {
      modalContainer.classList.remove('active');
    });

    if (extendedProps.reporte === 0) {
      anchor.style.display = 'none';
    } else {
      anchor.style.display = 'flex';
      anchor.querySelector(
        'a'
      ).href = `reporte-taller/${event.extendedProps.reporte}`;
    }

    if (extendedProps.estado === 'cerrado') {
      modalContainer.querySelector('#cerrar').style.display = 'none';
      modalContainer.querySelector('#borrar').style.display = 'none';
    } else if (extendedProps.estado === 'abierto') {
      modalContainer.querySelector('#borrar').style.display = 'flex';
      modalContainer.querySelector('#cerrar').style.display = 'flex';
      modalContainer.querySelector('#cerrar').addEventListener('click', (e) => {
        e.preventDefault();

        Swal.fire({
          title: '¿Desea cerrar la orden?',
          showDenyButton: true,
          showCancelButton: false,
          confirmButtonText: 'Guardar',
          denyButtonText: `Cancelar`,
        }).then((result) => {
          /* Read more about isConfirmed, isDenied below */
          if (result.isConfirmed) {
            fetch(`/api/cerrartaller?servicio=${extendedProps.id_servicio}`)
              .then((resp) => (resp.ok ? resp.json() : Promise.reject(resp)))
              .then((json) => {
                Swal.fire('Guardado!', '', 'success');
                setTimeout(async () => {
                  modalContainer.classList.remove('active');
                  calendarEvents = await getEvents();
                  calendar(calendarEvents);
                }, 500);
              })
              .catch((error) => {
                console.error(error);
                Swal.fire(
                  'Algo salió mal',
                  'Por favor contacte con el administrador',
                  'error'
                );
              });
          } else if (result.isDenied) {
            Swal.fire('Los orden no fue cerrada', '', 'info');
          }
        });
      });
      modalContainer.querySelector('#borrar').addEventListener('click', (e) => {
        e.preventDefault();

        Swal.fire({
          title: '¿Seguro de borrar la orden?',
          icon: 'info',
          showDenyButton: true,
          showCancelButton: false,
          confirmButtonText: 'Eliminar',
          denyButtonText: `Cancelar`,
        }).then((result) => {
          /* Read more about isConfirmed, isDenied below */
          if (result.isConfirmed) {
            fetch(`/api/archivartaller?vehiculo=${extendedProps.vehiculo__id}`)
              .then((resp) => (resp.ok ? resp.json() : Promise.reject(resp)))
              .then((json) => {
                Swal.fire('Eliminado', '', 'success');
                setTimeout(async () => {
                  modalContainer.classList.remove('active');
                  calendarEvents = await getEvents();
                  calendar(calendarEvents);
                }, 500);
              })
              .catch((error) => {
                console.error(error);
                Swal.fire(
                  'Algo salió mal',
                  'Por favor contacte con el administrador',
                  'error'
                );
              });
          } else if (result.isDenied) {
            Swal.fire('Los orden no fue eliminada', '', 'info');
          }
        });
      });
    }
  };

  const calendar = (calendarEvents = []) => {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      locale: 'esLocale',
      initialView: 'timeGridWeek', // * timeGridWeek || dayGridMonth
      height: '100vh',
      selectable: true,
      events: calendarEvents,
      eventColor: '026cf5',
      eventClick: function (e) {
        const { event } = e;
        modal(event);
      },
    });

    calendar.render();
  };

  calendar(calendarEvents);
})();
