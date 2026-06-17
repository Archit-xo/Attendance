import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="💻Smart Attendance System", layout="wide")
import base64

def get_base64_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_base64_image("src/attendance/background.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
STUDENT_FILE = "students.csv"
ATTENDANCE_FILE = "attendance.csv"
IMAGE_FOLDER = "students_images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

if not os.path.exists(STUDENT_FILE):
    pd.DataFrame(columns=["Roll No", "Name", "Class", "Image Path"]).to_csv(STUDENT_FILE, index=False)

if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["Roll No", "Name", "Class", "Date", "Time", "Status"]).to_csv(ATTENDANCE_FILE, index=False)


def load_students():
    return pd.read_csv(STUDENT_FILE)


def load_attendance():
    return pd.read_csv(ATTENDANCE_FILE)


def save_student(roll, name, student_class, image):
    students = load_students()

    if str(roll) in students["Roll No"].astype(str).values:
        return "Student already registered"

    image_path = f"{IMAGE_FOLDER}/{roll}_{name}.jpg"

    with open(image_path, "wb") as file:
        file.write(image.getbuffer())

    new_student = pd.DataFrame({
        "Roll No": [roll],
        "Name": [name],
        "Class": [student_class],
        "Image Path": [image_path]
    })

    students = pd.concat([students, new_student], ignore_index=True)
    students.to_csv(STUDENT_FILE, index=False)

    return "Student registered successfully"


def mark_attendance(roll):
    students = load_students()
    attendance = load_attendance()

    student = students[students["Roll No"].astype(str) == str(roll)]

    if student.empty:
        return "Student not found"

    name = student.iloc[0]["Name"]
    student_class = student.iloc[0]["Class"]

    today = datetime.now().strftime("%d-%m-%Y")
    time_now = datetime.now().strftime("%I:%M:%S %p")

    already_marked = attendance[
        (attendance["Roll No"].astype(str) == str(roll)) &
        (attendance["Date"] == today)
    ]

    if not already_marked.empty:
        return "Attendance already marked today"

    new_attendance = pd.DataFrame({
        "Roll No": [roll],
        "Name": [name],
        "Class": [student_class],
        "Date": [today],
        "Time": [time_now],
        "Status": ["Present"]
    })

    attendance = pd.concat([attendance, new_attendance], ignore_index=True)
    attendance.to_csv(ATTENDANCE_FILE, index=False)

    return f"Attendance marked for {name}"


st.title("Smart Attendance System")
menu = st.sidebar.selectbox(
    "Select Option",
    ["🏠Home", "📒Register Student", "🖊️Mark Attendance", "🧑‍🎓View Students", "📖View Attendance", "Dashboard"]
)

if menu == "🏠Home":
    st.header("🏠Home")
    st.write("Welcome to Smart Attendance System")
    st.info("First register a student, then mark attendance.")

elif menu == "📒Register Student":
    st.header("📒Register Student")

    roll = st.text_input("Enter Roll Number")
    name = st.text_input("Enter Student Name")
    student_class = st.text_input("Enter Class")
    image = st.camera_input("Capture Student Image")

    if st.button("Save Student"):
        if roll == "" or name == "" or student_class == "":
            st.warning("Please fill all details")
        elif image is None:
            st.warning("Please capture image")
        else:
            message = save_student(roll, name, student_class, image)
            st.success(message)

elif menu == "🖊️Mark Attendance":
    st.header("🖊️Mark Attendance")

    students = load_students()

    if students.empty:
        st.warning("No students registered")
    else:
        roll_list = students["Roll No"].astype(str).tolist()
        selected_roll = st.selectbox("Select Roll Number", roll_list)

        student = students[students["Roll No"].astype(str) == selected_roll]

        st.write("Name:", student.iloc[0]["Name"])
        st.write("Class:", student.iloc[0]["Class"])

        image_path = student.iloc[0]["Image Path"]

        if os.path.exists(image_path):
            st.image(image_path, width=200)

        if st.button("Mark Present"):
            message = mark_attendance(selected_roll)
            st.success(message)

elif menu == "🧑‍🎓View Students":
    st.header("Registered Students")

    students = load_students()

    if students.empty:
        st.warning("No students found")
    else:
        st.dataframe(students, use_container_width=True)

elif menu == "📖View Attendance":
    st.header("📖Attendance Records")

    attendance = load_attendance()

    if attendance.empty:
        st.warning("No attendance records found")
    else:
        st.dataframe(attendance, use_container_width=True)

        csv = attendance.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Attendance Report",
            data=csv,
            file_name="attendance_report.csv",
            mime="text/csv"
        )

elif menu == "Dashboard":
    st.header("Dashboard")

    students = load_students()
    attendance = load_attendance()

    total_students = len(students)

    today = datetime.now().strftime("%d-%m-%Y")
    today_attendance = attendance[attendance["Date"] == today]

    present_today = len(today_attendance)
    absent_today = total_students - present_today

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", total_students)
    col2.metric("Present Today", present_today)
    col3.metric("Absent Today", absent_today)

    if total_students > 0:
        percentage = (present_today / total_students) * 100
        st.progress(int(percentage))
        st.write(f"Today's Attendance: {percentage:.2f}%")

    st.subheader("Today Attendance List")
    st.dataframe(today_attendance, use_container_width=True)
