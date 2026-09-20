import {
  CategoryScale,
  Chart,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from "chart.js";

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, LineController, Tooltip);

type RateChartPayload = {
  pair: string;
  baseCurrency: string;
  quoteCurrency: string;
  selectedDate: string;
  labels: string[];
  dates: string[];
  rates: string[];
  selectedIndex: number | null;
};

function parsePayload(canvas: HTMLCanvasElement): RateChartPayload {
  const dataId = canvas.dataset.chartDataId;
  if (!dataId) throw new Error("Historical chart data reference is missing.");

  const script = document.getElementById(dataId);
  if (!(script instanceof HTMLScriptElement) || script.type !== "application/json") {
    throw new Error("Historical chart data payload is missing.");
  }

  const value = JSON.parse(script.textContent ?? "") as Partial<RateChartPayload>;
  if (
    typeof value.pair !== "string" ||
    typeof value.baseCurrency !== "string" ||
    typeof value.quoteCurrency !== "string" ||
    typeof value.selectedDate !== "string" ||
    !Array.isArray(value.labels) ||
    !Array.isArray(value.dates) ||
    !Array.isArray(value.rates) ||
    value.labels.length !== value.rates.length ||
    value.dates.length !== value.rates.length
  ) {
    throw new Error("Historical chart data payload is invalid.");
  }

  const rates = value.rates.map((rate) => Number(rate));
  if (rates.some((rate) => !Number.isFinite(rate) || rate <= 0)) {
    throw new Error("Historical chart contains an invalid rate.");
  }

  return {
    pair: value.pair,
    baseCurrency: value.baseCurrency,
    quoteCurrency: value.quoteCurrency,
    selectedDate: value.selectedDate,
    labels: value.labels.map(String),
    dates: value.dates.map(String),
    rates: value.rates.map(String),
    selectedIndex:
      typeof value.selectedIndex === "number" &&
      Number.isInteger(value.selectedIndex) &&
      value.selectedIndex >= 0 &&
      value.selectedIndex < value.rates.length
        ? value.selectedIndex
        : null,
  };
}

function cssColor(element: Element, property: string, fallback: string): string {
  const value = getComputedStyle(element).getPropertyValue(property).trim();
  return value || fallback;
}

function renderRateChart(canvas: HTMLCanvasElement): void {
  if (canvas.dataset.rateChartEnhanced === "true") return;

  const statusId = canvas.getAttribute("aria-describedby");
  const status = statusId ? document.getElementById(statusId) : null;

  try {
    const payload = parsePayload(canvas);
    const root = canvas.closest(".qa-rate-series") ?? document.documentElement;
    const brand = cssColor(root, "--color-brand", "#2458a6");
    const muted = cssColor(root, "--color-muted", "#667085");
    const border = cssColor(root, "--color-border-subtle", "#d0d5dd");
    const ink = cssColor(root, "--color-ink", "#101828");
    const rates = payload.rates.map(Number);
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    new Chart(canvas, {
      type: "line",
      data: {
        labels: payload.labels,
        datasets: [
          {
            data: rates,
            borderColor: brand,
            borderWidth: 2,
            backgroundColor: brand,
            fill: false,
            tension: 0,
            spanGaps: false,
            pointRadius: (context) =>
              context.dataIndex === payload.selectedIndex ? 4 : 0,
            pointHoverRadius: (context) =>
              context.dataIndex === payload.selectedIndex ? 6 : 4,
            pointBorderWidth: (context) =>
              context.dataIndex === payload.selectedIndex ? 2 : 0,
            pointBorderColor: ink,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: reducedMotion ? false : { duration: 220 },
        normalized: true,
        interaction: {
          intersect: false,
          mode: "index",
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              title: (items) => items[0]?.label ?? "",
              label: (context) =>
                `${payload.quoteCurrency} per ${payload.baseCurrency}: ${context.formattedValue}`,
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              autoSkip: true,
              color: muted,
              maxRotation: 0,
              maxTicksLimit: 6,
            },
            border: {
              color: border,
            },
          },
          y: {
            beginAtZero: false,
            grid: {
              color: border,
            },
            ticks: {
              color: muted,
              maxTicksLimit: 5,
            },
            border: {
              display: false,
            },
          },
        },
      },
    });

    canvas.dataset.rateChartEnhanced = "true";
    if (status) {
      status.textContent =
        payload.selectedIndex === null
          ? "Visual chart ready. The selected exact observation is not represented by this aggregated series; use the table and summary for exact semantics."
          : "Visual chart ready. The selected historical observation is marked on the line; the table contains the same series data.";
    }
  } catch {
    canvas.hidden = true;
    if (status) {
      status.textContent =
        "Visual chart is unavailable. The historical summary and data table remain available.";
      status.classList.remove("qa-visually-hidden");
    }
  }
}

export function enhanceRateCharts(root: ParentNode = document): void {
  for (const canvas of root.querySelectorAll<HTMLCanvasElement>("[data-rate-chart]")) {
    renderRateChart(canvas);
  }
}
