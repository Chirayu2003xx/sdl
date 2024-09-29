import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd
import smtplib
from email.mime.text import MIMEText

# Streamlit configurations
st.set_page_config(page_title="Student Lookup App", layout="wide")

# Database connection settings
hostname = 'localhost'
database = 'sdl2'
username = 'postgres'
pwd = 'Chirayu2003&'
port_id = 5432

# Load the converted Excel file (.xlsx) containing roll_no and email data
def load_email_data(file_path):
    # Read the Excel file and strip whitespace from the column names
    email_df = pd.read_excel(file_path)
    email_df.columns = email_df.columns.str.strip()  # Clean column names

    email_dict = dict(zip(email_df['Enrollment Number'], email_df['Email']))
    return email_dict

# Send an email to the student
def send_email(to_email, subject, body):
    sender_email = "chirayu2003trivedi@gmail.com"
    sender_password = "aoww tcfz lbof jsbx"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# Function to get a student's details from the List table
def get_student_details(roll_no):
    conn = None
    cur = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=hostname,
            user=username,
            dbname=database,
            password=pwd,
            port=port_id
        )
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Query the List table for the given roll number
        cur.execute("SELECT * FROM List WHERE roll_no = %s", (roll_no,))
        student = cur.fetchone()

        # If the student exists, return the details
        if student:
            return student
        else:
            return None

    except Exception as error:
        st.error(f"An error occurred: {error}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Load email data from the converted Excel file (replace 'emails.xlsx' with your actual file path)
email_data = load_email_data("/Users/chirayutrivedi/Desktop/sdl/emails.xlsx")

# Streamlit UI
st.title("Student Lookup")

# Student Lookup Section
st.subheader("Enter a Roll Number to Retrieve Student Information")
roll_no_input = st.text_input("Enter Roll Number:")

if roll_no_input:
    student_data = get_student_details(roll_no_input)
    
    if student_data:
        # Display the student's details
        st.write(f"**Roll Number**: {student_data['roll_no']}")
        st.write(f"**KT in Semester 1**: {student_data['ktsem1']}")
        st.write(f"**KT in Semester 2**: {student_data['ktsem2']}")
        st.write(f"**KT in Semester 3**: {student_data['ktsem3']}")
        st.write(f"**KT in Semester 4**: {student_data['ktsem4']}")
        st.write(f"**Total KT Count**: {student_data['kt_count']}")

        # Calculate the result based on KT count
        result = "SEM BACK" if student_data['kt_count'] > 5 else "Can Go To Next Sem"
        st.write(f"**Result**: {result}")

        # Fetch the student's email from the Excel file using the 'Enrollment Number'
        student_email = email_data.get(roll_no_input)

        if student_email:
            # Send the result to the student's email
            email_body = f"""
            Dear Student,

            Here are your semester-wise KT details:
            - KT in Semester 1: {student_data['ktsem1']}
            - KT in Semester 2: {student_data['ktsem2']}
            - KT in Semester 3: {student_data['ktsem3']}
            - KT in Semester 4: {student_data['ktsem4']}
            - Total KT Count: {student_data['kt_count']}
            - Result: {result}

            Best regards,
            SGSITS
            """

            if send_email(student_email, "Your Academic Details", email_body):
                st.success(f"Details sent to {student_email}")
            else:
                st.error("Failed to send the email.")
        else:
            st.warning("No email found for this roll number.")
    else:
        st.warning("Roll number not found.")