from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import pymysql


def employee_page(root, mycursor, conn):
    # functionality Part

    def id_exists(id):
        mycursor.execute('SELECT COUNT(*) FROM emp_data WHERE empid=%s', id)
        result = mycursor.fetchone()
        return result[0] > 0

    def select_data(event):
        selected = treeview.selection()
        content = treeview.item(selected)
        if content['values']:
            row = content['values']
            clear()
            empIdEntry.insert(0, row[0])
            empIdEntry.config(state='readonly')
            nameEntry.insert(0, row[1])
            emailEntry.insert(0, row[2])
            genderCombobox.set(row[3])
            dobDateEntry.set_date(row[4])
            contactEntry.insert(0, row[5])
            employment_typeCombobox.set(row[6])
            educationBox.set(row[7])
            work_shiftBox.set(row[8])
            addressText.insert(1.0, row[9])
            dojDateEntry.set_date(row[10])
            salaryEntry.insert(0, row[11])
            userTypecombobox.set(row[12])
            passwordEntry.insert(0, row[13])

    def treeview_data():
        mycursor.execute('SELECT * from emp_data')
        employees = mycursor.fetchall()
        treeview.delete(*treeview.get_children())
        for employee in employees:
            treeview.insert('', END, values=employee)

    def clear(value=False):
        if value:
            treeview.selection_remove(treeview.selection())
        empIdEntry.config(state=NORMAL)
        empIdEntry.delete(0, END)
        genderCombobox.current(0)
        contactEntry.delete(0, END)
        nameEntry.delete(0, END)
        from datetime import date
        dobDateEntry.set_date(date.today())
        employment_typeCombobox.current(0)
        emailEntry.delete(0, END)
        educationBox.current(0)
        work_shiftBox.current(0)
        addressText.delete(1.0, END)
        dojDateEntry.delete(0, END)
        salaryEntry.delete(0, END)
        userTypecombobox.current(0)
        passwordEntry.delete(0, END)

    def delete_data():
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showerror('Error', 'Select data to delete', parent=employee_window)
        else:
            result = messagebox.askyesno('Confirm', 'Do you really want to delete?', parent=employee_window)
            if result:
                mycursor.execute('DELETE FROM emp_data WHERE empid=%s', empIdEntry.get())
                conn.commit()
                treeview_data()
                clear()
                messagebox.showerror('Error', 'Data is deleted', parent=employee_window)

    def update_data():
        selected_item = treeview.selection()

        if not selected_item:
            messagebox.showerror('Error', 'Select data to update', parent=employee_window)

        else:
            empid = empIdEntry.get()
            gender = genderCombobox.get()
            contact = contactEntry.get()
            name = nameEntry.get()
            dob = dobDateEntry.get()
            employment_type = employment_typeCombobox.get()
            email = emailEntry.get()
            education = educationBox.get()
            work_shift = work_shiftBox.get()
            address = addressText.get(1.0, END).strip()
            doj = dojDateEntry.get()
            salary = salaryEntry.get()
            usertype = userTypecombobox.get()
            password = passwordEntry.get()

            mycursor.execute(
                'SELECT name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, usertype, password FROM emp_data WHERE empid=%s',
                (empid,))
            current_data = mycursor.fetchone()

            # New data entered by the user
            new_data = (
                name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, usertype, password)

            # Compare the fetched data with the new data
            if current_data == new_data:
                messagebox.showinfo('No Changes', 'No changes detected', parent=employee_window)
            else:

                mycursor.execute(
                    'UPDATE emp_data SET name=%s, email=%s, gender=%s, dob=%s, contact=%s, employment_type=%s, education=%s, work_shift=%s,address=%s,doj=%s,salary=%s,usertype=%s,password=%s WHERE empid=%s',
                    (name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, usertype,
                     password,
                     empid))
                conn.commit()
                treeview_data()
                clear()
                messagebox.showinfo('Success', 'Data is updated', parent=employee_window)

    def save_data():
        empid = empIdEntry.get()
        gender = genderCombobox.get()
        contact = contactEntry.get()
        name = nameEntry.get()
        dob = dobDateEntry.get()
        employment_type = employment_typeCombobox.get()
        email = emailEntry.get()
        education = educationBox.get()
        work_shift = work_shiftBox.get()
        address = addressText.get(1.0, END).strip()
        doj = dojDateEntry.get()
        salary = salaryEntry.get()
        usertype = userTypecombobox.get()
        password = passwordEntry.get()

        if not (
                empid and contact and name and dob and email and education and address and doj and salary and usertype and password):
            messagebox.showerror('Error', 'All fields are required', parent=employee_window)
        elif id_exists(empid):
            messagebox.showerror('Error', 'Id already exists', parent=employee_window)
        else:
            mycursor.execute('INSERT INTO emp_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (
                empid, name, email, gender, dob, contact, employment_type, education, work_shift, address, doj, salary, usertype,
                password))
            conn.commit()
            treeview_data()
            messagebox.showinfo('Success', 'Data is saved', parent=employee_window)
            clear()

    def search():
        if searchEntry.get() == '':
            messagebox.showerror('Error', 'Enter value to search', parent=employee_window)
        elif search_combobox.get() == 'Search By':
            messagebox.showerror('Error', 'Please select an option', parent=employee_window)
        else:
            mycursor.execute(f'SELECT * FROM emp_data WHERE {search_combobox.get()} LIKE %s',
                             '%' + searchEntry.get() + '%')
            result = mycursor.fetchall()
            if len(result) == 0:
                messagebox.showerror('Error', 'No record found', parent=employee_window)
            else:
                treeview.delete(*treeview.get_children())
                for employee in result:
                    treeview.insert('', END, values=employee)

    def show_data():
        treeview_data()
        searchEntry.delete(0, END)
        search_combobox.set('Search By')

    def back_func():
        employee_window.place_forget()

    #  gui
    employee_window = Frame(root, width=1070, height=567, bg='white')
    employee_window.place(x=200, y=100)
    titleLabel = Label(employee_window, text='Manage Employee Details', font=('Arial', 16, 'bold'), bg='#0f4d7d', fg='white')
    titleLabel.place(x=0, y=0, relwidth=1)
    backImage = PhotoImage(file='back.png')
    backButton = Button(employee_window, image=backImage, bd=0, cursor='hand2', bg='white', command=back_func)
    backButton.image = backImage
    backButton.place(x=10, y=30)



    treeviewFrame = Frame(employee_window, bg='white')
    treeviewFrame.place(x=0, y=50, relwidth=1, height=235)

    searchFrame = Frame(treeviewFrame, bg='white')
    searchFrame.pack()
    search_combobox = ttk.Combobox(searchFrame, values=('Id', 'Name', 'Email', 'employment_type', 'work_shift', 'Education', 'Salary'),
                                   state='readonly',
                                   justify=CENTER, font=('goudy old style', 12), width=15)
    search_combobox.grid(row=0, column=0, padx=20)
    search_combobox.set('Search By')
    searchEntry = Entry(searchFrame, font=('goudy old style', 12), bg='lightblue')
    searchEntry.grid(row=0, column=1)
    searchButton = Button(searchFrame, text='Search', font=('times new roman', 12,), bg='#0f4d7d', fg='white',
                          cursor='hand2', width=10, command=search)
    searchButton.grid(row=0, column=2, padx=20, pady=10)
    showButton = Button(searchFrame, text='Show All', font=('times new roman', 12), width=10, fg='white',
                        bg='#0f4d7d', cursor='hand2', command=show_data)
    showButton.grid(row=0, column=3)

    scrolly = Scrollbar(treeviewFrame, orient=VERTICAL)
    scrollx = Scrollbar(treeviewFrame, orient=HORIZONTAL)
    treeview = ttk.Treeview(treeviewFrame, columns=(
        'empid', 'name', 'email', 'gender', 'dob', 'contact', 'employment_type', 'education', 'work_shift', 'address', 'doj',
        'salary', 'usertype',),
                            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack()
    treeview.heading('empid', text='EmpId')
    treeview.heading('name', text='Name')
    treeview.heading('email', text='Email')
    treeview.heading('gender', text='Gender')
    treeview.heading('dob', text='Date of Birth')
    treeview.heading('contact', text='Mobile No')
    treeview.heading('employment_type', text='Employment Type')
    treeview.heading('education', text='Education')
    treeview.heading('work_shift', text='Work Shift')
    treeview.heading('address', text='Address')
    treeview.heading('doj', text='Date of Joining')
    treeview.heading('salary', text='Salary')
    treeview.heading('usertype', text='User Type')

    treeview.column('empid', width=60)
    treeview.column('gender', width=80)
    treeview.column('contact', width=100)
    treeview.column('name', width=140)
    treeview.column('dob', width=100)
    treeview.column('employment_type', width=140)
    treeview.column('email', width=180)
    treeview.column('education', width=100)
    treeview.column('work_shift', width=100)
    treeview.column('address', width=200)
    treeview.column('doj', width=100)
    treeview.column('salary', width=100)
    treeview.column('usertype', width=100)
    treeview['show'] = 'headings'

    # detailsframe
    detailsFrame = Frame(employee_window, bg='white')
    detailsFrame.place(x=0, y=300)

    empIdLabel = Label(detailsFrame, text='EmpId', font=('times new roman', 12), bg='white')
    empIdLabel.grid(row=0, column=0, padx=(60, 10), sticky='w')
    empIdEntry = Entry(detailsFrame, font=('times new roman', 12), bg='lightblue')
    empIdEntry.grid(row=0, column=1, pady=15)
    nameLabel = Label(detailsFrame, text='Name', font=('times new roman', 12), bg='white')
    nameLabel.grid(row=0, column=2, padx=(60, 10), sticky='w')
    nameEntry = Entry(detailsFrame, font=('times new roman', 12), bg='lightblue')
    nameEntry.grid(row=0, column=3)
    emailLabel = Label(detailsFrame, text='Email', font=('times new roman', 12), bg='white')
    emailLabel.grid(row=0, column=4, padx=(60, 10), sticky='w')
    emailEntry = Entry(detailsFrame, font=('times new roman', 12), bg='lightblue')
    emailEntry.grid(row=0, column=5)
    genderLabel = Label(detailsFrame, text='Gender', font=('times new roman', 12), bg='white')
    genderLabel.grid(row=1, column=0, padx=(60, 10), sticky='w')
    genderCombobox = ttk.Combobox(detailsFrame, values=('Male', 'Female'), font=('times new roman', 12),
                                  state='readonly', width=18)
    genderCombobox.grid(row=1, column=1)
    genderCombobox.current(0)

    dobLabel = Label(detailsFrame, text='Date of Birth', font=('times new roman', 12), bg='white')
    dobLabel.grid(row=1, column=2, padx=(60, 10), sticky='w')
    dobDateEntry = DateEntry(detailsFrame, font=('times new roman', 12), bg='lightblue', width=18, date_pattern='dd/MM/yyyy',
                         state='readonly')
    dobDateEntry.grid(row=1, column=3)
    contactLabel = Label(detailsFrame, text='Mobile No', font=('times new roman', 12), bg='white')
    contactLabel.grid(row=1, column=4, padx=(60, 10), sticky='w')
    contactEntry = Entry(detailsFrame, font=('times new roman', 12), bg='lightblue')
    contactEntry.grid(row=1, column=5)
    employment_typeLabel = Label(detailsFrame, text='Employment Type', font=('times new roman', 12), bg='white')
    employment_typeLabel.grid(row=2, column=0, padx=(60, 10), sticky='w')
    employment_typeCombobox = ttk.Combobox(detailsFrame, values=('Full Time', 'Part Time', 'Casual','Contract','Intern'),
                                  font=('times new roman', 12),
                                  state='readonly', width=18)
    employment_typeCombobox.grid(row=2, column=1, pady=15)
    employment_typeCombobox.current(0)

    educationLabel = Label(detailsFrame, text='Education', font=('times new roman', 12), bg='white')
    educationLabel.grid(row=2, column=2, padx=(60, 10), sticky='w')
    education_options = ["B.Tech", "B.Com", "M.Tech", "M.Com", "B.Sc", "M.Sc", "BBA", "MBA", "LLB", "LLM", "B.Arch",
                         "M.Arch"]
    educationBox = ttk.Combobox(detailsFrame, values=education_options, width=18, font=('times new roman', 12),
                                state='readonly')
    educationBox.grid(row=2, column=3)
    educationBox.set(education_options[0])
    work_shiftLabel = Label(detailsFrame, text='Work Shift', font=('times new roman', 12), bg='white')
    work_shiftLabel.grid(row=2, column=4, padx=(60, 10), sticky='w')
    work_shift_options = ['Morning', 'Evening', 'Night']
    work_shiftBox = ttk.Combobox(detailsFrame, values=work_shift_options, width=18, font=('times new roman', 12), state='readonly')
    work_shiftBox.grid(row=2, column=5)
    work_shiftBox.set(work_shift_options[0])

    addressLabel = Label(detailsFrame, text='Address', font=('times new roman', 12), bg='white')
    addressLabel.grid(row=3, column=0, padx=(60, 10), sticky='w')
    addressText = Text(detailsFrame, width=20, height=3, font=('times new roman', 12), bd=2,bg='lightblue')
    addressText.grid(row=3, column=1, rowspan=2)
    dojLabel = Label(detailsFrame, text='Date of Joining', font=('times new roman', 12), bg='white')
    dojLabel.grid(row=3, column=2, padx=(60, 10), sticky='w')
    dojDateEntry = DateEntry(detailsFrame, font=('times new roman', 12), bg='lightblue', width=18, date_pattern='dd/MM/yyyy',
                         state='readonly')
    dojDateEntry.grid(row=3, column=3)
    userTypeLabel = Label(detailsFrame, text='User Type', font=('times new roman', 12), bg='white')
    userTypeLabel.grid(row=4, column=2, padx=(60, 10), sticky='w', pady=(15, 0))
    userTypecombobox = ttk.Combobox(detailsFrame, font=('times new roman', 12), width=18, values=('Employee', 'Admin'),
                                    state='readonly')
    userTypecombobox.grid(row=4, column=3, pady=(15, 0))
    userTypecombobox.current(0)
    salaryLabel = Label(detailsFrame, text='Salary', font=('times new roman', 12), bg='white')
    salaryLabel.grid(row=3, column=4, padx=(60, 10), sticky='w')
    salaryEntry = Entry(detailsFrame, font=('times new roman', 12), bg='lightblue')
    salaryEntry.grid(row=3, column=5)

    passwordLabel = Label(detailsFrame, text='Password', font=('times new roman', 12), bg='white')
    passwordLabel.grid(row=4, column=4, padx=(60, 10), sticky='w', pady=(15, 0))
    passwordEntry = Entry(detailsFrame, font=('times new roman', 12), bg='lightblue')
    passwordEntry.grid(row=4, column=5, pady=(15, 0))

    # buttons
    buttonFrame = Frame(employee_window, bg='white')
    buttonFrame.place(x=260, y=520)

    saveButton = Button(buttonFrame, text='Save', font=('times new roman', 12, 'bold'), width=10, fg='white',
                        bg='#0f4d7d', cursor='hand2', command=save_data)
    saveButton.grid(row=0, column=0, padx=20)
    updateButton = Button(buttonFrame, text='Update', font=('times new roman', 12, 'bold'), width=10, fg='white',
                          bg='#0f4d7d', cursor='hand2', command=update_data)
    updateButton.grid(row=0, column=1, padx=20)
    deleteButton = Button(buttonFrame, text='Delete', font=('times new roman', 12, 'bold'), width=10, fg='white',
                          bg='#0f4d7d', cursor='hand2', command=delete_data)
    deleteButton.grid(row=0, column=2, padx=20)
    clearButton = Button(buttonFrame, text='Clear', font=('times new roman', 12, 'bold'), width=10, fg='white',
                         bg='#0f4d7d', cursor='hand2', command=lambda: clear(True))
    clearButton.grid(row=0, column=3, padx=20)


    treeview_data()
    treeview.bind('<ButtonRelease-1>', select_data)
    return employee_window, mycursor
