import streamlit as st
import time
import csv
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("⏳ AI Study Tracker + Progress Graph 📊")

# Setup
if 'timers' not in st.session_state:
    st.session_state.timers = {}
if 'start_times' not in st.session_state:
    st.session_state.start_times = {}

# Input Section
st.sidebar.header("📋 Enter Subjects & Time")
subjects_raw = st.sidebar.text_area("Enter one subject per line", height=150)
subjects = [s.strip() for s in subjects_raw.strip().split('\n') if s.strip()]
today = datetime.today().strftime('%Y-%m-%d')
log_file = "study_log.csv"

# Show Study Timers
st.header("📌 Live Timers")

for subject in subjects:
    col1, col2 = st.columns([3, 2])
    with col1:
        st.write(f"**{subject}**")
    with col2:
        if st.button(f"▶️ Start {subject}", key=f"start_{subject}"):
            st.session_state.start_times[subject] = time.time()
        if st.button(f"⏹ Stop {subject}", key=f"stop_{subject}"):
            if subject in st.session_state.start_times:
                elapsed = round((time.time() - st.session_state.start_times[subject]) / 60, 2)
                prev = st.session_state.timers.get(subject, 0)
                st.session_state.timers[subject] = prev + elapsed
                del st.session_state.start_times[subject]
                st.success(f"Recorded {elapsed} minutes for {subject}!")

# Show Completed Times
st.subheader("✅ Today’s Total Time")
for subject, mins in st.session_state.timers.items():
    st.write(f"**{subject}**: {round(mins, 2)} mins")

# Save Session
if st.button("💾 Save Today’s Log"):
    with open(log_file, "a", newline='') as file:
        writer = csv.writer(file)
        for subject, mins in st.session_state.timers.items():
            writer.writerow([today, subject, round(mins, 2)])
    st.success("Session saved!")

# Load & Plot History
if st.button("📊 Show Weekly Progress"):
    if os.path.exists(log_file):
        df = pd.read_csv(log_file, names=['Date', 'Subject', 'Minutes'])
        df['Date'] = pd.to_datetime(df['Date'])
        last_week = df[df['Date'] >= pd.to_datetime(today) - pd.Timedelta(days=6)]

        pivot = last_week.groupby(['Date', 'Subject'])['Minutes'].sum().unstack().fillna(0)
        st.subheader("📈 Study Time - Past 7 Days")

        fig, ax = plt.subplots(figsize=(10, 5))
        pivot.plot(kind='bar', stacked=True, ax=ax)
        plt.ylabel("Minutes")
        plt.title("Weekly Study Progress")
        st.pyplot(fig)
    else:
        st.warning("No study log found. Save at least one session first.")
