const form = document.getElementById("simulationForm");
const statusDiv = document.getElementById("status");
const summaryDiv = document.getElementById("summary");
const resultsDiv = document.getElementById("results");
const downloadExcelBtn = document.getElementById("downloadExcelBtn");

let netProfitChartInstance = null;
let cumulativeProfitChartInstance = null;
let demandRentedChartInstance = null;
let lastSimulationData = null;

form.addEventListener("submit", async function (e) {
  e.preventDefault();

  const data = {
    capacity: document.getElementById("capacity").value,
    cost_per_server: document.getElementById("cost_per_server").value,
    selling_price: document.getElementById("selling_price").value,
    salvage_value: document.getElementById("salvage_value").value,
    good_pct: document.getElementById("good_pct").value,
    fair_pct: document.getElementById("fair_pct").value,
    poor_pct: document.getElementById("poor_pct").value,
    num_days: document.getElementById("num_days").value
  };

  statusDiv.innerHTML = "Running simulation...";
  summaryDiv.innerHTML = "";
  resultsDiv.innerHTML = "";
  downloadExcelBtn.style.display = "none";
  lastSimulationData = null;

  try {
    const response = await fetch("/run-simulation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!result.success) {
      statusDiv.innerHTML = "❌ Error: " + result.error;
      return;
    }

    statusDiv.innerHTML = "✅ Simulation completed successfully!";

    renderSummary(result.data.summary);
    renderTable(result.data.results);
    renderCharts(result.data.charts);

    lastSimulationData = {
      results: result.data.results,
      summary: result.data.summary
    };

    downloadExcelBtn.style.display = "block";

  } catch (error) {
    statusDiv.innerHTML = "❌ Request failed: " + error.message;
  }
});

downloadExcelBtn.addEventListener("click", async function () {
  if (!lastSimulationData) {
    statusDiv.innerHTML = "❌ Please run the simulation first.";
    return;
  }

  try {
    statusDiv.innerHTML = "📥 Preparing Excel file...";

    const response = await fetch("/download-excel", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(lastSimulationData)
    });

    if (!response.ok) {
      const errorResult = await response.json();
      statusDiv.innerHTML = "❌ Error: " + (errorResult.error || "Failed to download file");
      return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "simulation_results.xlsx";
    document.body.appendChild(a);
    a.click();
    a.remove();

    window.URL.revokeObjectURL(url);

    statusDiv.innerHTML = "✅ Excel file downloaded successfully!";
  } catch (error) {
    statusDiv.innerHTML = "❌ Download failed: " + error.message;
  }
});

function renderSummary(summary) {
  summaryDiv.innerHTML = `
    <h2>Simulation Summary</h2>
    <div class="summary-box">
      <div class="card"><h3>Total Servers Rented</h3><p>${summary.total_servers_rented}</p></div>
      <div class="card"><h3>Total Idle Servers</h3><p>${summary.total_idle_servers}</p></div>
      <div class="card"><h3>Total Extra Demand</h3><p>${summary.total_extra_demand}</p></div>
      <div class="card"><h3>Total Rental Revenue</h3><p>${summary.total_rental_revenue}</p></div>
      <div class="card"><h3>Total Server Cost</h3><p>${summary.total_server_cost}</p></div>
      <div class="card"><h3>Total Salvage Revenue</h3><p>${summary.total_salvage_revenue}</p></div>
      <div class="card"><h3>Total Lost Profit</h3><p>${summary.total_lost_profit}</p></div>
      <div class="card"><h3>Final Net Profit</h3><p>${summary.final_net_profit}</p></div>
    </div>
  `;
}

function renderTable(results) {
  let tableHTML = `
    <h2>Daily Results</h2>
    <table>
      <thead>
        <tr>
          <th>Day</th>
          <th>Day Type</th>
          <th>RND</th>
          <th>Demand</th>
          <th>Rented</th>
          <th>Idle</th>
          <th>Extra Demand</th>
          <th>Total Cost</th>
          <th>Rental Revenue</th>
          <th>Salvage Revenue</th>
          <th>Lost Profit</th>
          <th>Net Profit</th>
        </tr>
      </thead>
      <tbody>
  `;

  results.forEach(row => {
    tableHTML += `
      <tr>
        <td>${row.day}</td>
        <td>${row.day_type}</td>
        <td>${row.rnd}</td>
        <td>${row.demand}</td>
        <td>${row.rented}</td>
        <td>${row.idle}</td>
        <td>${row.extra_demand}</td>
        <td>${row.total_cost}</td>
        <td>${row.rental_revenue}</td>
        <td>${row.salvage_revenue}</td>
        <td>${row.lost_profit}</td>
        <td>${row.net_profit}</td>
      </tr>
    `;
  });

  tableHTML += `
      </tbody>
    </table>
  `;

  resultsDiv.innerHTML = tableHTML;
}

function renderCharts(charts) {
  const netProfitCtx = document.getElementById("netProfitChart").getContext("2d");
  const cumulativeProfitCtx = document.getElementById("cumulativeProfitChart").getContext("2d");
  const demandRentedCtx = document.getElementById("demandRentedChart").getContext("2d");

  if (netProfitChartInstance) netProfitChartInstance.destroy();
  if (cumulativeProfitChartInstance) cumulativeProfitChartInstance.destroy();
  if (demandRentedChartInstance) demandRentedChartInstance.destroy();

  netProfitChartInstance = new Chart(netProfitCtx, {
    type: "line",
    data: {
      labels: charts.days,
      datasets: [{
        label: "Net Profit per Day",
        data: charts.net_profit,
        borderWidth: 3,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Net Profit per Day"
        }
      }
    }
  });

  cumulativeProfitChartInstance = new Chart(cumulativeProfitCtx, {
    type: "line",
    data: {
      labels: charts.days,
      datasets: [{
        label: "Cumulative Profit",
        data: charts.cumulative_profit,
        borderWidth: 3,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Cumulative Profit Over Time"
        }
      }
    }
  });

  demandRentedChartInstance = new Chart(demandRentedCtx, {
    type: "bar",
    data: {
      labels: charts.days,
      datasets: [
        {
          label: "Demand",
          data: charts.demand,
          borderWidth: 2
        },
        {
          label: "Rented",
          data: charts.rented,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Demand vs Rented"
        }
      }
    }
  });
}
