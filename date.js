const today = new Date();
const isoDate = new Intl.DateTimeFormat('en-CA', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  timeZone: 'Europe/Rome'
}).format(today);
const italianDate = new Intl.DateTimeFormat('it-IT', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'Europe/Rome'
}).format(today);

document.querySelectorAll('.current-date').forEach((element) => {
  element.dateTime = isoDate;
  element.textContent = italianDate;
});
