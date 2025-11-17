# ==========================================================
# EV Charging Optimization App – Enhanced Version
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------- Streamlit Config --------------------
st.set_page_config(
    page_title="EV Charging Optimization Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Load Dataset --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("malaysia_ev_charging_data_clean.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day_name()
    return df

df = load_data()

# -------------------- Peak/Off-Peak Logic --------------------
PEAK_START, PEAK_END = 19, 22
PEAK_RATE, OFFPEAK_RATE = 0.60, 0.40

def tariff(hour):
    if PEAK_START <= hour <= PEAK_END:
        return PEAK_RATE, "PEAK"
    return OFFPEAK_RATE, "OFF-PEAK"

# -------------------- Sidebar --------------------
st.sidebar.title("⚙️ Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Prediction", "Alerts & What-If Scenario",
                                        "Report Summary", "Charging Planner"])
st.sidebar.markdown("---")
st.sidebar.caption("EV Optimization App © Group Delta")

# -------------------- Custom CSS --------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
    }
    h1,h2,h3,h4,h5,h6 {
        color: #0F172A !important;
        font-family: 'Segoe UI', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 1️⃣ DASHBOARD
# ==========================================================
if page == "Dashboard":
    st.title("📊 EV Charging Dashboard")
    st.markdown("This dashboard visualizes Malaysia’s EV charging behavior, showing key energy usage patterns, peak hours, and charger preferences.")

    # KPI DATA
    peak_hour = df.groupby("hour")["kWh_used"].sum().idxmax()
    avg_cost = df["estimated_cost_RM"].mean()
    top_location = df["location"].value_counts().idxmax()

    # -------------------- KPI CARDS (NEW STYLE) --------------------
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
        <div style='background:#F8FAFC; padding:15px; border-radius:12px; 
        text-align:center; border:1px solid #CBD5E1;'>
            <h4 style='margin-bottom:0;'>⏰ Peak Hour</h4>
            <h2 style='margin-top:5px;'>{peak_hour}:00</h2>
        </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
        <div style='background:#F8FAFC; padding:15px; border-radius:12px; 
        text-align:center; border:1px solid #CBD5E1;'>
            <h4 style='margin-bottom:0;'>💰 Avg Cost/Session</h4>
            <h2 style='margin-top:5px;'>RM {avg_cost:.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
        <div style='background:#F8FAFC; padding:15px; border-radius:12px; 
        text-align:center; border:1px solid #CBD5E1;'>
            <h4 style='margin-bottom:0;'>📍 Top Location</h4>
            <h2 style='margin-top:5px;'>{top_location}</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # CHART SECTION
    colA, colB = st.columns(2)

    with colA:
        st.subheader("🔹 Charging Sessions by Hour")
        hourly = df["hour"].value_counts().sort_index()
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        ax1.plot(hourly.index, hourly.values, marker="o", color="#E63946")
        ax1.set_xlabel("Hour of Day")
        ax1.set_ylabel("Number of Sessions")
        ax1.set_title("EV Charging Frequency by Hour")
        st.pyplot(fig1)

    with colB:
        st.subheader("🔹 Fast vs Normal Charger Usage")
        charger = df["charger_type"].value_counts()
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        sns.barplot(x=charger.index, y=charger.values, palette="Greens", ax=ax2)
        ax2.set_xlabel("Charger Type")
        ax2.set_ylabel("Count")
        ax2.set_title("Charger Type Distribution")
        st.pyplot(fig2)

    st.markdown("---")

    st.subheader("🔹 Average Energy Usage by Day and Hour")
    pivot = df.pivot_table(values="kWh_used", index="day", columns="hour", aggfunc="mean")
    ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex(ordered_days)

    fig3, ax3 = plt.subplots(figsize=(8, 3))
    sns.heatmap(pivot, cmap="OrRd", ax=ax3)
    ax3.set_title("Energy Usage Heatmap (kWh)")
    st.pyplot(fig3)

# ==========================================================
# 2️⃣ PREDICTION
# ==========================================================
elif page == "Prediction":
    st.title("🧠 Smart Charging Recommendation")

    selected_hour = st.slider("Select your intended charging hour (0–23):", 0, 23, 18)
    cost, status = tariff(selected_hour)

    if status == "PEAK":
        st.error(f"⚠️ {selected_hour}:00 is a PEAK hour! Grid load & cost are higher.")
        suggestion = "💡 Try charging between 12AM–5AM for lower tariffs."
    else:
        st.success(f"✅ {selected_hour}:00 is OFF-PEAK. Cost & grid efficiency are better.")
        suggestion = "⚡ Excellent time slot! Continue charging during off-peak hours."

    st.metric(label="Estimated Tariff (RM/kWh)", value=f"{cost:.2f}")
    st.markdown(suggestion)

# ==========================================================
# 3️⃣ ALERTS & WHAT-IF
# ==========================================================
elif page == "Alerts & What-If Scenario":
    st.title("⚠️ Alerts & What-If Scenario")

    st.subheader("🔔 Peak Hour Detection")
    selected_time = st.slider("Select charging start time:", 0, 23, 17)
    cost, status = tariff(selected_time)

    if status == "PEAK":
        st.error(f"⚠️ {selected_time}:00 is PEAK. Avoid to reduce cost.")
    else:
        st.success(f"✅ {selected_time}:00 is OFF-PEAK — cheaper & better for the grid.")

    st.metric("Estimated Cost (RM/kWh)", f"{cost:.2f}")

    st.markdown("---")
    st.subheader("⚙️ What-If Cost Simulator")
    hour = st.slider("Select charging hour:", 0, 23, 10, key="hour_slider")
    kwh = st.number_input("Enter energy to charge (kWh):", 1, 100, 30, key="kwh_input")

    cost, status = tariff(hour)
    total_cost = kwh * cost
    st.metric(label=f"Estimated Cost for {kwh} kWh", value=f"RM {total_cost:.2f}")

# ==========================================================
# 4️⃣ REPORT SUMMARY
# ==========================================================
elif page == "Report Summary":
    st.title("📘 Report Summary – Data Insights & Recommendations")

    avg_consumption = df['kWh_used'].mean()
    peak_hours = df.groupby('hour')['kWh_used'].sum().idxmax()
    fast_usage = df[df['charger_type'] == 'Fast Charger']['kWh_used'].sum()
    normal_usage = df[df['charger_type'] == 'Normal Charger']['kWh_used'].sum()
    top_location = df.groupby('location')['kWh_used'].sum().idxmax()

    st.header("🔹 Charging Data Insights")
    st.write(f"**Average Consumption:** {avg_consumption:.2f} kWh")
    st.write(f"**Peak Hour (kWh usage):** {peak_hours}:00")
    st.write(f"**Fast Charger Total Usage:** {fast_usage:.2f} kWh")
    st.write(f"**Normal Charger Total Usage:** {normal_usage:.2f} kWh")
    st.write(f"**Most Active Location:** {top_location}")

    st.markdown("---")
    st.markdown("### 🔍 Interpretation & Recommendations")
    st.markdown("""
        - Users mostly charge after work, especially **6 PM – 10 PM**, causing congestion.
        - Encouraging **off-peak charging (10 PM – 5 AM)** helps stabilize the grid.
        - Fast chargers are concentrated in big cities; more should be placed outside Klang Valley.
        - Use tools like **charging planner**, price alerts, and prediction systems to guide users.
    """)

    st.success("✅ Data-driven insights successfully summarized.")

# ==========================================================
# 5️⃣ CHARGING PLANNER (UPDATED)
# ==========================================================
elif page == "Charging Planner":
    st.title("🗓️ Charging Planner & Cost Estimation")
    st.info("💡 Best time to charge: After 10 PM – 5 AM to avoid peak tariffs and reduce grid load.")

    normal_cost_avg = df[df['charger_type']=='Normal Charger']['estimated_cost_RM'].mean()
    fast_cost_avg = df[df['charger_type']=='Fast Charger']['estimated_cost_RM'].mean()

    # FIXED: Text now clearly visible
    col1, col2 = st.columns(2)

    col1.markdown(f"""
        <div style='background:#F8FAFC; padding:15px; border-radius:10px; 
        text-align:center; border:1px solid #CBD5E1; color:#0F172A;'>
            <h4>Normal Charger Avg Cost (RM/hr)</h4>
            <h2>{normal_cost_avg:.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
        <div style='background:#F8FAFC; padding:15px; border-radius:10px; 
        text-align:center; border:1px solid #CBD5E1; color:#0F172A;'>
            <h4>Fast Charger Avg Cost (RM/hr)</h4>
            <h2>{fast_cost_avg:.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

# -------------------- Footer --------------------
st.markdown("---")
st.caption("Developed by **Group Delta** | EV Charging Optimization Project (2025)")
