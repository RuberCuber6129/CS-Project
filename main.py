import streamlit as st
import sqlite3
import pandas as pd

# Connect to SQLite database (creates file if it doesn't exist)
connection = sqlite3.connect("clinicDB.db")
cursor = connection.cursor()

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Student School Data", "Student Contact Data", "About"]
)

st.title("Mayoor Clinic Website")
st.divider()
st.logo("download.png")

if page == "Home":
    st.subheader("🏥 Welcome to Mayoor Clinic")
    st.write("Use the navigation bar on the left to explore different sections.")

elif page == "Student School Data":
    st.subheader("📘 Student School Data")
    try:
        cursor.execute("SELECT * FROM student_school")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}\nTable `student_school` might not exist.")

elif page == "Student Contact Data":
    st.subheader("☎️ Student Contact Data")
    try:
        cursor.execute("SELECT * FROM student_contact")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error: {e}\nTable `student_contact` might not exist.")

elif page == "About":
    st.subheader("ℹ️ About")
    st.write("This is a demo clinic management system built with Streamlit and SQLite.")
