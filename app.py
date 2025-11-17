# ==============================================================
# EV Charging Optimization App (Tasks 1–6)
# Group Delta | Final Complete Enhanced Version v6
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------------------
# Streamlit Configuration
# --------------------------------------------------------------
st.set_page_config(
    page_title="EV Charging Optimization Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------------
# Load Dataset
# --------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("malaysia_ev_charging_data_clean.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    return df

df = load_data()

# --------------------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------------------
st.sidebar.title("⚙️ Navigation")
page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Prediction",
        "Alerts & What-If Scenario",
        "Report Summary",
        "Charging Planner"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("EV Optimization App © Group Delta")

# --------------------------------------------------------------
# Custom Styling (CSS)
# --------------------------------------------------------------
st.markdown("""
<style>
    body {
        background-color: #F9FAFB;
    }
    h1, h2, h3 {
        color: #0F172A;
        font-family: 'Segoe UI', sans-serif;
    }
    .explanation {
        color: #1E293B;
        font-size: 0.95rem;
        font-weight: 500;
    }
    .tariff-info {
        color: #111827;
        font-size: 1rem;
        font-weight: 600;
    }
    .stMetric {
        background-color: #E2E8F0;
        border-radius: 10px;
        padding: 8px;
    }
    .block-container {
        padding-top: 1rem;
    }
    div[data-testid="stSlider"], div[data-testid="stNumberInput"] label p {
        font-size: 1.05rem !important;
        font-weight: 600;
        color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------
# 1️⃣ DASHBOARD PAGE
# --------------------------------------------------------------
if page == "Dashboard":
    st.title("📊 EV Charging Dashboard")
    st.markdown("This dashboard visualizes Malaysia’s EV charging behavior.")

    # KPI DATA
    peak_hour = df.groupby("hour")["kWh_used"].sum().idxmax()
    avg_cost = df["estimated_cost_RM"].mean()
    top_location = df["location"].value_counts().idxmax()

    # KPI CARDS
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
        <div style='background:#F8FAFC; padding:15px; border-radius:12px; 
        text-align:center; border:1px solid #CBD5E1;'>
            <h4>⏰ Peak Hour</h4>
            <h2>{peak_hour}:00</h2>
        </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
        <div style='background:#F8FAFC; padding:15px; border-radius:12px; 
        text-align:center; border:1px solid #CBD5E1;'>
            <h4>💰 Avg Cost/Session</h4>
            <h2>RM {avg_cost:.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
        <div style='background:#F8FAFC; padding:15px; border-radius:12px; 
        text-align:center; border:1px solid #CBD5E1;'>
            <h4>📍 Top Location</h4>
            <h2>{top_location}</h2>
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


# --------------------------------------------------------------
# 2️⃣ PREDICTION PAGE
# --------------------------------------------------------------
elif page == "Prediction":
    st.title("🧠 Smart Charging Recommendation")
    st.markdown("Use this tool to get a **rule-based recommendation** for the best charging time based on Malaysia’s TNB peak (7PM–10PM) and off-peak hours.")

    selected_hour = st.slider("Select your intended charging hour (24-hour format):", 0, 23, 18)
    peak_start, peak_end = 19, 22
    peak_rate, offpeak_rate = 0.60, 0.40

    if peak_start <= selected_hour <= peak_end:
        st.error(f"⚠️ {selected_hour}:00 is a **PEAK hour!** Grid load & cost are higher.")
        cost = peak_rate
        suggestion = "💡 Try charging between 12AM–5AM for lower tariffs."
    else:
        st.success(f"✅ {selected_hour}:00 is an **OFF-PEAK hour.** Great for cost-saving and grid efficiency.")
        cost = offpeak_rate
        suggestion = "⚡ Excellent time slot! Continue charging during off-peak hours."

    st.metric(label="Estimated Tariff (RM/kWh)", value=f"{cost:.2f}")
    st.markdown(f"<p class='explanation'>{suggestion}</p>", unsafe_allow_html=True)
    st.markdown("<p class='tariff-info'>ℹ️ Tariff rates simulated based on simplified TNB structure (RM 0.60 peak | RM 0.40 off-peak).</p>", unsafe_allow_html=True)

# --------------------------------------------------------------
# 3️⃣ & 4️⃣ ALERTS + WHAT-IF SCENARIOS
# --------------------------------------------------------------
elif page == "Alerts & What-If Scenario":
    st.title("⚠️ Alerts & What-If Scenario")
    st.markdown("Simulate cost differences between **peak** and **off-peak** charging hours to understand potential savings.")

    peak_start, peak_end = 18, 22
    peak_cost, offpeak_cost = 0.60, 0.35

    st.subheader("🔔 Peak Hour Detection")
    selected_time = st.slider("Select your charging start time (24-hour format):", 0, 23, 17)
    if peak_start <= selected_time < peak_end:
        st.error(f"⚠️ {selected_time}:00 is a PEAK hour! Avoid to reduce cost.")
        st.metric("Estimated Cost (RM/kWh)", f"{peak_cost:.2f}")
    else:
        st.success(f"✅ {selected_time}:00 is OFF-PEAK — cheaper & better for the grid.")
        st.metric("Estimated Cost (RM/kWh)", f"{offpeak_cost:.2f}")

    st.markdown("---")
    st.subheader("⚙️ What-If Cost Simulator")
    hour = st.slider("Select charging hour:", 0, 23, 10, key="hour_slider")
    kwh = st.number_input("Enter energy to charge (kWh):", 1, 100, 30, key="kwh_input")

    cost = kwh * (peak_cost if peak_start <= hour < peak_end else offpeak_cost)
    st.metric(label=f"Estimated Cost for {kwh} kWh", value=f"RM {cost:.2f}")

    hours = np.arange(0, 24)
    costs = [peak_cost if peak_start <= h < peak_end else offpeak_cost for h in hours]
    fig4, ax4 = plt.subplots(figsize=(7,2.8))
    ax4.plot(hours, costs, marker="o", color="#FF8C00")
    ax4.axvspan(peak_start, peak_end, color="red", alpha=0.2, label="Peak Hours")
    ax4.set_xlabel("Hour of Day")
    ax4.set_ylabel("Cost (RM/kWh)")
    ax4.set_title("Cost Comparison Across 24 Hours")
    ax4.legend()
    st.pyplot(fig4)
    st.markdown("<p class='explanation'>📊 <b>Insight:</b> The shaded red area represents peak hours (6PM–10PM). Charging outside this window can save RM 5–15 per session.</p>", unsafe_allow_html=True)

# --------------------------------------------------------------
# 5️⃣ REPORT SUMMARY (Insights + Interpretation + Recommendations)
# --------------------------------------------------------------
elif page == "Report Summary":
    st.title("📘 Report Summary – Data Insights & Recommendations")
    st.markdown("This section summarizes key insights, interpretations, and actionable recommendations from the EV charging dataset.")

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
- Users mainly charge in the **evening after work**, causing grid congestion during peak hours.
- Encouraging **off-peak charging (10 PM – 5 AM)** can significantly reduce electricity costs and grid stress.
- **Fast charger usage** remains concentrated in major cities like Kuala Lumpur and Selangor.
- Recommended solutions:
  - Introduce **charging planner & alert systems** (as implemented in this app).
  - Encourage fast charger installation in **non-urban locations**.
  - Offer **incentive programs** for consistent off-peak charging.
""")

    st.markdown("### 🌱 Expected Impact")
    st.markdown("""
Implementing these recommendations can:
- Reduce EV charging costs by **15–25%**
- Support **grid efficiency** and sustainable energy management
- Promote **balanced infrastructure use** across Malaysia
""")
    st.success("✅ Data-driven insights successfully summarized.")

# --------------------------------------------------------------
# 6️⃣ CHARGING PLANNER
# --------------------------------------------------------------
elif page == "Charging Planner":
    st.title("🗓️ Charging Planner & Cost Estimation")
    st.markdown("This tool suggests ideal charging times and cost estimates based on the analyzed data.")

    normal_cost = df[df['charger_type'] == 'Normal Charger']['estimated_cost_RM'].mean()
    fast_cost = df[df['charger_type'] == 'Fast Charger']['estimated_cost_RM'].mean()

    st.subheader("🔹 Recommended Charging Window")
    st.info("💡 Best time to charge: **After 10 PM to 5 AM** to avoid peak tariffs and reduce grid load.")
    st.metric("Normal Charger Avg Cost (RM/hr)", f"{normal_cost:.2f}")
    st.metric("Fast Charger Avg Cost (RM/hr)", f"{fast_cost:.2f}")

    st.markdown("---")
    st.caption("Planner based on Malaysian EV data | Developed by Group Delta (2025)")

# --------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------
st.markdown("---")
st.caption("Developed by **Group Delta** | EV Charging Optimization Project (2025) | Built using Streamlit")
