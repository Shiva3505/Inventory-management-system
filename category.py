from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymysql


def category_page(root, mycursor, conn):
    # functionality Part

    def id_exists(id):
        mycursor.execute('SELECT COUNT(*) FROM category_data WHERE id=%s', id)
        result = mycursor.fetchone()
        return result[0] > 0

    def treeview_data():
        mycursor.execute('SELECT * from category_data')
        categories = mycursor.fetchall()
        treeview.delete(*treeview.get_children())
        for category in categories:
            treeview.insert('', END, values=category)

    def clear():
        categoryIdEntry.config(state=NORMAL)
        categoryIdEntry.delete(0, END)
        categoryNameEntry.delete(0, END)
        descriptionText.delete(1.0, END)

    def delete_data():
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showerror('Error', 'Select data to delete', parent=category_window)
        else:
            result = messagebox.askyesno('Confirm', 'Do you really want to delete?', parent=category_window)
            if result:
                item = treeview.item(selected_item)
                category_id = item['values'][0]
                mycursor.execute('DELETE FROM category_data WHERE id=%s', category_id)
                conn.commit()
                treeview_data()
                clear()
                messagebox.showinfo('Success', 'Data is deleted', parent=category_window)

    def add_data():
        if not (
                categoryIdEntry.get() and categoryNameEntry.get() and descriptionText.get(1.0, END).strip()):
            messagebox.showerror('Error', 'All fields are required', parent=category_window)
        elif id_exists(categoryIdEntry.get()):
            messagebox.showerror('Error', 'Id already exists', parent=category_window)
        else:
            mycursor.execute('INSERT INTO category_data VALUES (%s,%s,%s)', (
                categoryIdEntry.get(), categoryNameEntry.get(), descriptionText.get(1.0, END)))
            conn.commit()
            treeview_data()
            messagebox.showinfo('Success', 'Data is saved', parent=category_window)
            clear()

    # Frame
    category_window = Frame(root, width=1070, height=567, bg='white')
    category_window.place(x=200, y=100)

    backImage = PhotoImage(file='back.png')
    backButton = Button(category_window, image=backImage, bd=0, bg='white', cursor='hand2',
                        command=lambda: category_window.destroy())
    backButton.image = backImage
    backButton.place(x=10, y=50)

    titleLabel = Label(category_window, text='Manage Product Category', font=('Arial', 15, 'bold'), bg='#0f4d7d',
                       fg='white')
    titleLabel.place(x=0, y=0, relwidth=1)

    logo = PhotoImage(file='product_category.png')
    label = Label(category_window, image=logo, bg='white')
    label.image = logo
    label.place(x=30, y=120)

    # details frame
    detailsFrame = Frame(category_window, bg='white')
    detailsFrame.place(x=500, y=60)

    categoryIdLabel = Label(detailsFrame, text='ID', font=('times new roman', 13), bg='white')
    categoryIdLabel.grid(row=0, column=0, padx=20, pady=10, sticky='w')
    categoryIdEntry = Entry(detailsFrame, font=('times new roman', 13), bg='lightyellow', width=26)
    categoryIdEntry.grid(row=0, column=1, padx=20, pady=10, sticky='w')

    categoryNameLabel = Label(detailsFrame, text='Category ', font=('times new roman', 13), bg='white')
    categoryNameLabel.grid(row=1, column=0, padx=20, pady=10, sticky='w')
    categoryNameEntry = Entry(detailsFrame, font=('times new roman', 13), bg='lightyellow', width=26)
    categoryNameEntry.grid(row=1, column=1, padx=20, pady=10, sticky='w')

    descriptionLabel = Label(detailsFrame, text='Description', font=('times new roman', 13), bg='white')
    descriptionLabel.grid(row=2, column=0, padx=20, pady=10, sticky='nw')
    descriptionText = Text(detailsFrame, width=30, height=5, font=('times new roman', 12), bg='lightyellow')
    descriptionText.grid(row=2, column=1, padx=20, pady=10, sticky='w')

    # buttons
    buttonFrame = Frame(category_window, bg='white')
    buttonFrame.place(x=665, y=280)

    addButton = Button(buttonFrame, text='Add', font=('times new roman', 12, 'bold'), width=8, fg='white',
                       bg='#0f4d7d', cursor='hand2', command=add_data)
    addButton.grid(row=0, column=0, padx=8)

    deleteButton = Button(buttonFrame, text='Delete', font=('times new roman', 12, 'bold'), width=8, fg='white',
                          bg='#0f4d7d', cursor='hand2', command=delete_data)
    deleteButton.grid(row=0, column=2, padx=8)

    treeviewFrame = Frame(category_window, bg='white')
    treeviewFrame.place(x=530, y=340, height=200,width=500)

    scrolly = Scrollbar(treeviewFrame, orient=VERTICAL)
    scrollx = Scrollbar(treeviewFrame, orient=HORIZONTAL)

    treeview = ttk.Treeview(treeviewFrame, columns=('id', 'name', 'description'), yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)

    scrolly.config(command=treeview.yview)
    scrollx.config(command=treeview.xview)
    treeview.pack(fill=BOTH, expand=1)
    treeview.heading('id', text='Id')
    treeview.heading('name', text='Category ')
    treeview.heading('description', text='Description')

    treeview.column('id', width=80)
    treeview.column('name', width=120)
    treeview.column('description', width=320)
    treeview['show'] = 'headings'

    treeview_data()
    return category_window, mycursor
