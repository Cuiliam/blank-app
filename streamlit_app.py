import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("medical_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            blood_pressure TEXT NOT NULL,
            heart_rate INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn, cursor

# Validate blood pressure input format
def validate_bp(bp):
    parts = bp.split('/')
    if len(parts) != 2:
        return False
    systolic, diastolic = parts
    if not (systolic.isdigit() and diastolic.isdigit()):
        return False
    systolic = int(systolic)
    diastolic = int(diastolic)
    return 50 <= systolic <= 250 and 30 <= diastolic <= 150

# Function to validate input fields
def validate_inputs(name, age, bp, hr):
    if not name:
        st.error("Patient name is required.")
        return False
    if not age.isdigit() or not (1 <= int(age) <= 120):
        st.error("Please enter a valid age (1-120).")
        return False
    if not validate_bp(bp):
        st.error("Please enter blood pressure in format systolic/diastolic (e.g., 120/80).")
        return False
    if not hr.isdigit() or not (30 <= int(hr) <= 200):
        st.error("Please enter a valid heart rate (30-200 bpm).")
        return False
    return True

# Submit data to the database
def submit_data(name, age, bp, hr, conn, cursor):
    cursor.execute("""
        INSERT INTO medical_data (name, age, blood_pressure, heart_rate)
        VALUES (?, ?, ?, ?)
    """, (name, int(age), bp, int(hr)))
    conn.commit()
    st.success("Data submitted successfully!")

# View submitted data as a dataframe
def view_data(cursor):
    cursor.execute("SELECT * FROM medical_data")
    records = cursor.fetchall()
    if records:
        df = pd.DataFrame(records, columns=["ID", "Name", "Age", "Blood Pressure", "Heart Rate", "Timestamp"])
        st.dataframe(df)
        return df
    else:
        st.warning("No data found.")
        return pd.DataFrame()

# Plot heart rate and blood pressure
def plot_data(df):
    if not df.empty:
        # Split blood pressure into systolic and diastolic for plotting
        df['Systolic'] = df['Blood Pressure'].apply(lambda x: int(x.split('/')[0]))
        df['Diastolic'] = df['Blood Pressure'].apply(lambda x: int(x.split('/')[1]))

        # Plot heart rate
        fig1 = px.line(df, x='Timestamp', y='Heart Rate', title='Heart Rate Over Time', markers=True)
        st.plotly_chart(fig1)

        # Plot systolic and diastolic blood pressure
        fig2 = px.line(df, x='Timestamp', y=['Systolic', 'Diastolic'], title='Blood Pressure (Systolic/Diastolic) Over Time', markers=True)
        st.plotly_chart(fig2)

# Notifications Page
def notifications_page():
    st.write("### Notifications")
    # Placeholder for future notification features
    st.info("No new notifications.")
    st.write("Here you can display any notifications or alerts related to medical data or other important updates.")

# Main Streamlit app logic
def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.selectbox("Go to", ["Data Input", "Notifications"])

    # Initialize the database
    conn, cursor = init_db()

    if selection == "Data Input":
        st.title("Senior Safe - Medical Data Input")

        # Use columns for neater input layout
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Patient Name")
            age = st.text_input("Age")

        with col2:
            bp = st.text_input("Blood Pressure (mmHg)", placeholder="e.g., 120/80")
            hr = st.text_input("Heart Rate (bpm)")

        # Submit button
        if st.button("Submit"):
            if validate_inputs(name, age, bp, hr):
                submit_data(name, age, bp, hr, conn, cursor)

        # Display submitted data
        st.write("### Submitted Medical Data")
        df = view_data(cursor)

        # Plot heart rate and blood pressure
        if not df.empty:
            st.write("### Visualizations")
            plot_data(df)

    elif selection == "Notifications":
        notifications_page()

if __name__ == "__main__":
    main()
