"use strict";
(() => {
    const tires = document.querySelectorAll('.tire');
    tires.forEach((tire) => {
        tire.addEventListener('click', (e) => {
            let tireTs = tire;
            const id = tireTs.dataset.id;
            const modal = document.querySelector(`[data-modal="${id}"]`);
            modal === null || modal === void 0 ? void 0 : modal.classList.add('active');
            document.addEventListener('click', (e) => {
                const target = e.target;
                if (target.matches('.close-modal')) {
                    modal === null || modal === void 0 ? void 0 : modal.classList.remove('active');
                }
            });
        });
    });
})();
(() => {
    let saveData = [];
    const eventList = document.querySelector('.tire-list');
    const formHidden = document.getElementById('data-taller');
    const addEvent = (servicio) => {
        eventList.insertAdjacentHTML('afterbegin', `
    <div class="tire-item" data-servicioid="${servicio.id_servicio}" >
        <span class="delete" data-delete="${servicio.id_servicio}" data-tireown="${servicio.llantaId}">
            &times;
          </span>
          <div class="service__img">
            <span class="icon-llanta-outline"></span>
          </div>
          <div class="service__body">
          ${servicio.tipoServicio === 'desmontaje'
            ? `
              <h3 class="service__title">
              Desmontaje
            </h3>
          `
            : ''}
              ${servicio.inflar !== ''
            ? `
              <h3 class="service__title">
                Inflado
              </h3>
              `
            : ''}
              ${servicio.rotar === 'otro'
            ? `
              <h3 class="service__title">
                Rotación entre vehículos
              </h3>
              `
            : ''}
              ${servicio.rotar === 'mismo'
            ? `
              <h3 class="service__title">
                Rotación entre llantas
              </h3>
              `
            : ''}
              ${servicio.balancear !== ''
            ? `
              <h3 class="service__title">
              Balanceo
            </h3>
              `
            : ''}
              ${servicio.reparar !== ''
            ? `
              <h3 class="service__title">
                Reparación
              </h3>
              `
            : ''}
              ${servicio.valvula !== ''
            ? `
              <h3 class="service__title">
                Reparación de valvula
              </h3>
              `
            : ''}
              ${servicio.costado !== ''
            ? `
              <h3 class="service__title">
                Reparación de costado
              </h3>
              `
            : ''}
            <p><strong>Llanta:</strong> ${servicio.numero_economico}</p>
            <p><strong>Posición:</strong> ${servicio.posicion}</p>
            ${servicio.razon.length >= 1
            ? `
            <p>
              <strong>Razón de desmontaje:</strong> 
              ${servicio.razon}
            </p>
            `
            : ''}
            ${servicio.nuevaLlanta.length >= 1
            ? `<p><strong>Nueva llanta</strong>: ${servicio.nuevaLlanta}</p>`
            : ''}
            ${servicio.stock.length >= 1
            ? `<p><strong>Stock origen</strong>: ${servicio.stock}</p>`
            : ''}
            ${servicio.almacen_desmontaje.length >= 1
            ? `<p><strong>Stock origen</strong>: ${servicio.almacen_desmontaje}</p>`
            : ''}
          </div>
      </div>
      `);
    };
    const deleteEvent = ({ serviceId, tireId }) => {
        if (serviceId === undefined || tireId === undefined)
            return;
        const card = document.querySelector(`[data-servicioid="${serviceId}"]`);
        const modal = document.querySelector(`[data-modal="${tireId}"] form`);
        saveData = saveData.filter((item) => item.id_servicio !== serviceId);
        card === null || card === void 0 ? void 0 : card.remove();
        modal === null || modal === void 0 ? void 0 : modal.querySelectorAll('input, select, button').forEach((item) => {
            item.disabled = false;
        });
        modal === null || modal === void 0 ? void 0 : modal.querySelectorAll('.form__services input').forEach((item) => {
            item.checked = false;
        });
        modal === null || modal === void 0 ? void 0 : modal.querySelectorAll('.card__config-modal input').forEach((item) => {
            if (item.type === 'radio') {
                item.checked = false;
            }
            const tires = document.querySelector(`[data-rotar-id="${tireId}"] input[value="${tireId}"]`);
            tires.disabled = true;
        });
        modal === null || modal === void 0 ? void 0 : modal.querySelectorAll('.form__view-body select').forEach((item) => {
            item.value = '';
        });
        formHidden.value = JSON.stringify(saveData);
    };
    document.addEventListener('submit', (e) => {
        var _a, _b;
        const target = e.target;
        if (target.matches('#taller-form')) {
            const date = document.querySelector('input[type="date"]'), time = document.querySelector('input[type="time"]'), user = document.querySelector('select[name="usuario"]'), km = document.querySelector('input[name="km_montado"]'), noKm = document.querySelector('input[name="no_km"]');
            if (date.value === '' || time.value === '' || user.value === '') {
                e.preventDefault();
                Swal.fire('Error', 'No se han completado datos en la hoja de servicio', 'error');
                return;
            }
            if (km.value === '' && !noKm.checked) {
                e.preventDefault();
                Swal.fire('Error', 'No se ha puesto un KM de montado', 'error');
                return;
            }
            return;
        }
        if (target.matches('.service-page')) {
            e.preventDefault();
            const form = e.target;
            const data = Object.fromEntries(new FormData(form));
            const formHidden = document.getElementById('hoja-servicio');
            formHidden.value = JSON.stringify(data);
            (_a = document
                .querySelector('.alert__success')) === null || _a === void 0 ? void 0 : _a.classList.add('active');
            setTimeout(() => { var _a; return (_a = document.querySelector('.alert__success')) === null || _a === void 0 ? void 0 : _a.classList.remove('active'); }, 2000);
            return;
        }
        e.preventDefault();
        const form = e.target;
        const dataForm = new FormData(form);
        dataForm.append('id_servicio', String(Math.floor(Math.random() * 10000)));
        const data = Object.fromEntries(dataForm);
        addEvent(data);
        form
            .querySelectorAll('input, select, .btn-taller')
            .forEach((input) => (input.disabled = true));
        saveData.push(data);
        console.log(saveData);
        formHidden.value = JSON.stringify(saveData);
        (_b = document
            .querySelector('.alert__success')) === null || _b === void 0 ? void 0 : _b.classList.add('active');
        setTimeout(() => { var _a; return (_a = document.querySelector('.alert__success')) === null || _a === void 0 ? void 0 : _a.classList.remove('active'); }, 2000);
    });
    document.addEventListener('change', (e) => {
        var _a;
        const target = e.target;
        if (target.type === 'date' ||
            target.type === 'time' ||
            target.name === 'usuario') {
            const form = document.querySelector('.service-page');
            const data = Object.fromEntries(new FormData(form));
            const formHidden = document.getElementById('hoja-servicio');
            formHidden.value = JSON.stringify(data);
            (_a = document
                .querySelector('.alert__success')) === null || _a === void 0 ? void 0 : _a.classList.add('active');
            setTimeout(() => { var _a; return (_a = document.querySelector('.alert__success')) === null || _a === void 0 ? void 0 : _a.classList.remove('active'); }, 2000);
        }
        if (target.matches('[data-vehicleFix]')) {
            const formHidden = document.getElementById('vehiculo-data');
            const form = document.getElementById('vehicle-form');
            const formData = Object.fromEntries(new FormData(form));
            if (target.checked) {
                target.value = 'on';
            }
            else {
                target.value = '';
            }
            formHidden.value = JSON.stringify(formData);
        }
        if (target.name === 'rotar') {
            switch (target.value) {
                case 'no':
                    document
                        .querySelectorAll(`[data-rotar-id="${target.dataset.radioid}"]`)
                        .forEach((label) => (label.style.display = 'none'));
                    break;
                case 'mismo':
                    document.querySelectorAll(`[data-rotar-id="${target.dataset.radioid}"]`)[0].style.display = 'none';
                    document.querySelectorAll(`[data-rotar-id="${target.dataset.radioid}"]`)[1].style.display = 'flex';
                    break;
                case 'otro':
                    document.querySelectorAll(`[data-rotar-id="${target.dataset.radioid}"]`)[0].style.display = 'block';
                    document.querySelectorAll(`[data-rotar-id="${target.dataset.radioid}"]`)[1].style.display = 'none';
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
                    .querySelectorAll(`[data-view="${target.dataset.nav}"]`)
                    .forEach((view) => (view.style.display = 'none'));
                document.querySelectorAll(`[data-view="${target.dataset.nav}"]`)[1].style.display = 'block';
            }
            else {
                document
                    .querySelectorAll(`[data-view="${target.dataset.nav}"]`)
                    .forEach((item) => item.classList.remove('active'));
                target.classList.add('active');
                document
                    .querySelectorAll(`[data-view="${target.dataset.nav}"]`)
                    .forEach((view) => (view.style.display = 'none'));
                document.querySelectorAll(`[data-view="${target.dataset.nav}"]`)[0].style.display = 'block';
            }
        }
        if (target.name === 'inflarVehiculo') {
            if (target.value.length >= 0) {
                const inflar = document.querySelectorAll('[name="inflar"]');
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
        const target = e.target;
        const form = document.querySelector('.service-page');
        const data = Object.fromEntries(new FormData(form));
        const formHidden = document.getElementById('hoja-servicio');
        formHidden.value = JSON.stringify(data);
    });
    document.addEventListener('click', (e) => {
        const event = e.target;
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
        var _a;
        const target = e.target;
        if (target.name === 'stock') {
            const llanta = (_a = target.nextElementSibling) === null || _a === void 0 ? void 0 : _a.nextElementSibling;
            switch (target.value) {
                case 'nueva':
                    fetch('/api/tiresearchtaller?inventario=Nueva')
                        .then((res) => res.json())
                        .then((json) => {
                        let options = `<option value="">Seleccione una llanta</option>`;
                        json.result.forEach((item) => {
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
                        json.result.forEach((item) => {
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
                        json.result.forEach((item) => {
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
    document.addEventListener('change', (e) => {
        const target = e.target;
        const origen = document.getElementById(`origen-llanta-${target.dataset.radioid}`);
        const vehiculoOrigen = document.getElementById(`origen-vehiculo-${target.dataset.radioid}`);
        const kmMontado = document.getElementById(`origen-km_montadoo-${target.dataset.radioid}`);
        if (target.value === 'mismo') {
            const tires = document.querySelector(`[data-rotar-id="${target.dataset.radioid}"] input[value="${target.dataset.radioid}"]`);
            tires.disabled = true;
        }
        if (target.value === 'otro') {
            origen.innerHTML = `<option value="">Seleccione una llanta</option>`;
            fetch('/api/vehicleandtiresearchtaller')
                .then((res) => (res.ok ? res.json() : Promise.reject(res)))
                .then((json) => {
                vehiculoOrigen.innerHTML = `<option value="">Seleccione un vehiculo</option>`;
                vehiculoOrigen.innerHTML += json.vehiculos_list.map((item) => {
                    return `<option value="${item.id}">${item.numero_economico}</option>`;
                });
            })
                .catch((error) => console.error(error));
            vehiculoOrigen.addEventListener('change', (e) => {
                if (vehiculoOrigen.value === '')
                    return;
                fetch('/api/vehicleandtiresearchtaller?id_select=' +
                    vehiculoOrigen.value.toLocaleLowerCase())
                    .then((res) => (res.ok ? res.json() : Promise.reject(res)))
                    .then((json) => {
                    kmMontado.max = json.km_max || '';
                    kmMontado.min = json.km_min || '';
                    origen.innerHTML = `<option value="">Seleccione un vehiculo</option>`;
                    origen.innerHTML += json.llantas.map((item) => {
                        return `<option value="${item.id}">${item.posicion}</option>`;
                    });
                })
                    .catch((error) => console.error(error));
            });
        }
    });
})();
//# sourceMappingURL=index.js.map