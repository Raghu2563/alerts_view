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
    assignees = st.multiselect("Filter by Assignee", df["assignee"].dropna().unique(), default=df["assignee"].dropna().unique())
    services = st.multiselect("Filter by Service", df["service"].dropna().unique(), default=df["service"].dropna().unique())

    filtered = df[df["assignee"].isin(assignees) & df["service"].isin(services)]

    # Charts
    st.subheader("🕒 Average TTR by Assignee")
    avg_ttr = filtered.groupby("assignee")["TTR (mins)"].mean().reset_index()
    fig1 = px.bar(avg_ttr, x="assignee", y="TTR (mins)", color="assignee", text_auto=".2s")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 Alerts per Service")
    fig2 = px.histogram(filtered, x="service", color="service", title="Alert Volume per Service")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📅 Alerts Over Time")
    fig3 = px.histogram(filtered, x="created_at", nbins=30, title="Alert Trend by Created Time")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("👥 Alert Count per Assignee")
    fig4 = px.histogram(filtered, x="assignee", color="assignee", title="Alert Distribution")
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("🕒 Busiest Hours of the Day (by Alert Creation)")
    fig5 = px.histogram(filtered, x="created_hour", nbins=24, title="Alerts by Hour of Day", labels={"created_hour": "Hour of Day"})
    st.plotly_chart(fig5, use_container_width=True)

    # Raw Data Table
    with st.expander("📄 Show Filtered Raw Data"):
        st.dataframe(filtered)
else:
    st.info("Please upload a CSV file to begin.")
