from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import time, qrcode
import os, tempfile, pymysql
from PIL import ImageTk, Image


def get_tax_from_database():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="Shiva3505@",
            database="ims1_data1"
        )
        mycursor = conn.cursor()
        # Fetch the tax percentage from the database
        mycursor.execute("SELECT tax_percentage FROM settings WHERE id = 1")
        result = mycursor.fetchone()

        # Check if result is not None and assign to tax variable
        if result:
            tax = result[0]
            return tax
        else:
            messagebox.showwarning("Warning", "No tax percentage set in the database.")
            return 0  # Default tax value if not set
    except Exception as e:
        print(f"Error fetching tax from database: {e}")
        messagebox.showerror("Database Error", "Failed to fetch tax percentage.")
        return 0  # Default tax value if error occurs


def show_sales():
    sale_data_list = []
    for data in cart_data:
        product_id = data[0]
        product_name = data[1]
        product_price = float(data[2])
        product_quantity = int(data[3])
        sale_amount = product_price * product_quantity
        # Store sales data tuple
        sale_data = (product_id, product_name, product_quantity, sale_amount)
        sale_data_list.append(sale_data)

    sale_insert_query = """
    INSERT INTO sales (product_id, product_name, quantity_sold, sale_date, sale_amount)
    VALUES (%s, %s,%s, CURDATE(), %s)
    """
    for sale_data in sale_data_list:
        try:
            mycursor.execute(sale_insert_query, sale_data)
            conn.commit()
        except Exception as e:
            print(f"Error inserting sale data: {e}")
            conn.rollback()
    print(sale_data_list)


def connection():
    global mycursor, conn, emp_name
    try:
        conn = pymysql.connect(host='localhost', user='root', password='Shiva3505@', database='ims1_data1')
        mycursor = conn.cursor()
    except:
        messagebox.showerror('Error', 'Something went wrong, Please open MySQL app before running again')

    try:
        emp_id = os.getenv('EMP_ID')
        print(emp_id)
        mycursor.execute('SELECT name from emp_data WHERE empid=%s', emp_id)
        emp_name = mycursor.fetchone()
        if len(emp_name) > 0:
            emp_name = emp_name[0]
    except Exception as e:
        print(e)


# Functions
def treeview_data():
    mycursor.execute(
        'SELECT id,name,price,discount,quantity,status from pro_data WHERE status="active"')
    suppliers = mycursor.fetchall()
    treeview.delete(*treeview.get_children())
    for supply in suppliers:
        treeview.insert('', END, values=supply)


def search():
    if searchEntry.get() == '':
        messagebox.showerror('Error', 'Enter value to search', )

    else:
        mycursor.execute(f'SELECT id,name,price,quantity,status FROM pro_data WHERE name=%s and status="active"',
                         searchEntry.get())
        result = mycursor.fetchall()
        if len(result) == 0:
            messagebox.showerror('Error', 'No record found')
        else:
            treeview.delete(*treeview.get_children())
            for employee in result:
                treeview.insert('', END, values=employee)


def show_data():
    treeview_data()
    searchEntry.delete(0, END)


def clear(value=False):
    global cart_data
    if value:
        treeview.selection_remove(treeview.selection())
        instockLabel.config(text='In stock: 0')

    prodnameEntry.config(state=NORMAL)
    priceperqtyEntry.config(state=NORMAL)
    prodnameEntry.delete(0, END)
    priceperqtyEntry.delete(0, END)
    qtyEntry.delete(0, END)
    prodnameEntry.config(state='readonly')
    priceperqtyEntry.config(state='readonly')


def clear_all():
    global cart_data, check_bill_generate
    clear(value=True)
    cart_data = []
    tree_cart.delete(*tree_cart.get_children())
    billamountLabel.config(text='Bill Amount (₹)\n0')
    netpayLabel.config(text='Net Pay (₹)\n0')
    mycartProductLabel.config(text=f'My Cart\tTotal Products: {len(cart_data)}')
    textarea.config(state=NORMAL)
    textarea.delete(1.0, END)
    textarea.config(state=DISABLED)
    nameEntry.delete(0, END)
    contactEntry.delete(0, END)
    searchEntry.delete(0, END)
    calculatorField.delete(0, END)
    check_bill_generate = 0


