(async () => {
  const getEvents = async () => {
    try {
      const resp = await fetch('api/calendario');
      const json = await resp.json();

      if (!resp.ok) throw new Error('Algo salió mal');

      console.log(json)

      let newEvents;

      for (const event of json.calendarios) {
        const { horario_start_str, horario_end_str, ...restEvent } = event;

        newEvents = [
          {
            ...restEvent,
            start: event.horario_start_str,
            end: event.horario_end_str,
          }
        ];
      }

      return newEvents;
    } catch (error) {
      console.error(error);
    }
  };

  const calendarEvents = await getEvents();

  const calendar = (calendarEvents = []) => {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      locale: 'esLocale',
      initialView: 'timeGridWeek', // * timeGridWeek || dayGridMonth
      height: '100vh',
      selectable: true,
      events: calendarEvents,
      eventColor: '026cf5',
      eventClick: function ({ event }) {
        console.log({ event })
        alert('Event: ' + event.title);
      },
    });

    calendar.render();
  };

  calendar(calendarEvents);
})();
