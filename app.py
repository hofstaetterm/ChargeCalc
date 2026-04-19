from pathlib import Path

import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Charge Calculator")

@st.cache_data
def load_charging_curve() -> pd.DataFrame:
    csv_path = Path(__file__).parent / "chargingCurves" / "Tesla_M3_Pannasonic3.csv"
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error(f"Charging curve CSV not found: {csv_path}")
        return pd.DataFrame({"SoC": [], "ChargingSpeed": []})

st.title("Charge Calculator")

method = st.radio(
    "Calculation method",
    ("Use charging curve", "Enter average charging speed"),
)

st.header("Battery Information")
col1, col2, col3 = st.columns(3)
with col1:
    startSoC = st.number_input(
        "Start SoC (%)",
        min_value=0,
        max_value=100,
        value=20,
        step=1,
    )
with col2:
    endSoC = st.number_input(
        "End SoC (%)",
        min_value=0,
        max_value=100,
        value=80,
        step=1,
    )
with col3:
    batteryCapacity = st.number_input(
        "Battery Capacity (kWh)",
        min_value=0.0,
        value=66.5,
        step=0.1,
        format="%.1f",
    )

priceMin = 0.931
avgChargingSpeed = 0.0

if startSoC >= endSoC:
    st.warning("End SoC must be greater than Start SoC.")
else:
    if method == "Use charging curve":
        st.header("Charger Information")
        col1, col2 = st.columns(2)
        with col1:
            priceMin = st.number_input(
                "Price per minute",
                min_value=0.0,
                value=0.931,
                step=0.01,
                format="%.3f",
            )

        st.header("Charging Curve")
        charge_curve = load_charging_curve()
        st.line_chart(charge_curve.set_index("SoC")["ChargingSpeed"])

        avgChargingSpeed = charge_curve.set_index("SoC")["ChargingSpeed"].loc[int(startSoC): int(endSoC)].mean()
        avgChargingSpeed = avgChargingSpeed
    else:
        st.header("Manual Charging Speed")
        col1, col2 = st.columns(2)
        with col1:
            avgChargingSpeed = st.number_input(
                "Average Charging Speed (kW)",
                min_value=0.0,
                value=150.0,
                step=1.0,
                format="%.1f",
            )
        with col2:
            priceMin = st.number_input(
                "Price per minute",
                min_value=0.0,
                value=0.931,
                step=0.01,
                format="%.3f",
            )

    if avgChargingSpeed <= 0.0:
        st.error("Average charging speed must be greater than zero.")
    else:
        st.header("Results")
        deltaSoCPercent = endSoC - startSoC
        deltaSoCkWh = deltaSoCPercent * batteryCapacity / 100
        chargingTimeMinutes = math.ceil((deltaSoCkWh / avgChargingSpeed) * 60)
        chargingCost = chargingTimeMinutes * priceMin
        costPerKWh = chargingCost / deltaSoCkWh

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Avg. Charging Speed:")
            st.write(f"{avgChargingSpeed:.2f} kW")
        with col2:
            st.write("Delta SoC:")
            st.write(f"{deltaSoCPercent:.0f}% ({deltaSoCkWh:.2f} kWh)")
        with col3:
            st.write("Est. Charging Time:")
            st.write(f"{chargingTimeMinutes:.0f} minutes")

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Est. Charging Cost:")
            st.write(f"{chargingCost:.2f} €")
        with col2:
            st.write("Est. Cost per kWh:")
            st.write(f"{costPerKWh:.2f} €/kWh")
