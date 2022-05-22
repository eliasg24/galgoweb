import { getByEconomic } from "./getByEconomic.js";
import { getRodante } from "./getRodante.js"

document.addEventListener('DOMContentLoaded', (e) => {
  getRodante();
  getByEconomic();
})