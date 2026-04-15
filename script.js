// ── Charging curve data (replaces your CSV file) ──────────────────────────────
// Format: { SoC: ChargingSpeed }
// Replace these values with your actual Tesla_M3_Pannasonic3.csv data
const chargingCurveData = {
    0: 50, 5: 80, 10: 100, 15: 130, 20: 150, 25: 150, 30: 150,
    35: 150, 40: 145, 45: 140, 50: 130, 55: 120, 60: 110,
    65: 100, 70: 90, 75: 80, 80: 70, 85: 60, 90: 50,
    95: 40, 100: 30
};

// ── Chart setup ───────────────────────────────────────────────────────────────
const ctx = document.getElementById("chargingCurveChart").getContext("2d");
const chart = new Chart(ctx, {
    type: "line",
    data: {
        labels: Object.keys(chargingCurveData),
        datasets: [{
            label: "Charging Speed (kW)",
            data: Object.values(chargingCurveData),
            borderColor: "#ff4b4b",
            backgroundColor: "rgba(255,75,75,0.1)",
            borderWidth: 2,
            pointRadius: 2,
            fill: true,
            tension: 0.3
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { labels: { color: "#fafafa" } }
        },
        scales: {
            x: {
                title: { display: true, text: "SoC (%)", color: "#aaaaaa" },
                ticks: { color: "#aaaaaa" },
                grid: { color: "#333" }
            },
            y: {
                title: { display: true, text: "Charging Speed (kW)", color: "#aaaaaa" },
                ticks: { color: "#aaaaaa" },
                grid: { color: "#333" }
            }
        }
    }
});

// ── Toggle between methods ────────────────────────────────────────────────────
function toggleMethod() {
    const method = document.querySelector('input[name="method"]:checked').value;
    document.getElementById("curveSection").style.display  = method === "curve"  ? "block" : "none";
    document.getElementById("manualSection").style.display = method === "manual" ? "block" : "none";
    calculate();
}

// ── Main calculation ──────────────────────────────────────────────────────────
function calculate() {
    const method          = document.querySelector('input[name="method"]:checked').value;
    const startSoC        = parseInt(document.getElementById("startSoC").value);
    const endSoC          = parseInt(document.getElementById("endSoC").value);
    const batteryCapacity = parseFloat(document.getElementById("batteryCapacity").value);

    // Validate inputs
    if (isNaN(startSoC) || isNaN(endSoC) || isNaN(batteryCapacity)) return;
    if (startSoC >= endSoC) {
        document.getElementById("resDeltaSoC").textContent = "Start must be < End";
        return;
    }

    let avgChargingSpeed, priceMin;

    if (method === "curve") {
        priceMin = parseFloat(document.getElementById("priceMinCurve").value);

        // Average charging speed between startSoC and endSoC from curve
        const socValues = Object.keys(chargingCurveData)
            .map(Number)
            .filter(soc => soc >= startSoC && soc <= endSoC);

        if (socValues.length === 0) {
            document.getElementById("resAvgSpeed").textContent = "No curve data in range";
            return;
        }

        const sum = socValues.reduce((acc, soc) => acc + chargingCurveData[soc], 0);
        avgChargingSpeed = sum / socValues.length;

    } else {
        avgChargingSpeed = parseFloat(document.getElementById("avgSpeedManual").value);
        priceMin         = parseFloat(document.getElementById("priceMinManual").value);
    }

    if (isNaN(avgChargingSpeed) || isNaN(priceMin)) return;

    // Calculations (mirrors your Python logic exactly)
    const deltaSoCPercent      = endSoC - startSoC;
    const deltaSoCkWh          = deltaSoCPercent * batteryCapacity / 100;
    const chargingTimeMinutes  = Math.ceil((deltaSoCkWh / avgChargingSpeed) * 60);
    const chargingCost         = (chargingTimeMinutes / 60) * priceMin * 60;

    // Update results
    document.getElementById("resAvgSpeed").textContent = `${avgChargingSpeed.toFixed(2)} kW`;
    document.getElementById("resDeltaSoC").textContent = `${deltaSoCPercent}% (${deltaSoCkWh.toFixed(2)} kWh)`;
    document.getElementById("resTime").textContent     = `${chargingTimeMinutes} minutes`;
    document.getElementById("resCost").textContent     = `${chargingCost.toFixed(2)}€`;
}

// ── Run on load ───────────────────────────────────────────────────────────────
calculate();