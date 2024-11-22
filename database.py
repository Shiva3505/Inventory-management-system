import pymysql
from tkinter import messagebox

def connect_database(database=''):
    try:
        conn = pymysql.connect(host='localhost', user='root', password='Shiva3505@',database='inventory_data5')
        mycursor = conn.cursor()
    except:
        messagebox.showerror('Error', 'Something went wrong, Please open MySQL app before running again')
        return None,None

    return mycursor, conn
