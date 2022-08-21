"use strict";
const getSelectInputs = (id) => {
    const views = Array(...document.querySelectorAll(`[data-view="${id}"]`)), servicios = Array(...views[0].querySelectorAll('input, select')), montajes = Array(...views[1].querySelectorAll('input, select'));
    const isVehicle = servicios.some((input) => input.value === 'mismo' && input.checked === true);
    const isOtherVehicle = servicios.some((input) => input.value === 'otro' && input.checked === true);
    const totalServicios = servicios.filter((item) => {
        if (item.checked === true) {
            return item;
        }
        if (item.type !== 'checkbox' && item.type !== 'radio') {
            if (item.value)
                return item;
        }
    });
    const totalMontajes = montajes.filter((item) => {
        if (item.checked === true) {
            return item;
        }
        if (item.type !== 'checkbox' && item.type !== 'radio') {
            if (item.value)
                return item;
        }
    });
    return {
        totalMontajes,
        totalServicios,
        servicios,
        montajes,
        isVehicle,
        isOtherVehicle,
    };
};
(() => {
    document.addEventListener('DOMContentLoaded', (e) => {
        const form = document.querySelector('.service-page');
        const data = Object.fromEntries(new FormData(form));
        const formHidden = document.getElementById('hoja-servicio');
        formHidden.value = JSON.stringify(data);
    });
})();
(() => {
    const tires = document.querySelectorAll('.tire');
    tires.forEach((tire) => {
        tire.addEventListener('click', (e) => {
            let tireTs = tire;
            const id = tireTs.dataset.id;
            const modal = document.querySelector(`[data-modal="${id}"]`);
            modal?.classList.add('active');
            document.addEventListener('click', (e) => {
                const target = e.target;
                if (target.matches('.close-modal')) {
                    modal?.classList.remove('active');
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
            ${servicio.otroVehiculo.length >= 1
            ? `
            <p>
              <strong>Vehículo Destino:</strong> 
              ${servicio.otroVehiculo}
            </p>
            `
            : ''}
            ${servicio.destino_llanta
            ? `
              <p>
                <strong>Llanta y Posición Destino:</strong> 
                ${servicio.destino_llanta}
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
            ? `<p><strong>Stock destino</strong>: ${servicio.almacen_desmontaje}</p>`
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
        card?.remove();
        modal
            ?.querySelectorAll('input, select, button')
            .forEach((item) => {
            item.disabled = false;
        });
        modal
            ?.querySelectorAll('.form__services input')
            .forEach((item) => {
            item.checked = false;
        });
        modal
            ?.querySelectorAll('.card__config-modal input')
            .forEach((item) => {
            if (item.type === 'radio') {
                item.checked = false;
            }
            const tires = document.querySelector(`[data-rotar-id="${tireId}"] input[value="${tireId}"]`);
            tires.disabled = true;
        });
        modal
            ?.querySelectorAll('.form__view-body select')
            .forEach((item) => {
            item.value = '';
        });
        formHidden.value = JSON.stringify(saveData);
    };
    document.addEventListener('submit', (e) => {
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
            document
                .querySelector('.alert__success')
                ?.classList.add('active');
            setTimeout(() => document.querySelector('.alert__success')?.classList.remove('active'), 2000);
            return;
        }
        e.preventDefault();
        const form = e.target;
        const dataForm = new FormData(form);
        dataForm.append('id_servicio', String(Math.floor(Math.random() * 10000)));
        const data = Object.fromEntries(dataForm);
        const formContainer = form.parentElement;
        const { totalMontajes, totalServicios, montajes, isVehicle, isOtherVehicle, } = getSelectInputs(form.parentElement?.dataset.modal);
        const otroVehiculo = form.querySelector('.otro-vehiculo'), ovInputs = Array(...otroVehiculo?.querySelectorAll('input, select')).filter((item) => item.type !== 'hidden');
        const imposibleKm = ovInputs.find((input) => input.name === 'no_km' && input.checked === true);
        let rotarIsComplete = true;
        if (ovInputs[0].value) {
            if (!imposibleKm) {
                rotarIsComplete = ovInputs.some((input) => !input.value);
            }
            else {
                ovInputs[1].value
                    ? (rotarIsComplete = false)
                    : (rotarIsComplete = true);
            }
        }
        if (isVehicle) {
            let inputs = Array(...form.querySelectorAll('.card__config-modal input')), isSelectInput = inputs.some((input) => input.checked === true);
            if (!isSelectInput) {
                return Swal.fire('Rotación incompleta', 'Seleccione una llanta para completar la rotación', 'warning');
            }
        }
        if (isOtherVehicle) {
            if (rotarIsComplete) {
                return Swal.fire('Algo anda mal', 'Faltan datos para completar la rotación', 'warning');
            }
        }
        if (totalMontajes.length === 0 && totalServicios.length <= 1) {
            return Swal.fire('Ups, no se ha realizado nada', 'No puede guardar si no ha realizado un servicio', 'error');
        }
        if (totalMontajes.length > 0) {
            if (totalMontajes.length < montajes.length) {
                return Swal.fire('Montaje incompleto', 'El montaje no se ha completado', 'warning');
            }
        }
        addEvent(data);
        form
            .querySelectorAll('input, select, .btn-taller')
            .forEach((input) => (input.disabled = true));
        saveData.push(data);
        formHidden.value = JSON.stringify(saveData);
        formContainer?.classList.remove('active');
        document
            .querySelector('.alert__success')
            ?.classList.add('active');
        setTimeout(() => document.querySelector('.alert__success')?.classList.remove('active'), 2000);
    });
    document.addEventListener('change', (e) => {
        const target = e.target;
        if (target.matches('#no_km')) {
            const kmInput = document.querySelector('[name="km_montado"]');
            if (target.checked) {
                kmInput.disabled = true;
            }
            else {
                kmInput.disabled = false;
            }
        }
        if (target.type === 'date' ||
            target.type === 'time' ||
            target.name === 'usuario') {
            const form = document.querySelector('.service-page');
            const data = Object.fromEntries(new FormData(form));
            const formHidden = document.getElementById('hoja-servicio');
            formHidden.value = JSON.stringify(data);
            document
                .querySelector('.alert__success')
                ?.classList.add('active');
            setTimeout(() => document.querySelector('.alert__success')?.classList.remove('active'), 2000);
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
            const container = document.querySelectorAll(`[data-rotar-id="${target.dataset.radioid}"]`);
            switch (target.value) {
                case 'no':
                    document
                        .querySelectorAll(`[data-rotar-id="${target.dataset.radioid}"]`)
                        .forEach((label) => (label.style.display = 'none'));
                    container[0]
                        .querySelectorAll('input, select')
                        .forEach((input) => (input.value = ''));
                    container[1]
                        .querySelectorAll('input, select')
                        .forEach((input) => (input.checked = false));
                    break;
                case 'mismo':
                    container[0].style.display = 'none';
                    container[1].style.display = 'flex';
                    container[0]
                        .querySelectorAll('input, select')
                        .forEach((input) => (input.value = ''));
                    break;
                case 'otro':
                    container[0].style.display = 'block';
                    container[1].style.display = 'none';
                    container[1]
                        .querySelectorAll('input')
                        .forEach((input) => (input.checked = false));
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
        const target = e.target;
        if (target.name === 'stock') {
            const llanta = target.nextElementSibling
                ?.nextElementSibling;
            switch (target.value) {
                case 'nueva':
                    fetch('/api/tiresearchtaller?inventario=Nueva')
                        .then((res) => res.json())
                        .then((json) => {
                        let options = '';
                        json.result.forEach((item) => {
                            options += `<option value="${item.numero_economico}">${item.numero_economico} - ${item.producto__producto}</option>`;
                        });
                        llanta.innerHTML = options;
                    })
                        .catch((error) => console.error(error));
                    break;
                case 'renovada':
                    fetch('/api/tiresearchtaller?inventario=Renovada')
                        .then((res) => res.json())
                        .then((json) => {
                        let options = '';
                        json.result.forEach((item) => {
                            options += `<option value="${item.numero_economico}">${item.numero_economico} - ${item.producto__producto}</option>`;
                        });
                        llanta.innerHTML = options;
                    })
                        .catch((error) => console.error(error));
                    break;
                case 'servicio':
                    fetch('/api/tiresearchtaller?inventario=Servicio')
                        .then((res) => res.json())
                        .then((json) => {
                        let options = '';
                        json.result.forEach((item) => {
                            options += `<option value="${item.numero_economico}">${item.numero_economico} - ${item.producto__producto}</option>`;
                        });
                        llanta.innerHTML = options;
                    })
                        .catch((error) => console.error(error));
                    break;
            }
        }
        if (target.name === 'nuevaLlanta') {
            const datalist = target.nextElementSibling;
            const list = Array(...datalist.querySelectorAll('option')).map((item) => item.value);
            if (!list.includes(target.value)) {
                target.value = '';
                Swal.fire('Error', 'El valor no coincide con ningun número económico', 'info');
            }
        }
    });
})();
(() => {
    document.addEventListener('change', (e) => {
        const target = e.target;
        if (target.value === 'mismo') {
            const tires = document.querySelector(`[data-rotar-id="${target.dataset.radioid}"] input[value="${target.dataset.radioid}"]`);
            tires.disabled = true;
        }
        if (target.value === 'otro') {
            const origen = document.getElementById(`origen-llanta-${target.dataset.radioid}`);
            const vehiculoOrigen = document.getElementById(`origen-vehiculo-${target.dataset.radioid}`);
            const kmMontado = document.getElementById(`origen-km_montadoo-${target.dataset.radioid}`);
            const container = origen.parentElement?.parentElement;
            const destinoVehiculo = container?.querySelector('[name="destino-vehiculo"]');
            const destinoLlanta = container?.querySelector('[name="destino-llanta"]');
            origen.innerHTML = `<option value="">Seleccione una llanta</option>`;
            const inputOrigen = vehiculoOrigen.previousElementSibling;
            let list = [];
            fetch('/api/vehicleandtiresearchtaller')
                .then((res) => (res.ok ? res.json() : Promise.reject(res)))
                .then((json) => {
                json.vehiculos_list.forEach((item) => {
                    vehiculoOrigen.innerHTML += `<option value="${item.numero_economico}"></option>`;
                });
                list = Array(...vehiculoOrigen.querySelectorAll('option')).map((item) => item.value);
            })
                .catch((error) => console.error(error));
            inputOrigen?.addEventListener('change', (e) => {
                if (inputOrigen.value === '')
                    return;
                if (!list.includes(inputOrigen.value)) {
                    inputOrigen.value = '';
                    Swal.fire('Error', 'El número economico no existe', 'error');
                    return;
                }
                fetch('/api/vehicleandtiresearchtaller?id_select=' + inputOrigen.value)
                    .then((res) => (res.ok ? res.json() : Promise.reject(res)))
                    .then(({ km_max, km_min, llantas }) => {
                    kmMontado.max = km_max || '';
                    kmMontado.min = km_min || '';
                    origen.innerHTML = `<option value="">Seleccione un vehiculo</option>`;
                    origen.innerHTML += llantas.map((item) => {
                        return `<option value="${item.id}">${item.numero_economico} - ${item.posicion}</option>`;
                    });
                })
                    .catch((error) => console.error(error));
            });
        }
    });
})();
(() => {
    document.addEventListener('change', (e) => {
        const target = e.target;
        if (target.matches('[data-view] input, [data-view] select')) {
            const id = target.dataset.idpadre;
            const { totalMontajes, totalServicios } = getSelectInputs(id);
            if (totalServicios.length > 1) {
                document.querySelector(`[data-nav="${target.dataset.idpadre}"][value="desmontaje"]`).disabled = true;
            }
            else {
                document.querySelector(`[data-nav="${target.dataset.idpadre}"][value="desmontaje"]`).disabled = false;
            }
            if (totalMontajes.length > 0) {
                document.querySelector(`[data-nav="${target.dataset.idpadre}"][value="sr"]`).disabled = true;
            }
            else {
                document.querySelector(`[data-nav="${target.dataset.idpadre}"][value="sr"]`).disabled = false;
            }
        }
    });
})();
(() => {
    document.addEventListener('change', (e) => {
        const target = e.target;
        if (target.name === 'llantaOrigen') {
            const id = target.dataset.idpadre;
            const options = Array(...target.querySelectorAll('option'));
            let selectedOption = options.find((item) => item.value === target.value)?.textContent;
            const destinoLlanta = document.querySelector(`[name="destino_llanta"][data-idpadre="${id}"]`);
            console.log({ destinoLlanta });
            destinoLlanta.value = selectedOption;
        }
    });
})();
//# sourceMappingURL=index.js.map