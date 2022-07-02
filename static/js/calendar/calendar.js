(async () => {
  const getEvents = async () => {
    try {
      const resp = await fetch('api/calendario');
      const json = await resp.json();

      if (!resp.ok) throw new Error('Algo salió mal');

      return json.calendarios;
    } catch (error) {
      console.error(error);
    }
  };

  const calendarEvents = await getEvents();

  const calendar = (calendarEvents = []) => {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      locale: 'esLocale',
      initialView: 'timeGridWeek',
      height: '100vh',
      selectable: true,
      events: calendarEvents,
      eventColor: 'seagreen',
      eventClick: function (info) {
        alert('Event: ' + info.event.title);
      },
    });

    calendar.render();
  };

  calendar(calendarEvents);
})();
