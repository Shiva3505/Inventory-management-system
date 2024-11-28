import os
import smtplib
import pymysql
import streamlit as st
from datetime import datetime
import email_password


# Database connection
def connection():
    try:
        conn = pymysql.connect(host='localhost', user='root', password='Shiva3505@')
        mycursor = conn.cursor()
        mycursor.execute('CREATE DATABASE IF NOT EXISTS inventory_data5')
        mycursor.execute('USE inventory_data5')

        # Create tables
        mycursor.execute(
            '''CREATE TABLE IF NOT EXISTS sup_data (
                invoice INT AUTO_INCREMENT PRIMARY KEY, 
                name VARCHAR(20), 
                contact VARCHAR(10), 
                description VARCHAR(100)
            )'''
        )
        mycursor.execute(
            '''CREATE TABLE IF NOT EXISTS emp_data (
                empid INT AUTO_INCREMENT PRIMARY KEY, 
                name VARCHAR(20), 
                email VARCHAR(30), 
                gender VARCHAR(9), 
                dob DATE, 
                contact INT, 
                employment_type VARCHAR(20), 
                education VARCHAR(20), 
                work_shift VARCHAR(20), 
                address VARCHAR(100), 
                doj DATE, 
                salary INT, 
                usertype VARCHAR(20), 
                password VARCHAR(20)
            )'''
        )
        mycursor.execute(
            '''CREATE TABLE IF NOT EXISTS product_data (
                id INT AUTO_INCREMENT PRIMARY KEY, 
                category VARCHAR(20), 
                supplier VARCHAR(20), 
                name VARCHAR(20), 
                price INT, 
                discount INT,
                price_after_discount INT, 
                quantity INT, 
                status VARCHAR(10)
            )'''
        )
        mycursor.execute(
            '''CREATE TABLE IF NOT EXISTS sales (
                sale_id INT AUTO_INCREMENT PRIMARY KEY, 
                product_id INT, 
                product_name VARCHAR(100),
                quantity_sold INT, 
                sale_date DATE, 
                sale_amount DECIMAL(10, 2), 
                FOREIGN KEY (product_id) REFERENCES product_data(id)
            )'''
        )
        mycursor.execute(
            '''CREATE TABLE IF NOT EXISTS settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tax_percentage FLOAT
            )'''
        )
        return conn, mycursor
    except Exception as e:
        st.error("Failed to connect to the database. Please start MySQL and try again.")
        return None, None


# Send OTP via email
def send_email(to_, name):
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        email_ = email_password.myemail
        password_ = email_password.mypassword
        s.login(email_, password_)
        otp = datetime.now().strftime('%H%M%S')
        subj = 'StockApp - One Time Password'
        msg = f'Dear {name},\n\nYour OTP is {otp}.\n\nWith Regards,\nStockApp Team'
        s.sendmail(email_, to_, f'Subject:{subj}\n\n{msg}')
        return otp
    except Exception as e:
        st.error("Failed to send email. Please check your internet connection or email configuration.")
        return None


# App layout and functionality
def main():
    conn, mycursor = connection()
    if not conn or not mycursor:
        return

    st.title("Inventory Management System")
    st.sidebar.image("login.png", width=100)
    st.sidebar.write("Please log in to continue.")

    emp_id = st.text_input("Employee ID", key="emp_id")
    password = st.text_input("Password", type="password", key="password")
    if st.button("Login"):
        if not emp_id or not password:
            st.error("Employee ID and Password are required.")
        else:
            mycursor.execute('SELECT usertype FROM emp_data WHERE empid=%s AND password=%s', (emp_id, password))
            user = mycursor.fetchone()
            if user:
                st.success(f"Welcome! Login successful as {user[0]}.")
                os.environ['EMP_ID'] = emp_id
                if user[0] == 'Admin':
                    st.write("Redirecting to Admin Dashboard...")
                    import admin
                else:
                    st.write("Redirecting to Billing Dashboard...")
            else:
                st.error("Invalid Employee ID or Password.")

    if st.button("Forgot Password?"):
        st.subheader("Password Reset")
        emp_id_fp = st.text_input("Enter your Employee ID", key="emp_id_fp")
        if st.button("Send OTP"):
            if emp_id_fp:
                mycursor.execute('SELECT email, name FROM emp_data WHERE empid=%s', (emp_id_fp,))
                result = mycursor.fetchone()
                if result:
                    email, name = result
                    otp = send_email(email, name)
                    if otp:
                        st.success("OTP sent to your registered email.")
                        otp_input = st.text_input("Enter OTP", key="otp_input")
                        new_password = st.text_input("New Password", type="password", key="new_password")
                        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
                        if st.button("Submit"):
                            if new_password == confirm_password:
                                mycursor.execute(
                                    'UPDATE emp_data SET password=%s WHERE empid=%s',
                                    (new_password, emp_id_fp)
                                )
                                conn.commit()
                                st.success("Password reset successfully.")
                            else:
                                st.error("Passwords do not match.")
                    else:
                        st.error("Failed to send OTP. Please try again.")
                else:
                    st.error("Invalid Employee ID.")
            else:
                st.error("Employee ID is required.")


if __name__ == "__main__":
    main()
