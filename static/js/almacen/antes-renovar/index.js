import { getByEconomic } from "./getByEconomic.js";
import { getTires } from "./getTires.js"

document.addEventListener('DOMContentLoaded', (e) => {
  getTires();
  getByEconomic();
})

