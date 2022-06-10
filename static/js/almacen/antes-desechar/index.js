import { removeFilters, setFilters, setValues } from "./getByEconomic.js";
import { getCounter } from "./getCounter.js";
import getTires from "./getTires.js";

document.addEventListener('DOMContentLoaded', (e) => {
  setFilters();
  setValues();
  removeFilters();
  getTires(window.location.search);
  getCounter();
});
