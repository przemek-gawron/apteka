// Wykresy pulpitu. Dane pobierane z /api/stats/* (z celowym opóźnieniem -> spinner).
(function () {
  const css = getComputedStyle(document.documentElement);
  const color = (name) => css.getPropertyValue(name).trim();
  const pln = new Intl.NumberFormat("pl-PL", { style: "currency", currency: "PLN" });
  const charts = {};

  const hasChartJs = typeof window.Chart !== "undefined";
  if (hasChartJs) {
    Chart.defaults.font.family = color("--font");
    Chart.defaults.color = color("--muted");
    Chart.defaults.borderColor = color("--border");
  }

  function box(name) {
    const el = document.querySelector(`[data-chart="${name}"]`);
    return {
      spinner: el.querySelector(".spinner"),
      canvas: el.querySelector("canvas"),
      error: el.querySelector(".chart-error"),
    };
  }

  async function load(name, url, render) {
    const b = box(name);
    b.spinner.hidden = false;
    b.error.hidden = true;
    b.canvas.hidden = true;
    try {
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      b.canvas.hidden = false;
      render(b.canvas, data);
    } catch (e) {
      console.error(`Wykres ${name}:`, e);
      b.error.hidden = false;
    } finally {
      b.spinner.hidden = true;
    }
  }

  function draw(key, canvas, config) {
    if (!hasChartJs) return;
    if (charts[key]) charts[key].destroy();
    charts[key] = new Chart(canvas, config);
  }

  function loadRevenue(days) {
    const foot = document.querySelector('[data-testid="revenue-total"]');
    foot.hidden = true;
    return load("revenue", `/api/stats/revenue?days=${days}`, (canvas, data) => {
      const total = data.reduce((s, d) => s + d.revenue, 0);
      const count = data.reduce((s, d) => s + d.sales, 0);
      foot.textContent = `Suma: ${pln.format(total)} · ${count} paragonów`;
      foot.hidden = false;
      draw("revenue", canvas, {
        type: "line",
        data: {
          labels: data.map((d) => d.date.slice(5).split("-").reverse().join(".")),
          datasets: [{
            label: "Obrót",
            data: data.map((d) => d.revenue),
            borderColor: color("--primary"),
            backgroundColor: color("--primary-soft"),
            fill: true,
            tension: 0.3,
            pointRadius: days > 30 ? 0 : 3,
          }],
        },
        options: {
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: (c) => pln.format(c.parsed.y) } },
          },
          scales: { y: { beginAtZero: true, ticks: { callback: (v) => pln.format(v) } } },
        },
      });
    });
  }

  const rangeSelect = document.getElementById("revenue-range");
  rangeSelect.addEventListener("change", () => loadRevenue(rangeSelect.value));
  loadRevenue(rangeSelect.value);

  load("top", "/api/stats/top-drugs?days=30&limit=5", (canvas, data) => {
    const list = document.querySelector('[data-testid="top-list"]');
    list.replaceChildren();
    data.forEach((d) => {
      const li = document.createElement("li");
      const name = document.createElement("span");
      const stats = document.createElement("span");
      name.textContent = d.name;
      stats.className = "muted";
      stats.textContent = `${d.quantity} szt. · ${pln.format(d.revenue)}`;
      li.append(name, stats);
      list.appendChild(li);
    });
    draw("top", canvas, {
      type: "bar",
      data: {
        labels: data.map((d) => d.name),
        datasets: [{ label: "Sztuki", data: data.map((d) => d.quantity), backgroundColor: color("--primary"), borderRadius: 6 }],
      },
      options: { indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false } } },
    });
  });

  load("categories", "/api/stats/categories?days=30", (canvas, data) => {
    const palette = ["--c1", "--c2", "--c3", "--c4", "--c5", "--c6", "--c7", "--c8", "--c9", "--c10"].map(color);
    draw("categories", canvas, {
      type: "doughnut",
      data: {
        labels: data.map((d) => d.category),
        datasets: [{ data: data.map((d) => d.revenue), backgroundColor: palette, borderColor: color("--surface"), borderWidth: 2 }],
      },
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right", labels: { boxWidth: 12 } },
          tooltip: { callbacks: { label: (c) => `${c.label}: ${pln.format(c.parsed)}` } },
        },
      },
    });
  });
})();
