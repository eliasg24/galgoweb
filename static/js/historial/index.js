import { getDocs } from "./getDocs.js";
import { search } from "./search.js";

document.addEventListener('DOMContentLoaded', (e) => {
  getDocs(`${window.location.origin}/api/historicodeorden?page=1&size=10`);
  search();
});