import { getByDate } from "./getByDate.js";
import { getByEconomic } from "./getByEconomic.js";
import { getVehicles } from "./getData.js";

document.addEventListener('DOMContentLoaded', (e) => {
  getVehicles();
  getByDate();
  getByEconomic()
  filterBtn();
});

const filterBtn = () => {
  const open = document.querySelector('.btn-filter');
  const close = document.querySelector('.btn-close');
  const filters = document.querySelector('.filter__container');

  open.addEventListener('click', (e) => {
    filters.classList.add('active');
  });

  close.addEventListener('click', (e) => {
    filters.classList.remove('active');
  });
};
