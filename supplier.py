from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymysql


def supplier_page(root, mycursor, conn):
    # functionality Part

    def id_exists(id):
        mycursor.execute('SELECT COUNT(*) FROM sup_data WHERE invoice=%s', id)
        result = mycursor.fetchone()
        return result[0] > 0

    def select_data(event):
        selected = treeview.selection()
        content = treeview.item(selected)
        if content['values']:
            row = content['values']
            clear()
            invoiceEntry.insert(0, row[0])
            invoiceEntry.config(state='readonly')
            suppliernameEntry.insert(0, row[1])
            contactEntry.insert(0, row[2])
            descriptionText.insert(1.0, row[3])

    def treeview_data():
        mycursor.execute('SELECT * from sup_data')
        suppliers = mycursor.fetchall()
        treeview.delete(*treeview.get_children())
        for supply in suppliers:
            treeview.insert('', END, values=supply)

    def clear(value=False):
        if value:
            treeview.selection_remove(treeview.selection())
        invoiceEntry.config(state=NORMAL)
        invoiceEntry.delete(0, END)
        suppliernameEntry.delete(0, END)
        contactEntry.delete(0, END)
        descriptionText.delete(1.0, END)

    def delete_data():
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showerror('Error', 'Select data to delete', parent=supplier_window)
        else:
            result = messagebox.askyesno('Confirm', 'Do you really want to delete?', parent=supplier_window)
            if result:
                mycursor.execute('DELETE FROM sup_data WHERE invoice=%s', invoiceEntry.get())
                conn.commit()
                treeview_data()
                clear()
                messagebox.showerror('Error', 'Data is deleted', parent=supplier_window)

    def update_data():
        selected_item = treeview.selection()

        if not selected_item:
            messagebox.showerror('Error', 'Select data to update', parent=supplier_window)
        else:
            # Get the selected item's invoice number
            invoice = invoiceEntry.get()

            # Fetch the current data for the selected item
            mycursor.execute('SELECT name, contact, description FROM sup_data WHERE invoice = %s', (invoice,))
            current_data = mycursor.fetchone()

            # Get the new data entered by the user
            new_name = suppliernameEntry.get()
            new_contact = contactEntry.get()
            new_description = descriptionText.get(1.0, END).strip()

            # Check if there are any changes
            if (current_data[0] == new_name and
                    current_data[1] == new_contact and
                    current_data[2] == new_description):
                messagebox.showinfo('Info', 'No changes detected', parent=supplier_window)
            else:
                # Update the data
                mycursor.execute(
                    'UPDATE sup_data SET name=%s, contact=%s, description=%s WHERE invoice=%s',
                    (new_name, new_contact, new_description, invoice))
                conn.commit()
                treeview_data()
                clear()
                messagebox.showinfo('Success', 'Data is updated', parent=supplier_window)

    def save_data():
        if not (
                invoiceEntry.get() and contactEntry.get() and suppliernameEntry.get() and descriptionText.get(1.0,
                                                                                                              END).strip()):
            messagebox.showerror('Error', 'All fields are required', parent=supplier_window)
        elif id_exists(invoiceEntry.get()):
            messagebox.showerror('Error', 'Id already exists', parent=supplier_window)
        else:
            mycursor.execute('INSERT INTO sup_data VALUES (%s,%s,%s,%s)', (
                invoiceEntry.get(), suppliernameEntry.get(), contactEntry.get(), descriptionText.get(1.0, END)))
            conn.commit()
            treeview_data()
            messagebox.showinfo('Success', 'Data is saved', parent=supplier_window)
            clear()

    def search():
        if searchEntry.get() == '':
            messagebox.showerror('Error', 'Enter value to search', parent=supplier_window)

        else:
            mycursor.execute(f'SELECT * FROM sup_data WHERE invoice = %s', searchEntry.get())
            result = mycursor.fetchall()
            if len(result) == 0:
                messagebox.showerror('Error', 'No record found', parent=supplier_window)
            else:
                treeview.delete(*treeview.get_children())
                for employee in result:
                    treeview.insert('', END, values=employee)

    def show_data():
        treeview_data()
        searchEntry.delete(0, END)

    def back_func():
        supplier_window.place_forget()

    # GUI
    supplier_window = Frame(root, width=1070, height=567, bg='white')
    supplier_window.place(x=200, y=100)


    titleLabel = Label(supplier_window, text='Manage Supplier Details', font=('Arial', 15, 'bold'), bg='#0f4d7d',
                       fg='white')
    titleLabel.place(x=0, y=0, relwidth=1)

    backImage = PhotoImage(file='back.png')
    backButton = Button(supplier_window, image=backImage, bd=0, bg='white', cursor='hand2', command=back_func)
    backButton.image = backImage
    backButton.place(x=10, y=50)


    leftFrame = Frame(supplier_window, bg='white')
    leftFrame.place(x=10, y=100)

    invoiceLabel = Label(leftFrame, text='Id', font=('times new roman', 13,'bold'), bg='white')
    invoiceLabel.grid(row=0, column=0, sticky='w', padx=(10, 20))
    invoiceEntry = Entry(leftFrame, font=('times new roman', 13), bg='lightyellow')
    invoiceEntry.grid(row=0, column=1, pady=20, sticky='w')

    suppliernameLabel = Label(leftFrame, text='Supplier ', font=('times new roman', 13,'bold'), bg='white')
    suppliernameLabel.grid(row=1, column=0, sticky='w', padx=(10, 20))
    suppliernameEntry = Entry(leftFrame, font=('times new roman', 13), bg='lightyellow')
    suppliernameEntry.grid(row=1, column=1, sticky='w')

    contactLabel = Label(leftFrame, text='Mobile No', font=('times new roman', 13,'bold'), bg='white')
    contactLabel.grid(row=2, column=0, sticky='w', padx=(10, 20))
    contactEntry = Entry(leftFrame, font=('times new roman', 13), bg='lightyellow')
    contactEntry.grid(row=2, column=1, pady=20, sticky='w')

    descriptionLabel = Label(leftFrame, text='Description', font=('times new roman', 13,'bold'), bg='white')
    descriptionLabel.grid(row=3, column=0, sticky='nw', padx=(10, 20))
    descriptionText = Text(leftFrame, font=('times new roman', 14), bg='lightyellow', width=40, height=8)
    descriptionText.grid(row=3, column=1)

    # buttons
    buttonFrame = Frame(supplier_window, bg='white')
    buttonFrame.place(x=140, y=470)

    saveButton = Button(buttonFrame, text='Save', font=('times new roman', 12, 'bold'), width=8, fg='white',
                        bg='#0f4d7d', cursor='hand2', command=save_data)
    saveButton.grid(row=0, column=0, padx=8)
    updateButton = Button(buttonFrame, text='Update', font=('times new roman', 12, 'bold'), width=8, fg='white',
                          bg='#0f4d7d', cursor='hand2', command=update_data)
    updateButton.grid(row=0, column=1, padx=8)
    deleteButton = Button(buttonFrame, text='Delete', font=('times new roman', 12, 'bold'), width=8, fg='white',
                          bg='#0f4d7d', cursor='hand2', command=delete_data)
    deleteButton.grid(row=0, column=2, padx=8)
    clearButton = Button(buttonFrame, text='Clear', font=('times new roman', 12, 'bold'), width=8, fg='white',
                         bg='#0f4d7d', cursor='hand2', command=lambda: clear(True))
    clearButton.grid(row=0, column=3, padx=8)

    searchFrame = Frame(supplier_window, bg='white')
    searchFrame.place(x=565, y=115)

    invoiceLabel = Label(searchFrame, text='Id', font=('times new roman', 13,'bold'), bg='white')
    invoiceLabel.grid(row=0, column=0, padx=20)
    searchEntry = Entry(searchFrame, font=('times new roman', 13), bg='lightyellow', width=14)
    searchEntry.grid(row=0, column=1)
    searchButton = Button(searchFrame, text='Search', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                          cursor='hand2', width=8, command=search)
    searchButton.grid(row=0, column=2, padx=20)

    showButton = Button(searchFrame, text='Show All', font=('times new roman', 12, 'bold'), width=8, fg='white',
                        bg='#0f4d7d', cursor='hand2', command=show_data)
    showButton.grid(row=0, column=3)

    treeviewFrame = Frame(supplier_window, bg='white')
    treeviewFrame.place(x=545, y=165, height=340,width=510)

    scrolly = Scrollbar(treeviewFrame, orient=VERTICAL)
    scrollx = Scrollbar(treeviewFrame, orient=HORIZONTAL)
    treeview = ttk.Treeview(treeviewFrame, columns=('invoice', 'name', 'contact', 'description'),
                            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack(fill=BOTH, expand=1)
    treeview.heading('invoice', text='Invoice No.')
    treeview.heading('name', text='Name')
    treeview.heading('contact', text='Contact')
    treeview.heading('description', text='Description')

    treeview.column('invoice', width=80)
    treeview.column('name', width=120)
    treeview.column('contact', width=100)
    treeview.column('description', width=240)
    treeview['show'] = 'headings'

    treeview_data()
    treeview.bind('<ButtonRelease-1>', select_data)
    return supplier_window, mycursor