def select_data(event):
    global stock
    selected = treeview.selection()
    content = treeview.item(selected)
    if content['values']:
        row = content['values']
        clear()
        prodnameEntry.config(state=NORMAL)
        priceperqtyEntry.config(state=NORMAL)

        prodnameEntry.insert(0, row[1])
        priceperqtyEntry.insert(0, row[4])
        qtyEntry.insert(0, '1')
        prodnameEntry.config(state='readonly')
        priceperqtyEntry.config(state='readonly')
        stock = row[5]
        instockLabel.config(text=f'In stock {row[5]}')


def select_cart_data(event):
    global stock
    selected = tree_cart.selection()
    content = tree_cart.item(selected)
    if content['values']:
        row = content['values']
        clear()
        prodnameEntry.config(state=NORMAL)
        priceperqtyEntry.config(state=NORMAL)

        prodnameEntry.insert(0, row[1])
        priceperqtyEntry.insert(0, row[4])
        qtyEntry.insert(0, row[3])
        prodnameEntry.config(state='readonly')
        priceperqtyEntry.config(state='readonly')
        stock = row[4]
        instockLabel.config(text=f'In stock {row[4]}')


cart_data = []

total_discount = 0


def add_update_cart():
    global total_discount
    selected_item = treeview.selection()
    selected_treecart = tree_cart.selection()
    if not (selected_item or selected_treecart):
        messagebox.showerror('Error', 'Select Data')
    elif qtyEntry.get() == '':
        messagebox.showerror('Error', 'Add Quantity')
    elif qtyEntry.get() > stock:
        messagebox.showerror('Error', f'Sorry only {stock} quantity is there.')
    else:
        # prod_price=int(qtyEntry.get())*float(priceperqtyEntry.get().replace(',',''))
        prod_price = float(priceperqtyEntry.get())
        mycursor.execute('Select id,price from pro_data where name=%s', prodnameEntry.get())
        pid = mycursor.fetchone()
        original_price = float(pid[1])
        discount_amount = (original_price - prod_price) * int(qtyEntry.get())

        # Update the total discount by removing the previous discount and adding the new one
        for data in cart_data:
            if pid[0] == data[0]:
                previous_discount = (original_price - float(data[2])) * int(data[3])
                total_discount -= previous_discount
                break

        total_discount += discount_amount
        print(total_discount)
        cart_list = [pid[0], prodnameEntry.get(), prod_price, qtyEntry.get(), stock]
        present = 'no'
        index = 0
        for data in cart_data:
            if pid[0] == data[0]:
                present = 'yes'
                break
            index += 1
        if present == 'yes':
            ans = messagebox.askyesno('Confirm', 'Product exists. Do you want to update?')
            if ans:
                if qtyEntry.get() == '0':
                    cart_data.pop(index)
                else:
                    # cart_data[index][2]=prod_price
                    cart_data[index][3] = qtyEntry.get()
        else:
            cart_data.append(cart_list)
        show_cart()
        bill_update()

def show_cart():
    tree_cart.delete(*tree_cart.get_children())
    for data in cart_data:
        tree_cart.insert('', END, values=data)


def bill_update():
    global bill_amount, net_pay, tax
    bill_amount = 0

    for data in cart_data:
        bill_amount += float(float(data[2]) * int(data[3]))
    tax = get_tax_from_database()
    tax = ((bill_amount * tax) / 100)
    net_pay = bill_amount + tax
    billamountLabel.config(text=f'Bill Amount (₹)\n{bill_amount}')
    netpayLabel.config(text=f'Net Pay (₹)\n{net_pay}')
    mycartProductLabel.config(text=f'My Cart\t Total Products: {len(cart_data)}')


