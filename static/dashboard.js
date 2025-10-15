async function fetchData() {
  const start = document.getElementById('start').value;
  const end = document.getElementById('end').value;
  const minFare = document.getElementById('minFare').value;
  const maxFare = document.getElementById('maxFare').value;

  if (!start || !end) {
    alert("Please select both start and end dates.");
    return;
  }

  try {
    const res = await fetch(`/api/trips?start=${start}&end=${end}&min_fare=${minFare}&max_fare=${maxFare}`);
    const data = await res.json();

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    // Summary
    document.getElementById("totalTrips").textContent = data.summary.total_trips || 0;
    document.getElementById("avgFare").textContent = data.summary.avg_fare || 0;
    document.getElementById("avgDistance").textContent = data.summary.avg_distance || 0;
    document.getElementById("avgSpeed").textContent = data.summary.avg_speed || 0;

    // Table
    const table = document.getElementById("tripTable");
    table.innerHTML = "";
    data.trips.forEach(trip => {
      const row = `
        <tr>
          <td>${trip.pickup_dt}</td>
          <td>${trip.dropoff_dt}</td>
          <td>${trip.trip_distance_km ?? '-'}</td>
          <td>${trip.total_amount ?? '-'}</td>
          <td>${trip.trip_speed_kmph ?? '-'}</td>
        </tr>`;
      table.insertAdjacentHTML('beforeend', row);
    });
  } catch (err) {
    console.error(err);
    alert("Failed to fetch data.");
  }
}
