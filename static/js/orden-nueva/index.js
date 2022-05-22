import { addItem } from './addItem.js';
import { form } from './form.js';
import { getData } from './getData.js';
import { removeItem } from './removeItem.js';

document.addEventListener('DOMContentLoaded', (e) => {
  getData();
  form();
  addItem();
  removeItem();
});

const date = document.getElementById('date');
let dateNow = new Date();

dateNow.toISOString().split('T')[0];

const offset = dateNow.getTimezoneOffset();
dateNow = new Date(dateNow.getTime() - offset * 60 * 1000);
date.value = dateNow.toISOString().split('T')[0];