def bill_top():
    global invoice
    invoice = int(time.strftime("%H%M%S")) + int(time.strftime('%d%m%Y'))

    bill_temp = f'''
    \t\t\tInventory Genius
    \t\t Phone No. 7801043389, Hyderabad,500049
    {str("=" * 54)}
    Customer Name: {nameEntry.get()}
    Phone no: {contactEntry.get()}
    Bill no: {str(invoice)}\t\t\tDate: {str(time.strftime('%d/%m/%Y'))}
    {"=" * 54}
    Name\t\tQty\tPrice\t\tDiscount\t\tFinal Price
    {str("=" * 54)} 
    '''
    textarea.delete(1.0, END)
    textarea.insert(1.0, bill_temp)


def bill_bottom():
    global net_pay, qr_photo
    bill_temp = f'''
    {str("=" * 54)}
    Bill Amount\t\t\t\t₹{bill_amount}
    Total Discount\t\t\t\t₹{total_discount}
    Tax\t\t\t\t₹{tax}
    Net Pay\t\t\t\t₹{net_pay}
    {str("=" * 54)}\n    
    '''
    textarea.insert(END, bill_temp)

    # Generate QR code
    qr_data = f'Date: {time.strftime("%d/%m/%Y")}\nInvoice: {invoice}\nCustomer: {nameEntry.get()}\nNet Pay: {net_pay}'

    qr = qrcode.make(qr_data)

    # Save QR code image
    qr_image_path = f'bills/{invoice}.png'
    qr.save(qr_image_path)

    image = Image.open(qr_image_path)

    resized_image = image.resize((200, 200))

    # Convert the image to a format Tkinter can use
    qr_photo = ImageTk.PhotoImage(resized_image)

    textarea.insert(END,'\t\t')
    textarea.image_create(END, image=qr_photo)


def bill_middle():
    for row in cart_data:
        pid = row[0]
        name = row[1]
        price = float(row[2]) * int(row[3])
        qty = int(row[3])

        # Ensure stock is treated as an integer and handle non-numeric values
        try:
            stock = int(row[4])  # Assuming row[4] should contain the stock value
        except ValueError:
            print(f"Invalid stock value for product {pid}. Stock: {row[4]}")  # Log or handle error
            stock = 0  # Set stock to a default value in case of error

        left_qty = stock - qty  # Calculate remaining quantity

        # Determine the status based on the remaining quantity
        if left_qty == 0:
            status = 'Inactive'
        else:
            status = 'Active'

        # Get price and discount from the database
        mycursor.execute('SELECT price,discount from pro_data WHERE id=%s', (pid,))
        result = mycursor.fetchone()

        original_price = float(result[0])
        discount = float(result[1])
        discount_amount = (discount / 100) * original_price

        # Insert data into the textarea
        textarea.insert(END, f'\n    {name}\t\t{qty}\t₹{original_price}\t\t{discount}%={discount_amount}\t\t₹{price}')

        # Update the database with new stock and status
        mycursor.execute('UPDATE pro_data SET quantity=%s, status=%s WHERE id=%s', (left_qty, status, pid))
        conn.commit()

    treeview_data()  # Refresh the treeview after updating database


def generate_bill():
    global check_bill_generate, cart_data,total_discount
    if not (nameEntry.get() and contactEntry.get()):
        messagebox.showerror('Error', 'Name and Contact cannot be empty')
    elif len(cart_data) == 0:
        messagebox.showerror('Error', 'Add products to cart')

    else:
        if not os.path.exists('bills'):
            os.makedirs('bills')
        textarea.config(state=NORMAL)

        bill_top()
        bill_middle()
        bill_bottom()

        show_sales()

        file = open(f'bills/{str(invoice)}.txt', 'w',encoding='utf-8')
        file.write(textarea.get(1.0, END))
        file.close()
        messagebox.showinfo('Success', f'Bill {invoice} is saved.')
        check_bill_generate = 1
        cart_data = []
        clear(True)
        mycartProductLabel.config(text=f'My Cart\tTotal Products: 0')
        tree_cart.delete(*tree_cart.get_children())
        textarea.config(state=DISABLED)

        total_discount = 0


