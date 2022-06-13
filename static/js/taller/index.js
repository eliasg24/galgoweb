"use strict";
(() => {
    const tires = document.querySelectorAll('.tire');
    tires.forEach((tire) => {
        tire.addEventListener('click', (e) => {
            var _a;
            const id = tire.dataset.id;
            (_a = document.querySelector(`[data-modal="${id}"]`)) === null || _a === void 0 ? void 0 : _a.classList.add('active');
            document.addEventListener('click', (e) => {
                var _a;
                if (e.target.matches('.close-modal')) {
                    (_a = document
                        .querySelector(`[data-modal="${id}"]`)) === null || _a === void 0 ? void 0 : _a.classList.remove('active');
                }
            });
        });
    });
})();
(() => {
    const saveData = [];
    document.addEventListener('submit', (e) => {
        if (e.target.matches('#taller-form'))
            return;
        e.preventDefault();
        const form = e.target;
        const data = Object.fromEntries(new FormData(form));
        form
            .querySelectorAll('input, select, .btn-submit')
            .forEach((input) => input.setAttribute('disabled', ''));
        saveData.push(data);
        const formHidden = document.getElementById('data-taller');
        formHidden.value = JSON.stringify(saveData);
    });
    document.addEventListener('change', (e) => {
        if (e.target.name === 'rotar') {
            switch (e.target.value) {
                case 'no':
                    document
                        .querySelectorAll(`[data-rotar-id="${e.target.dataset.radioid}"]`)
                        .forEach((label) => (label.style.display = 'none'));
                    break;
                case 'mismo':
                    document.querySelectorAll(`[data-rotar-id="${e.target.dataset.radioid}"]`)[0].style.display = 'none';
                    document.querySelectorAll(`[data-rotar-id="${e.target.dataset.radioid}"]`)[1].style.display = 'block';
                    break;
                case 'otro':
                    document
                        .querySelectorAll(`[data-rotar-id="${e.target.dataset.radioid}"]`)
                        .forEach((label) => (label.style.display = 'block'));
                    break;
                default:
                    break;
            }
        }
    });
    document.addEventListener('click', (e) => {
        if (e.target.dataset.nav) {
            if (e.target.value === 'desmontaje') {
                document
                    .querySelectorAll('[data-nav]')
                    .forEach((item) => item.classList.remove('active'));
                e.target.classList.add('active');
                document
                    .querySelectorAll(`[data-view]`)
                    .forEach((view) => (view.style.display = 'none'));
                document.querySelectorAll(`[data-view="${e.target.dataset.nav}"]`)[1].style.display = 'block';
            }
            else {
                document
                    .querySelectorAll('[data-nav]')
                    .forEach((item) => item.classList.remove('active'));
                e.target.classList.add('active');
                document
                    .querySelectorAll(`[data-view]`)
                    .forEach((view) => (view.style.display = 'none'));
                document.querySelectorAll(`[data-view="${e.target.dataset.nav}"]`)[0].style.display = 'block';
            }
        }
    });
})();
//# sourceMappingURL=index.js.map