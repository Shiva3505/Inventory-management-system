from tkinter import *
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from tkinter import ttk
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import filedialog

current_data = []  # Global variable to store currently displayed data
current_search_date = None  # Global variable to store the last searched date, default is None


def sales_page(root, mycursor, conn):
    def export_to_excel():
        # Get data from Treeview
        data = [tree.item(item)['values'] for item in tree.get_children()]

        if not data:
            messagebox.showwarning("No Data", "No data available to export.")
            return
        columns = [col for col in tree["columns"]]
        df = pd.DataFrame(data, columns=columns)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Export Success", f"Data exported to {file_path}")




    search_list = []

    def listBox_addFile():
        list_Box.delete(0, END)
        if os.path.exists('bills'):
            for file in os.listdir('bills'):
                if file.split('.')[-1] == 'txt':
                    list_Box.insert(END, file)
                    search_list.append(file.split('.')[0])

    def billArea_insert(event):
        global qr_photo
        row_index = list_Box.curselection()
        if len(row_index) > 0:
            file = list_Box.get(row_index)
            file_name = file.split('.')[0]
            open_file = open(f'bills/{file}', 'r',encoding='utf-8')
            file_content = open_file.read()  # Read the entire file content at once
            billArea.delete(1.0, END)  # Clear existing content in billArea
            billArea.insert(END, file_content)  # Insert the file content into billArea
            open_file.close()

            qr_image_path = f'bills/{file_name}.png'
            image = Image.open(qr_image_path)

            # Resize the image (e.g., to 200x200 pixels)
            resized_image = image.resize((200, 200))

            # Convert the image to a format Tkinter can use
            qr_photo = ImageTk.PhotoImage(resized_image)
            billArea.insert(END, '\t\t')
            billArea.image_create(END, image=qr_photo)
            billArea.insert(END, "\n\t\tScan the QR code for the invoice summary.\n")

    def search():
        if searchEntry.get() == '':
            messagebox.showerror('Error', 'Enter value to search', parent=sales_window)
        elif searchEntry.get() in search_list:

            open_file = open(f'bills/{searchEntry.get()}.txt', 'r')
            file_content = open_file.read()  # Read the entire file content at once

            billArea.delete(1.0, END)  # Clear existing content in billArea
            billArea.insert(END, file_content)  # Insert the file content into billArea
            open_file.close()
        else:
            messagebox.showerror('Error', 'Invalid invoice no.', parent=sales_window)

    def reset():
        """Reset all fields and display all sales data with no sorting applied."""
        listBox_addFile()  # Assuming this clears the file list or a similar function
        billArea.delete(1.0, END)  # Clears the bill area text widget
        display_sales()  # Reset the displayed data to show all sales
        sorting_combobox.set('Select Sorting Option')  # Reset the sorting combobox
        searchEntry.delete(0, END)  # Clear the search entry
        # Reset the global search date so future sorts apply to all data
        global current_search_date
        current_search_date = None

        available_dates_combobox.set('Select Date to View Sales')

    def display_sales(search_date=None, sort_by=None, ascending=True):
        """Fetch and display sales records, either all or filtered by date."""
        try:
            query = """
                SELECT product_name, SUM(quantity_sold), SUM(sale_amount)
                FROM sales
            """
            params = ()

            if search_date:
                formatted_date = datetime.strptime(search_date, "%d-%m-%Y").strftime("%Y-%m-%d")
                query += " WHERE sale_date = %s"
                params = (formatted_date,)

            query += " GROUP BY product_name"

            # Add sorting logic
            if sort_by:
                order = 'ASC' if ascending else 'DESC'
                query += f" ORDER BY {sort_by} {order}"

            # Execute the query with parameters
            mycursor.execute(query, params)
            sales_data = mycursor.fetchall()

            # Update total sales label (optional)
            if search_date:
                mycursor.execute("SELECT SUM(sale_amount) FROM sales WHERE sale_date = %s", (formatted_date,))
                daily_sales_amount = mycursor.fetchone()[0] or 0
                daily_sales_label.config(text=f"Total Sales Amount on {search_date}: ₹ {daily_sales_amount}")
            else:
                mycursor.execute("SELECT SUM(sale_amount) FROM sales")
                total_sales_amount = mycursor.fetchone()[0] or 0
                daily_sales_label.config(text=f"Total Sales Amount: ₹ {total_sales_amount}")

            # Display data in the Treeview
            display_sales_data(sales_data)

        except Exception as e:
            print(f"Error fetching sales records: {e}")

    def display_sales_data(data):
        """Utility function to display data in the Treeview."""
        for item in tree.get_children():
            tree.delete(item)  # Clear the Treeview before inserting new data

        for row in data:
            tree.insert("", "end", values=row)

    def apply_sorting(event):
        """Apply sorting based on the selected option."""
        sort_option = sorting_combobox.get()

        if sort_option == 'Sort by Quantity Ascending':
            sort_by = 'SUM(quantity_sold)'
            ascending = True
        elif sort_option == 'Sort by Quantity Descending':
            sort_by = 'SUM(quantity_sold)'
            ascending = False
        elif sort_option == 'Sort by Amount Ascending':
            sort_by = 'SUM(sale_amount)'
            ascending = True
        elif sort_option == 'Sort by Amount Descending':
            sort_by = 'SUM(sale_amount)'
            ascending = False
        else:
            return  # No sorting option selected

        # Apply sorting to the filtered data based on the stored search date
        display_sales(search_date=current_search_date, sort_by=sort_by, ascending=ascending)

    def populate_available_dates():
        """Fetch available sales dates from the database and populate the combobox."""
        try:
            query = "SELECT DISTINCT sale_date FROM sales ORDER BY sale_date"
            mycursor.execute(query)
            dates = [date[0].strftime("%d-%m-%Y") for date in mycursor.fetchall()]  # Format to dd-mm-yyyy
            available_dates_combobox['values'] = dates  # Populate combobox with available dates
        except Exception as e:
            print(f"Error fetching dates: {e}")

    def search_sales_by_date(event):
        sorting_combobox.set('Select Sorting Option')
        """Display sales for the selected date in the combobox."""
        global current_search_date
        search_date = available_dates_combobox.get()  # Get the selected date
        if search_date:
            current_search_date = search_date  # Store the selected date globally
            display_sales(search_date=search_date)  # Display sales for the selected date
        else:
            messagebox.showwarning("Input Error", "Please select a valid date.")

    def show_sales_report():
        mycursor.execute("""
            SELECT product_name, SUM(quantity_sold) as total_quantity
            FROM sales
            GROUP BY product_name
        """)
        data = mycursor.fetchall()

        products = [row[0] for row in data]
        quantities = [row[1] for row in data]

        plt.figure(figsize=(10, 5))
        plt.bar(products, quantities, color='blue')
        plt.xlabel('Product Name')
        plt.ylabel('Total Quantity Sold')
        plt.title('Sales Report')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    sales_window = Frame(root, width=1070, height=567, bg='white')
    sales_window.place(x=200, y=100)


    titleLabel = Label(sales_window, text='Customer Bill and Sales Analysis', font=('times new roman', 18, 'bold'), bg='#0f4d7d', fg='white')
    titleLabel.place(x=0, y=0, relwidth=1)

    backImage = PhotoImage(file='back.png')
    backButton = Button(sales_window, image=backImage, bd=0, bg='white', cursor='hand2',
                        command=lambda: sales_window.destroy())
    backButton.image = backImage
    backButton.place(x=10, y=50)


    searchFrame = Frame(sales_window, bg='white')
    searchFrame.place(x=250, y=80)

    invoiceLabel = Label(searchFrame, text='Invoice No.', font=('times new roman', 12), bg='white')
    invoiceLabel.grid(row=0, column=0, padx=20)
    searchEntry = Entry(searchFrame, font=('times new roman', 12), bg='lightyellow', width=14)
    searchEntry.grid(row=0, column=1)
    searchButton = Button(searchFrame, text='Search Bill', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                          cursor='hand2', width=8, command=search)
    searchButton.grid(row=0, column=2, padx=20)


    listFrame = Frame(sales_window, bg='white', bd=3, relief=RIDGE)
    listFrame.place(x=20, y=130, height=350, width=200)
    scrolly = Scrollbar(listFrame, orient=VERTICAL)
    list_Box = Listbox(listFrame, font=('times new roman', 12), yscrollcommand=scrolly.set)
    scrolly.pack(side=RIGHT, fill=Y)
    scrolly.config(command=list_Box.yview)
    list_Box.pack(fill=BOTH, expand=1)

    list_Box.bind('<ButtonRelease-1>', billArea_insert)

    billFrame = Frame(sales_window, bg='white', bd=3, relief=RIDGE)
    billFrame.place(x=240, y=130, height=350, width=420)

    billLabel = Label(billFrame, text='Customer Bill Area', font=('times new roman', 14, 'bold'), bg='#0f4d7d', fg='white')
    billLabel.pack(fill=X)

    scrolly = Scrollbar(billFrame, orient=VERTICAL)
    billArea = Text(billFrame, font=('times new roman', 10), yscrollcommand=scrolly.set)
    scrolly.pack(side=RIGHT, fill=Y)
    scrolly.config(command=billArea.yview)
    billArea.pack(fill=BOTH, expand=1)


    rightFrame = Frame(sales_window, bg='white')
    rightFrame.place(x=680, y=68)

    available_dates_combobox = ttk.Combobox(rightFrame, width=25, font=('times new roman', 12))
    available_dates_combobox.pack(pady=15)
    available_dates_combobox.set('Select Date to View Sales')

    sorting_options = [
        'Sort by Quantity Ascending',
        'Sort by Quantity Descending',
        'Sort by Amount Ascending',
        'Sort by Amount Descending'
    ]
    sorting_combobox = ttk.Combobox(rightFrame, values=sorting_options, font=('times new roman', 12),width=25)
    sorting_combobox.set('Select Sorting Option')
    sorting_combobox.pack()
    sorting_combobox.bind('<<ComboboxSelected>>', apply_sorting)

    # Initial display (when no date is searched)
    daily_sales_label = Label(rightFrame, text="", font=("times new roman", 12), bg='white')
    daily_sales_label.pack(pady=10)

    # Frame to hold Treeview and Scrollbars
    frame = Frame(rightFrame, bg='white')
    frame.pack(fill=BOTH, expand=True)

    # Create Treeview with columns
    columns = ("Product Name", "Quantity Sold", "Total Sales Amount")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=13)

    # Define column headings and their widths
    tree.heading("Product Name", text="Product Name")
    tree.heading("Quantity Sold", text="Quantity Sold")
    tree.heading("Total Sales Amount", text="Total Sales Amount (₹)")

    # Set fixed column widths
    tree.column("Product Name", width=150)
    tree.column("Quantity Sold", width=80)
    tree.column("Total Sales Amount", width=130)

    v_scrollbar = Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure( yscrollcommand=v_scrollbar.set)


    v_scrollbar.pack(side="right", fill="y")

    # Pack the Treeview after configuring scrollbars
    tree.pack(fill=BOTH, expand=True)



    buttonFrame=Frame(sales_window,bg='white')
    buttonFrame.place(x=450,y=510)
    exportButton = Button(buttonFrame, text='Export', font=('times new roman', 12, 'bold'), width=8, fg='white',
                         bg='#0f4d7d', cursor='hand2', command=export_to_excel)
    exportButton.grid(row=0, column=0,padx=20)

    show_report_button = Button(buttonFrame, text="Show Report", font=('times new roman', 12, 'bold'), bg='#0f4d7d',
                                fg='white', cursor='hand2', command=show_sales_report)
    show_report_button.grid(row=0,column=1)

    resetButton = Button(buttonFrame, text='Reset', font=('times new roman', 12, 'bold'), width=8, fg='white',
                         bg='#0f4d7d', cursor='hand2', command=reset)
    resetButton.grid(row=0, column=2, padx=20)

    listBox_addFile()
    display_sales()
    # Bind the Combobox selection to the search_sales_by_date function
    available_dates_combobox.bind("<<ComboboxSelected>>", search_sales_by_date)

    # Call this function to populate dates when the app starts
    populate_available_dates()
    return sales_window
