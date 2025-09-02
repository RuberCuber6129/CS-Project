import streamlit as st
import mysql.connector as mysql
import pandas as pd

connection = mysql.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="clinicDB"
)

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
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM student_school")
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=cols)
    st.dataframe(df)

elif page == "Student Contact Data":
    st.subheader("☎️ Student Contact Data")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM student_contact")
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=cols)
    st.dataframe(df)

elif page == "About":
    st.subheader("ℹ️ About")
    st.write("This is a demo clinic management system built with Streamlit and MySQL.")
