import streamlit as st
import pandas as pd
import plotly.express as px

# Load CSV
uploaded_file = st.file_uploader("Upload Alert CSV", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Convert dates
    for col in ["created_at", "acknowledged_at", "resolved_at"]:
        df[col] = pd.to_datetime(df[col], format="%d/%m/%y %H:%M", errors='coerce')

    # Convert TTR to minutes
    df["TTR (mins)"] = df["ttr (ms)"] / 60000

    # Extract hour of day from created_at
    df["created_hour"] = df["created_at"].dt.hour

    # Filters
    st.title("🔔 Alert Dashboard - Last 7 Days")
    services = st.multiselect("Filter by Service", df["service"].dropna().unique(), default=df["service"].dropna().unique())

    filtered = df[df["service"].isin(services)]

    # Charts
    st.subheader("🕒 Average TTR")
    avg_ttr = filtered["TTR (mins)"].mean()
    st.metric("Average TTR (mins)", f"{avg_ttr:.2f}")

    st.subheader("📊 Alerts per Service")
    fig2 = px.histogram(filtered, x="service", color="service", title="Alert Volume per Service")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📅 Alerts Over Time")
    fig3 = px.histogram(filtered, x="created_at", nbins=30, title="Alert Trend by Created Time")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🕒 Busiest Hours of the Day (by Alert Creation)")
    fig5 = px.histogram(filtered, x="created_hour", nbins=24, title="Alerts by Hour of Day", labels={"created_hour": "Hour of Day"})
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("🔁 Most Frequently Triggered Alerts")
    if "title" in df.columns and "id" in df.columns and "service" in df.columns:
        top_alerts = filtered.groupby(["title", "service"]).agg({"id": ["count", "first"]}).reset_index()
        top_alerts.columns = ["Alert Title", "Service", "Count", "Sample ID"]
        top_alerts = top_alerts.sort_values(by="Count", ascending=False).head(10)
        top_alerts["Sample Alert URL"] = top_alerts["Sample ID"].apply(lambda x: f"[Link](https://app.squadcast.com/incident/{x})")
        st.markdown("### Top 10 Alerts with Sample Links")
        st.write(top_alerts[["Alert Title", "Service", "Count", "Sample Alert URL"]].to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.warning("'title', 'service' or 'id' column not found in the CSV.")

    # Raw Data Table
    with st.expander("📄 Show Filtered Raw Data"):
        st.dataframe(filtered)
else:
    st.info("Please upload a CSV file to begin.")