def update_date_time():
    time_ = time.strftime('%I:%M %p')
    date_ = time.strftime('%d/%m/%Y')
    subtitleLabel.config(text=f'Welcome employee \t\t Date: {date_}\t\t Time: {time_}')
    subtitleLabel.after(500, update_date_time)


check_bill_generate = 0


def print_bill():
    if check_bill_generate == 1:
        messagebox.showinfo('Print', 'Printing')
        new_file = tempfile.mktemp('.txt')
        open(new_file, 'w').write(textarea.get(1.0, END))
        os.startfile(new_file, 'print')

    else:
        messagebox.showerror('Error', 'Generate the bill before printing.')


def logout():
    root.destroy()
    os.system('python login.py')


# GUI Part
root = Tk()
root.title('Inventory Management System')
root.geometry('1280x668+0+0')
root.config(bg='white')
icon = PhotoImage(file='icon.png')
titleLabel = Label(root, text='  Inventory Management System', image=icon, compound=LEFT,
                   font=('times new roman', 40, 'bold'), bg='#010c48', fg='white', anchor='w', padx=20)
titleLabel.place(x=0, y=0, relwidth=1, height=70)
logoutButton = Button(root, text='Logout', font=('times new roman', 20, 'bold'), bg='#0f4d7d', fg='white',
                      cursor='hand2', command=logout)
logoutButton.place(x=1100, y=10, height=50, width=150)
subtitleLabel = Label(root, text='Date:DD-MM-YYYY\t\t Time: HH:MM:SS',
                      font=('times new roman', 15), bg='#4d636d', fg='white')
subtitleLabel.place(x=0, y=70, relwidth=1, height=30)

# left menu

leftFrame = Frame(root, bd=2, relief=RIDGE, bg='white')
leftFrame.place(x=10, y=110)

titleLabel = Label(leftFrame, text='All Products', font=('Arial', 15, 'bold'), bg='#0f4d7d', fg='white')
titleLabel.grid(row=0, column=0, columnspan=2, sticky='news', pady=(0, 15))

searchLabel = Label(leftFrame, text='Product Name', font=('Arial', 13, 'bold'), bg='white')
searchLabel.grid(row=1, column=0, padx=(20, 0))

searchEntry = Entry(leftFrame, font=('times new roman', 13), bg='lightyellow', width=18)
searchEntry.grid(row=1, column=1, padx=20)

buttonFrame = Frame(leftFrame, bg='white')
buttonFrame.grid(row=2, columnspan=2, pady=10)
searchButton = Button(buttonFrame, text='Search', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                      cursor='hand2', width=8, command=search)
searchButton.grid(row=2, column=0, padx=(0, 20))

showButton = Button(buttonFrame, text='Show All', font=('times new roman', 12, 'bold'), width=8, fg='white',
                    bg='#0f4d7d', cursor='hand2', command=show_data)
showButton.grid(row=2, column=1)

treeviewFrame = Frame(root, bg='white', bd=2, relief=RIDGE)
treeviewFrame.place(x=10, y=250, height=375, width=350)

