#python -m streamlit run e:/Sandbox/ChargeCalc/pages/chargecalc.py 
import streamlit as st
import pandas as pd
import math

st.title("Charge Calculator")

method = st.radio(
    "Calculation method",
    ("Use charging curve", "Enter average charging speed")
)

st.header("Battery Information")
col1, col2, col3 = st.columns(3)
with col1:
    startSoC = st.text_input("Start SoC (%)", value="20")
with col2:
    endSoC = st.text_input("End SoC (%)", value="80")
with col3:
    batteryCapacity = st.text_input("Battery Capacity (kWh)", value="66.5")

if method == "Use charging curve":
    st.header("Charger Information")
    col1, col2 = st.columns(2)
    with col1:
        chargerPower = st.text_input("Charger Power (kW)", value="150")
    with col2:
        priceMin = st.text_input("Price per minute", value="0.931")

    st.header("Charging Curve")
    ChargingCurve = pd.read_csv(r"E:\Sandbox\ChargeCalc\chargingCurves\Tesla_M3_Pannasonic3.csv")
    st.line_chart(ChargingCurve.set_index("SoC")["ChargingSpeed"])

    avgChargingSpeed = ChargingCurve.set_index("SoC")["ChargingSpeed"].loc[int(startSoC):int(endSoC)].mean()
else:
    st.header("Manual Speed")
    col1, col2 = st.columns(2)
    with col1:
        avgChargingSpeedUserInput = st.text_input("Average Charging Speed (kW)", value="150")
    with col2:
        priceMin = st.text_input("Price per minute", value="0.931")

    avgChargingSpeed = float(avgChargingSpeedUserInput)

st.header("Results")
deltaSoCPercent = int(endSoC) - int(startSoC)
deltaSoCkWh = deltaSoCPercent * float(batteryCapacity) / 100
chargingTimeMinutes = math.ceil((deltaSoCkWh / avgChargingSpeed) * 60)
chargingCost = (chargingTimeMinutes / 60) * float(priceMin) * 60

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("Avg. Charging Speed:")
    st.write(f"{avgChargingSpeed:.2f} kW")
with col2:
    st.write("Delta SoC:")
    st.write(f"{deltaSoCPercent}% ({deltaSoCkWh:.2f} kWh)")
with col3:
    st.write("Est. Charging Time:")
    st.write(f"{chargingTimeMinutes:.2f} minutes")
with col4: 
    st.write("Est. Charging Cost:")
    st.write(f"{chargingCost:.2f}€")