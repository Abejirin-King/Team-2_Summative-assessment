document.getElementById("apply").addEventListener("click", async () => {
  const start = document.getElementById("start").value;
  const end = document.getElementById("end").value;
  const minFare = document.getElementById("min_fare").value;
  const maxFare = document.getElementById("max_fare").value;
  const sortBy = document.getElementById("sort_by").value;
  const results = document.getElementById("results");
  const tableContainer = document.getElementById("table-container");

  if (!start || !end) {
    results.innerHTML = "<p>Please select both start and end dates.</p>";
    return;
  }

  results.innerHTML = "<p>Loading...</p>";
  tableContainer.innerHTML = "";

  try {
    const response = await fetch(`/api/trips?start=${start}&end=${end}&min_fare=${minFare}&max_fare=${maxFare}&sort_by=${sortBy}`);
    const data = await response.json();

    if (!data.summary || data.summary.total_trips === 0) {
      results.innerHTML = "<p>No trips found for this range.</p>";
      return;
    }

    const s = data.summary;
    results.innerHTML = `
      <div class="cards">
        <div class="card"><h3>Total Trips</h3><p>${s.total_trips}</p></div>
        <div class="card"><h3>Avg Fare</h3><p>$${s.avg_fare}</p></div>
        <div class="card"><h3>Avg Distance</h3><p>${s.avg_distance} km</p></div>
        <div class="card"><h3>Avg Speed</h3><p>${s.avg_speed} km/h</p></div>
      </div>
    `;

    // Table for trip details
    let tableHTML = `
      <table>
        <thead>
          <tr>
            <th>Pickup</th>
            <th>Dropoff</th>
            <th>Distance (km)</th>
            <th>Fare ($)</th>
            <th>Speed (km/h)</th>
          </tr>
        </thead>
        <tbody>
    `;
    data.trips.forEach(trip => {
      tableHTML += `
        <tr>
          <td>${trip.pickup_dt}</td>
          <td>${trip.dropoff_dt}</td>
          <td>${trip.trip_distance_km}</td>
          <td>${trip.total_amount}</td>
          <td>${trip.trip_speed_kmph}</td>
        </tr>
      `;
    });
    tableHTML += `</tbody></table>`;
    tableContainer.innerHTML = tableHTML;

  } catch (err) {
    console.error("Error fetching data:", err);
    results.innerHTML = "<p>Error loading data. Check console for details.</p>";
  }
});