scrolly = Scrollbar(treeviewFrame, orient=VERTICAL)
scrollx = Scrollbar(treeviewFrame, orient=HORIZONTAL)
treeview = ttk.Treeview(treeviewFrame,
                        columns=('id', 'name', 'price', 'discount', 'price_after_discount', 'quantity', 'status'),
                        yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

scrolly.pack(side=RIGHT, fill=Y)
scrollx.pack(side=BOTTOM, fill=X)
scrollx.config(command=treeview.xview)
scrolly.config(command=treeview.yview)
treeview.pack(fill=BOTH, expand=1)
treeview.heading('id', text='ID')
treeview.heading('name', text='Name')
treeview.heading('price', text='Price')
treeview.heading('discount', text='Discount (%)')
treeview.heading('price_after_discount', text='Discounted Price')
treeview.heading('quantity', text='Quantity')
treeview.heading('status', text='Status')

treeview.column('id', width=60)
treeview.column('name', width=120)
treeview.column('price', width=80)
treeview.column('discount', width=80)
treeview.column('price_after_discount', width=110)
treeview.column('quantity', width=60)
treeview.column('status', width=80)
treeview['show'] = 'headings'

middleTopFrame = Frame(root, bg='white', bd=2, relief=RIDGE)
middleTopFrame.place(x=370, y=110)

titleLabel = Label(middleTopFrame, text='Customer Details', font=('Arial', 14, 'bold'), bg='#0f4d7d', fg='white')
titleLabel.grid(row=0, column=0, columnspan=4, sticky='news', pady=(0, 10))

nameLabel = Label(middleTopFrame, text='Name', font=('Arial', 12, 'bold'), bg='white')
nameLabel.grid(row=1, column=0, padx=(10, 0))

nameEntry = Entry(middleTopFrame, font=('times new roman', 12), bg='lightyellow', width=16)
nameEntry.grid(row=1, column=1, padx=10)

contactLabel = Label(middleTopFrame, text='Contact No.', font=('Arial', 12, 'bold'), bg='white')
contactLabel.grid(row=1, column=2)

contactEntry = Entry(middleTopFrame, font=('times new roman', 12), bg='lightyellow', width=16)
contactEntry.grid(row=1, column=3, padx=10, pady=10)

calculatorFrame = Frame(root, bg='white', bd=2, relief=RIDGE)
calculatorFrame.place(x=370, y=210)

# Calculator
operator = ''  # 7+9


def buttonClick(numbers):  # 9
    global operator
    operator = operator + numbers
    calculatorField.delete(0, END)
    calculatorField.insert(END, operator)


def clear_field():
    global operator
    operator = ''
    calculatorField.delete(0, END)


def answer():
    global operator
    result = str(eval(operator))
    calculatorField.delete(0, END)
    calculatorField.insert(0, result)
    operator = ''


titleLabel = Label(calculatorFrame, text='Calculator', font=('Arial', 15, 'bold'))
titleLabel.grid(row=0, column=0, columnspan=4, sticky='news')
calculatorField = Entry(calculatorFrame, font=('arial', 18, 'bold'), width=15, bd=4, justify=RIGHT)
calculatorField.grid(row=1, column=0, columnspan=4)
calculatorField.insert(0, '0')

button7 = Button(calculatorFrame, text='7', font=('arial', 12, 'bold'), bd=2, width=4, height=2,
                 command=lambda: buttonClick('7'))
button7.grid(row=2, column=0)

button8 = Button(calculatorFrame, text='8', font=('arial', 12, 'bold'), bd=2, width=4, height=2,
                 command=lambda: buttonClick('8'))
button8.grid(row=2, column=1)

button9 = Button(calculatorFrame, text='9', font=('arial', 12, 'bold'), bd=2, width=4, height=2
                 , command=lambda: buttonClick('9'))
button9.grid(row=2, column=2)

buttonPlus = Button(calculatorFrame, text='+', font=('arial', 12, 'bold'), bd=2, width=4, height=2
                    , command=lambda: buttonClick('+'))
buttonPlus.grid(row=2, column=3)

button4 = Button(calculatorFrame, text='4', font=('arial', 12, 'bold'), bd=2, width=4, height=2
                 , command=lambda: buttonClick('4'))
button4.grid(row=3, column=0)

button5 = Button(calculatorFrame, text='5', font=('arial', 12, 'bold'), bg='white', bd=2, width=4, height=2
                 , command=lambda: buttonClick('5'))
button5.grid(row=3, column=1)

button6 = Button(calculatorFrame, text='6', font=('arial', 12, 'bold'), bg='white', bd=2, width=4, height=2
                 , command=lambda: buttonClick('6'))
button6.grid(row=3, column=2)

buttonMinus = Button(calculatorFrame, text='-', font=('arial', 12, 'bold'), bd=2, width=4, height=2
                     , command=lambda: buttonClick('-'))
buttonMinus.grid(row=3, column=3)

button1 = Button(calculatorFrame, text='1', font=('arial', 12, 'bold'), bd=2, width=4, height=2
                 , command=lambda: buttonClick('1'))
button1.grid(row=4, column=0)

button2 = Button(calculatorFrame, text='2', font=('arial', 12, 'bold'), bg='white', bd=2, width=4, height=2
                 , command=lambda: buttonClick('2'))
button2.grid(row=4, column=1)

button3 = Button(calculatorFrame, text='3', font=('arial', 12, 'bold'), bg='white', bd=2, width=4, height=2
                 , command=lambda: buttonClick('3'))
button3.grid(row=4, column=2)

buttonMult = Button(calculatorFrame, text='*', font=('arial', 12, 'bold'), bd=2, width=4, height=2
                    , command=lambda: buttonClick('*'))
buttonMult.grid(row=4, column=3)

buttonAns = Button(calculatorFrame, text='Ans', font=('arial', 12, 'bold'), bd=2, width=4, height=2,
                   command=answer)
buttonAns.grid(row=5, column=0)

buttonClear = Button(calculatorFrame, text='Clear', font=('arial', 12, 'bold'), bd=2, width=4, height=2
                     , command=clear_field)
buttonClear.grid(row=5, column=1)

button0 = Button(calculatorFrame, text='0', font=('arial', 12, 'bold'), bd=2, width=4, height=2
                 , command=lambda: buttonClick('0'))
button0.grid(row=5, column=2)

buttonDiv = Button(calculatorFrame, text='/', font=('arial', 12, 'bold'), bd=2, width=4, height=2,
                   command=lambda: buttonClick('/'))
buttonDiv.grid(row=5, column=3)

treeFrame = Frame(root, bg='white', bd=2, relief=RIDGE)
treeFrame.place(x=585, y=210, height=282, width=250)

mycartProductLabel = Label(treeFrame, text='My Cart\tTotal Products: 0', font=('Arial', 13, 'bold'), anchor='w')
mycartProductLabel.pack(fill=X)

scrolly = Scrollbar(treeFrame, orient=VERTICAL)
scrollx = Scrollbar(treeFrame, orient=HORIZONTAL)
tree_cart = ttk.Treeview(treeFrame, columns=('id', 'name', 'price', 'quantity'),
                         yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

scrolly.pack(side=RIGHT, fill=Y)
scrollx.pack(side=BOTTOM, fill=X)
scrollx.config(command=tree_cart.xview)
scrolly.config(command=tree_cart.yview)
tree_cart.pack(fill=BOTH, expand=1)
tree_cart.heading('id', text='ID')
tree_cart.heading('name', text='Name')
tree_cart.heading('price', text='Price')
tree_cart.heading('quantity', text='Quantity')

tree_cart.column('id', width=60)
tree_cart.column('name', width=100)
tree_cart.column('price', width=80)
tree_cart.column('quantity', width=60)
tree_cart['show'] = 'headings'

middleBottomFrame = Frame(root, bg='white', bd=2, relief=RIDGE)
middleBottomFrame.place(x=370, y=510)

prodnameLabel = Label(middleBottomFrame, text='Product Name', font=('Arial', 12, 'bold'), bg='white')
prodnameLabel.grid(row=0, column=0, padx=(10, 0), sticky='w')

prodnameEntry = Entry(middleBottomFrame, font=('times new roman', 12), bg='lightyellow', width=16, state='readonly')
prodnameEntry.grid(row=1, column=0, padx=10)

priceperqtyLabel = Label(middleBottomFrame, text='Price', font=('Arial', 12, 'bold'), bg='white')
priceperqtyLabel.grid(row=0, column=1, sticky='w')

priceperqtyEntry = Entry(middleBottomFrame, font=('times new roman', 12), bg='lightyellow', width=16, state='readonly')
priceperqtyEntry.grid(row=1, column=1, padx=10, pady=5)

qtyLabel = Label(middleBottomFrame, text='Quantity', font=('Arial', 12, 'bold'), bg='white')
qtyLabel.grid(row=0, column=2, sticky='w')

qtyEntry = Entry(middleBottomFrame, font=('times new roman', 12), bg='lightyellow', width=16)
qtyEntry.grid(row=1, column=2, padx=10)

instockLabel = Label(middleBottomFrame, text='In Stock: 0', font=('Arial', 12, 'bold'), bg='white')
instockLabel.grid(row=2, column=0)

buttonFrame = Frame(middleBottomFrame, bg='white')
buttonFrame.grid(row=2, columnspan=2, pady=10, column=1)

clearButton = Button(buttonFrame, text='Clear', font=('times new roman', 12, 'bold'), bg='#0f4d7d', fg='white',
                     cursor='hand2', width=12, command=lambda: clear(True))
clearButton.grid(row=0, column=0, padx=(0, 15))

addupdateButton = Button(buttonFrame, text='Add/Update Cart', font=('times new roman', 12, 'bold'), fg='white',
                         bg='#0f4d7d', cursor='hand2', width=16, command=add_update_cart)
addupdateButton.grid(row=0, column=1, padx=10)

rightTopFrame = Frame(root, bg='white', bd=2, relief=RIDGE)
rightTopFrame.place(x=845, y=110)

titleLabel = Label(rightTopFrame, text='Customer Billing Area', font=('Arial', 15, 'bold'), bg='#0f4d7d', fg='white')
titleLabel.grid(row=0, column=0, columnspan=4, sticky='news')
scrolly = Scrollbar(rightTopFrame, orient=VERTICAL)
textarea = Text(rightTopFrame, font=('times new roman', 10,), width=66, height=23, yscrollcommand=scrolly.set,bg='lightyellow',
                state=DISABLED)
# Place the Text and Scrollbar in the grid
textarea.grid(row=1, column=0, )
scrolly.grid(row=1, column=1, sticky='ns')

# Configure the scrollbar command
scrolly.config(command=textarea.yview)

rightBottomFrame = Frame(root, bg='white')
rightBottomFrame.place(x=865, y=503)

billamountLabel = Label(rightBottomFrame, text='Bill Amount (₹)\n0', font=('times new roman', 11, 'bold'),
                        bg='#4d636d',
                        fg='white',
                        width=13, height=3)
billamountLabel.grid(row=0, column=0, pady=8)

taxLabel = Label(rightBottomFrame, text=f'Tax\n{get_tax_from_database()}%', font=('times new roman', 11, 'bold'),
                 fg='white',
                 bg='#4d636d', width=13, height=3)
taxLabel.grid(row=0, column=1, padx=5)

netpayLabel = Label(rightBottomFrame, text='Net Pay (₹)\n0', font=('times new roman', 11, 'bold'), fg='white',
                    bg='#4d636d', width=13, height=3)
netpayLabel.grid(row=0, column=2)

generateButton = Button(rightBottomFrame, text='Generate Bill', font=('times new roman', 11, 'bold'), fg='white',
                        bg='#0f4d7d', cursor='hand2', width=13, height=2, command=generate_bill)
generateButton.grid(row=1, column=0)

printButton = Button(rightBottomFrame, text='Print', font=('times new roman', 11, 'bold'), fg='white',
                     bg='#0f4d7d', cursor='hand2', width=13, height=2, command=print_bill)
printButton.grid(row=1, column=1, padx=5)

clearAllButton = Button(rightBottomFrame, text='Clear All', font=('times new roman', 11, 'bold'), fg='white',
                        bg='#0f4d7d', cursor='hand2', width=13, height=2, command=clear_all)
clearAllButton.grid(row=1, column=2)

connection()
treeview_data()
treeview.bind('<ButtonRelease-1>', select_data)
tree_cart.bind('<ButtonRelease-1>', select_cart_data)

update_date_time()
root.mainloop()
