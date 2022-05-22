import { getDocs } from "./getDocs.js";

document.addEventListener('DOMContentLoaded', (e) => {
  getDocs(`${window.location.origin}/api/historicodeorden?page=1&size=10`);
});