from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pymysql


def product_page(root, mycursor, conn):
    # functionality Part

    def select_data(event):
        selected = treeview.selection()
        content = treeview.item(selected)
        if content['values']:
            row = content['values']
            clear()
            categoryCombobox.set(row[1])
            supplierCombobox.set(row[2])
            nameEntry.insert(0, row[3])
            priceEntry.insert(0, row[4])
            discountEntry.insert(0, row[5])
            quantityEntry.insert(0, row[7])
            statusCombobox.set(row[8])

    def treeview_data():
        mycursor.execute('SELECT * from product_data')
        suppliers = mycursor.fetchall()
        treeview.delete(*treeview.get_children())
        for supply in suppliers:
            treeview.insert('', END, values=supply)

    def clear(value=False):

        if value:
            treeview.selection_remove(treeview.selection())
        categoryCombobox.set('Select' if cat_row else 'Empty')
        supplierCombobox.set('Select' if sup_row else 'Empty')
        nameEntry.delete(0, END)
        priceEntry.delete(0, END)
        discountEntry.delete(0, END)
        quantityEntry.delete(0, END)
        statusCombobox.set('Select')

    def delete_data():
        selected_item = treeview.selection()

        if not selected_item:
            messagebox.showerror('Error', 'Select data to delete', parent=product_window)
        else:
            result = messagebox.askyesno('Confirm', 'Do you really want to delete?', parent=product_window)
            if result:
                row = treeview.item(selected_item)
                category_id = row['values'][0]
                mycursor.execute('DELETE FROM product_data WHERE id=%s', category_id)
                conn.commit()
                treeview_data()
                clear()
                messagebox.showinfo('Success', 'Data is deleted', parent=product_window)

    def update_data():
        selected_item = treeview.selection()

        if not selected_item:
            messagebox.showerror('Error', 'Select data to update', parent=product_window)
        else:
            row = treeview.item(selected_item)
            product_id = row['values'][0]  # Assuming 'id' is at index 0
            current_values = {
                'category': row['values'][1],
                'supplier': row['values'][2],
                'name': row['values'][3],
                'price': str(row['values'][4]),
                'discount': str(row['values'][5]),
                'quantity': str(row['values'][6]),
                'status': row['values'][7]
            }

            new_values = {
                'category': categoryCombobox.get(),
                'supplier': supplierCombobox.get(),
                'name': nameEntry.get(),
                'price': priceEntry.get(),
                'discount': discountEntry.get(),
                'quantity': quantityEntry.get(),
                'status': statusCombobox.get()
            }

            if current_values == new_values:
                messagebox.showinfo('Info', 'No changes detected', parent=product_window)
            else:
                try:
                    # Calculate price after discount
                    price = float(new_values['price'])
                    discount = float(new_values['discount'])
                    price_after_discount = price * (1 - discount / 100)

                    # Update the record in the database
                    mycursor.execute(
                        'UPDATE product_data SET category=%s, supplier=%s, name=%s, price=%s, discount=%s, price_after_discount=%s, quantity=%s, status=%s WHERE id=%s',
                        (
                            new_values['category'],
                            new_values['supplier'],
                            new_values['name'],
                            new_values['price'],
                            new_values['discount'],
                            price_after_discount,
                            new_values['quantity'],
                            new_values['status'],
                            product_id
                        )
                    )
                    conn.commit()
                    treeview_data()
                    clear()
                    messagebox.showinfo('Success', 'Data is updated', parent=product_window)
                except pymysql.err.ProgrammingError as e:
                    messagebox.showerror('SQL Error', f"An error occurred: {e}", parent=product_window)
                except ValueError as e:
                    messagebox.showerror('Input Error', f"Invalid input: {e}", parent=product_window)

    def fetch_supplier_category():
        global cat_row, sup_row
        category_options = []
        supplier_options = []
        mycursor.execute('SELECT name FROM category_data')
        cat_row = mycursor.fetchall()
        if len(cat_row) > 0:
            categoryCombobox.set('Select')
            for name in cat_row:
                category_options.append(name[0])
            categoryCombobox.config(values=category_options)
        mycursor.execute('SELECT name FROM sup_data')
        sup_row = mycursor.fetchall()
        if len(sup_row) > 0:
            supplierCombobox.set('Select')
            for name in sup_row:
                supplier_options.append(name[0])
            supplierCombobox.config(values=supplier_options)

    def save_data():
        if (categoryCombobox.get() == 'Empty'):
            messagebox.showerror('Error', 'Add Category', parent=product_window)
        elif supplierCombobox.get() == 'Empty':
            messagebox.showerror('Error', 'Add Supplier', parent=product_window)
        elif (
                categoryCombobox.get() == 'Select' or supplierCombobox.get() == 'Select' or nameEntry.get() == '' or priceEntry.get() == '' or discountEntry.get() == '' or quantityEntry.get() == '' or statusCombobox.get() == 'Select'):
            messagebox.showerror('Error', 'All fields are required', parent=product_window)

        else:

            mycursor.execute(
                'SELECT * FROM product_data WHERE category = %s AND supplier = %s AND name = %s',
                (categoryCombobox.get(), supplierCombobox.get(), nameEntry.get())
            )
            existing_record = mycursor.fetchone()

            if existing_record:
                messagebox.showerror('Error', 'This product already exists', parent=product_window)
            else:
                try:
                    # Get values from entries
                    category = categoryCombobox.get()
                    supplier = supplierCombobox.get()
                    name = nameEntry.get()
                    price = float(priceEntry.get())
                    discount = float(discountEntry.get())
                    quantity = quantityEntry.get()
                    status = statusCombobox.get()

                    # Calculate price after discount
                    price_after_discount = price * (1 - discount / 100)

                    # Insert data into database
                    mycursor.execute(
                        'INSERT INTO product_data (category, supplier, name, price, discount, price_after_discount, quantity, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                        (
                            category,
                            supplier,
                            name,
                            price,
                            discount,
                            price_after_discount,
                            quantity,
                            status
                        )
                    )
                    conn.commit()
                    treeview_data()
                    messagebox.showinfo('Success', 'Data is saved', parent=product_window)
                    clear()
                except Exception as e:
                    messagebox.showerror('Error', f'Error saving data: {e}', parent=product_window)

    def search():
        if searchEntry.get() == '':
            messagebox.showerror('Error', 'Enter value to search', parent=product_window)
        elif searchCombobox.get() == 'Search By':
            messagebox.showerror('Error', 'Please select an option', parent=product_window)

        else:
            mycursor.execute(f'SELECT * FROM product_data WHERE {searchCombobox.get()}=%s', searchEntry.get())
            result = mycursor.fetchall()
            if len(result) == 0:
                messagebox.showerror('Error', 'No record found', parent=product_window)
            else:
                treeview.delete(*treeview.get_children())
                for employee in result:
                    treeview.insert('', END, values=employee)

    def show_data():
        treeview_data()
        searchEntry.delete(0, END)
        searchCombobox.set('Search By')

    # GUI

    product_window = Frame(root, width=1070, height=567, bg='white')
    product_window.place(x=200, y=100)

    backImage = PhotoImage(file='back.png')
    backButton = Button(product_window, image=backImage, bd=0, bg='white', cursor='hand2',
                        command=lambda: product_window.destroy())
    backButton.image = backImage
    backButton.place(x=20, y=5)

    leftFrame = Frame(product_window, bd=2, relief=RIDGE, bg='white')
    leftFrame.place(x=20, y=40)

    titleLabel = Label(leftFrame, text='Manage Product Details', font=('Arial', 15, 'bold'), bg='#0f4d7d', fg='white')
    titleLabel.grid(row=0, column=0, columnspan=2, sticky='news')

    categoryLabel = Label(leftFrame, text='Category', font=('times new roman', 15), bg='white')
    categoryLabel.grid(row=1, column=0, sticky='w', padx=20)
    categoryCombobox = ttk.Combobox(leftFrame,
                                    font=('times new roman', 15),
                                    state='readonly', width=18)
    categoryCombobox.grid(row=1, column=1, pady=15, sticky='w')
    categoryCombobox.set('Empty')

    supplierLabel = Label(leftFrame, text='Supplier', font=('times new roman', 15), bg='white')
    supplierLabel.grid(row=2, column=0, sticky='w', padx=20)
    supplierCombobox = ttk.Combobox(leftFrame,
                                    font=('times new roman', 15),
                                    state='readonly', width=18)
    supplierCombobox.grid(row=2, column=1, pady=15, sticky='w')
    supplierCombobox.set('Empty')

    nameLabel = Label(leftFrame, text='Name', font=('times new roman', 15), bg='white')
    nameLabel.grid(row=3, column=0, padx=20, sticky='w')
    nameEntry = Entry(leftFrame, font=('times new roman', 15), bg='lightyellow')
    nameEntry.grid(row=3, column=1, sticky='w', pady=15)

    priceLabel = Label(leftFrame, text='Price', font=('times new roman', 15), bg='white')
    priceLabel.grid(row=4, column=0, sticky='w', padx=20)
    priceEntry = Entry(leftFrame, font=('times new roman', 15), bg='lightyellow')
    priceEntry.grid(row=4, column=1, pady=15, sticky='w')

    discountLabel = Label(leftFrame, text='Discount (%)', font=('times new roman', 15), bg='white')
    discountLabel.grid(row=5, column=0, sticky='w', padx=20)
    discountEntry = Spinbox(leftFrame, from_=0, to=100, increment=1, font=('times new roman', 15),width=19)
    discountEntry.grid(row=5, column=1, pady=15, sticky='w')

    quantityLabel = Label(leftFrame, text='Quantity', font=('times new roman', 15), bg='white')
    quantityLabel.grid(row=6, column=0, sticky='w', padx=20)
    quantityEntry = Entry(leftFrame, font=('times new roman', 15), bg='lightyellow')
    quantityEntry.grid(row=6, column=1, pady=15, sticky='w')

    statusLabel = Label(leftFrame, text='Status', font=('times new roman', 15), bg='white')
    statusLabel.grid(row=7, column=0, sticky='w', padx=20)
    statusCombobox = ttk.Combobox(leftFrame, values=('Active', 'Inactive'),
                                  font=('times new roman', 15),
                                  state='readonly', width=18)
    statusCombobox.grid(row=7, column=1, pady=15, sticky='w')
    statusCombobox.set('Select')

    # buttons
    buttonFrame = Frame(leftFrame, bg='white')
    buttonFrame.grid(row=8, columnspan=2, pady=30, padx=10)

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

    searchFrame = LabelFrame(product_window, bg='white', text='Search Products', font=('arial', 13, 'bold'))
    searchFrame.place(x=455, y=35)

    searchCombobox = ttk.Combobox(searchFrame, values=('Category', 'Supplier', 'Name'),
                                  font=('times new roman', 12),
                                  state='readonly')
    searchCombobox.grid(row=0, column=0, padx=10)
    searchCombobox.set('Search By')
    searchEntry = Entry(searchFrame, font=('times new roman', 12), bg='lightyellow')
    searchEntry.grid(row=0, column=1, padx=(0, 10))
    searchButton = Button(searchFrame, text='Search', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                          cursor='hand2', width=10, command=search)
    searchButton.grid(row=0, column=2, pady=5)

    showButton = Button(searchFrame, text='Show All', font=('times new roman', 12, 'bold'), width=10, fg='white',
                        bg='#0f4d7d', cursor='hand2', command=show_data)
    showButton.grid(row=0, column=3, pady=5, padx=10)

    treeviewFrame = Frame(product_window, bg='white')
    treeviewFrame.place(x=455, y=110, height=455, width=600)

    scrolly = Scrollbar(treeviewFrame, orient=VERTICAL)
    scrollx = Scrollbar(treeviewFrame, orient=HORIZONTAL)
    treeview = ttk.Treeview(treeviewFrame,
                            columns=('id', 'category', 'supplier', 'name', 'price','discount', 'price_after_discount', 'quantity', 'status'),
                            yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

    scrolly.pack(side=RIGHT, fill=Y)
    scrollx.pack(side=BOTTOM, fill=X)
    scrollx.config(command=treeview.xview)
    scrolly.config(command=treeview.yview)
    treeview.pack(fill=BOTH, expand=1)
    treeview.heading('id', text='ID')
    treeview.heading('category', text='Category')
    treeview.heading('supplier', text='Supplier')
    treeview.heading('name', text='Name')
    treeview.heading('price', text='Price')
    treeview.heading('discount', text='Discount')
    treeview.heading('price_after_discount', text='Discounted Price')
    treeview.heading('quantity', text='Quantity')
    treeview.heading('status', text='Status')

    treeview.column('id', width=80)
    treeview.column('category', width=160)
    treeview.column('supplier', width=120)
    treeview.column('name', width=160)
    treeview.column('price', width=100)
    treeview.column('discount', width=100)
    treeview.column('price_after_discount', width=120)
    treeview.column('quantity', width=100)
    treeview.column('status', width=140)
    treeview['show'] = 'headings'

    fetch_supplier_category()
    treeview_data()
    treeview.bind('<ButtonRelease-1>', select_data)
    return product_window, mycursor
