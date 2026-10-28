from flask import Flask, render_template, request, redirect, url_for,session
from database import connection
import pandas as pd

app = Flask(__name__)
app.secret_key = "dineflow_secret_key"


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        
        password = request.form["password"].strip()

        cursor = connection.cursor()

        # Check Admin
        cursor.execute("""
            SELECT * FROM users
            WHERE username=%s AND password=%s
        """, (username, password))

        admin = cursor.fetchone()

        if admin:
            cursor.close()
            return redirect("/dashboard")

        # Check Customer
        cursor.execute("""
            SELECT * FROM customers
            WHERE username=%s AND password=%s
        """, (username, password))

        customer = cursor.fetchone()

        cursor.close()

        if customer:

            session["customer_id"] = customer["customer_id"]
            session["customer_name"] = customer["customer_name"]

            return redirect("/customer_dashboard")

        return "Invalid Username or Password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    cursor = connection.cursor()

    # ==========================================
    # TOTAL CUSTOMERS
    # ==========================================

    cursor.execute("SELECT COUNT(*) AS total FROM customers")
    total_customers = cursor.fetchone()["total"]


    # ==========================================
    # TOTAL MENU ITEMS
    # ==========================================

    cursor.execute("SELECT COUNT(*) AS total FROM menu")
    total_menu = cursor.fetchone()["total"]


    # ==========================================
    # TOTAL TABLES
    # ==========================================

    cursor.execute("SELECT COUNT(*) AS total FROM restaurant_tables")
    total_tables = cursor.fetchone()["total"]


    # ==========================================
    # TOTAL ORDERS
    # ==========================================

    cursor.execute("SELECT COUNT(*) AS total FROM orders")
    total_orders = cursor.fetchone()["total"]


    # ==========================================
    # TOTAL REVENUE
    # ==========================================

    cursor.execute("SELECT SUM(total_amount) AS revenue FROM orders")
    revenue = cursor.fetchone()["revenue"]

    if revenue is None:
        revenue = 0


    cursor.close()


    # ==========================================
    # AI DEMAND PREDICTION
    # ==========================================

    try:

        predictions = pd.read_csv(
            "ml/demand_predictions.csv"
        )

        predictions = predictions[
            [
                "date",
                "item_name",
                "category",
                "predicted_demand",
                "recommendation"
            ]
        ]

        predictions = predictions.to_dict(
            "records"
        )

    except Exception as e:

        print(
            "AI prediction error:",
            e
        )

        predictions = []


    # ==========================================
    # SEND DATA TO DASHBOARD
    # ==========================================

    return render_template(
        "dashboard.html",

        total_customers=total_customers,

        total_menu=total_menu,

        total_tables=total_tables,

        total_orders=total_orders,

        revenue=revenue,

        predictions=predictions
    )
@app.route("/customer_dashboard")
def customer_dashboard():

    customer_name = session.get("customer_name")

    return render_template(
        "customer_dashboard.html",
        customer_name=customer_name
    )

@app.route("/menu")
def menu():

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM menu")

    menu = cursor.fetchall()

    cursor.close()

    return render_template("menu.html", menu=menu)



@app.route("/add_menu", methods=["GET","POST"])
def add_menu():

    if request.method=="POST":

        item_name=request.form["item_name"]
        category=request.form["category"]
        price=request.form["price"]

        cursor=connection.cursor()

        sql="""
        INSERT INTO menu(item_name,category,price)
        VALUES(%s,%s,%s)
        """

        cursor.execute(sql,(item_name,category,price))

        connection.commit()

        cursor.close()

        return redirect("/menu")

    return render_template("add_menu.html")

@app.route("/edit_menu/<int:id>", methods=["GET", "POST"])
def edit_menu(id):

    cursor = connection.cursor()

    if request.method == "POST":

        item_name = request.form["item_name"]
        category = request.form["category"]
        price = request.form["price"]
        availability = request.form["availability"]

        sql = """
        UPDATE menu
        SET item_name=%s,
            category=%s,
            price=%s,
            availability=%s
        WHERE menu_id=%s
        """

        cursor.execute(sql, (item_name, category, price, availability, id))

        connection.commit()

        cursor.close()

        return redirect("/menu")

    cursor.execute("SELECT * FROM menu WHERE menu_id=%s", (id,))

    item = cursor.fetchone()

    cursor.close()

    return render_template("edit_menu.html", item=item)

@app.route("/delete_menu/<int:id>")
def delete_menu(id):

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM menu WHERE menu_id=%s",
        (id,)
    )

    connection.commit()

    cursor.close()

    return redirect("/menu")


@app.route("/customers", methods=["GET"])
def customers():

    cursor = connection.cursor()

    search = request.args.get("search", "")

    if search:

        cursor.execute(
            """
            SELECT * FROM customers
            WHERE customer_name LIKE %s
            """,
            ("%" + search + "%",)
        )

    else:

        cursor.execute("SELECT * FROM customers")

    customers = cursor.fetchall()

    cursor.close()

    return render_template(
        "customers.html",
        customers=customers
    )

@app.route("/add_customer", methods=["GET","POST"])
def add_customer():

    if request.method=="POST":

        customer_name = request.form["customer_name"]
        phone = request.form["phone"]

        cursor = connection.cursor()

        sql = """
        INSERT INTO customers(customer_name,phone)
        VALUES(%s,%s)
        """

        cursor.execute(sql,(customer_name,phone))

        connection.commit()

        cursor.close()

        return redirect("/customers")

    return render_template("add_customer.html")

@app.route("/edit_customer/<int:id>", methods=["GET","POST"])
def edit_customer(id):

    cursor = connection.cursor()

    if request.method=="POST":

        customer_name=request.form["customer_name"]
        phone=request.form["phone"]

        sql="""
        UPDATE customers
        SET customer_name=%s,
            phone=%s
        WHERE customer_id=%s
        """

        cursor.execute(sql,(customer_name,phone,id))

        connection.commit()

        cursor.close()

        return redirect("/customers")

    cursor.execute(
        "SELECT * FROM customers WHERE customer_id=%s",
        (id,)
    )

    customer=cursor.fetchone()

    cursor.close()

    return render_template(
        "edit_customer.html",
        customer=customer
    )

@app.route("/delete_customer/<int:id>")
def delete_customer(id):

    cursor=connection.cursor()

    cursor.execute(
        "DELETE FROM customers WHERE customer_id=%s",
        (id,)
    )

    connection.commit()

    cursor.close()

    return redirect("/customers")

@app.route("/tables")
def tables():

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM restaurant_tables")

    tables = cursor.fetchall()

    cursor.close()

    return render_template(
        "tables.html",
        tables=tables
    )

@app.route("/add_table", methods=["GET","POST"])
def add_table():

    if request.method=="POST":

        table_number = request.form["table_number"]
        capacity = request.form["capacity"]

        cursor = connection.cursor()

        sql = """
        INSERT INTO restaurant_tables(table_number,capacity)
        VALUES(%s,%s)
        """

        cursor.execute(sql,(table_number,capacity))

        connection.commit()

        cursor.close()

        return redirect("/tables")

    return render_template("add_table.html")

@app.route("/edit_table/<int:id>", methods=["GET","POST"])
def edit_table(id):

    cursor = connection.cursor()

    if request.method == "POST":

        table_number = request.form["table_number"]
        capacity = request.form["capacity"]
        status = request.form["status"]

        sql = """
        UPDATE restaurant_tables
        SET table_number=%s,
            capacity=%s,
            status=%s
        WHERE table_id=%s
        """

        cursor.execute(sql, (table_number, capacity, status, id))

        connection.commit()

        cursor.close()

        return redirect("/tables")

    cursor.execute(
        "SELECT * FROM restaurant_tables WHERE table_id=%s",
        (id,)
    )

    table = cursor.fetchone()

    cursor.close()

    return render_template(
        "edit_table.html",
        table=table
    )

@app.route("/delete_table/<int:id>")
def delete_table(id):

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM restaurant_tables WHERE table_id=%s",
        (id,)
    )

    connection.commit()

    cursor.close()

    return redirect("/tables")

@app.route("/orders")
def orders():

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            o.order_id,
            c.customer_name,
            t.table_number,
            m.item_name,
            o.quantity,
            o.total_amount,
            o.order_status

        FROM orders o

        JOIN customers c
            ON o.customer_id = c.customer_id

        LEFT JOIN restaurant_tables t
            ON o.table_id = t.table_id

        JOIN menu m
            ON o.menu_id = m.menu_id

        ORDER BY o.order_id DESC
    """)

    orders = cursor.fetchall()

    cursor.close()

    return render_template(
        "orders.html",
        orders=orders
    )

@app.route("/add_order", methods=["GET", "POST"])
def add_order():

    cursor = connection.cursor()

    if request.method == "POST":

        customer_id = request.form["customer_id"]
        table_id = request.form["table_id"]
        menu_id = request.form["menu_id"]
        quantity = int(request.form["quantity"])

        # Get menu price
        cursor.execute(
            "SELECT price FROM menu WHERE menu_id=%s",
            (menu_id,)
        )

        item = cursor.fetchone()

        price = float(item["price"])

        total_amount = price * quantity

        sql = """
        INSERT INTO orders
        (customer_id, table_id, menu_id, quantity, total_amount, order_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                customer_id,
                table_id,
                menu_id,
                quantity,
                total_amount,
                "Preparing"
            )
        )

        connection.commit()

        cursor.close()

        return redirect("/orders")

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    cursor.execute("SELECT * FROM restaurant_tables")
    tables = cursor.fetchall()

    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()

    cursor.close()

    return render_template(
        "add_order.html",
        customers=customers,
        tables=tables,
        menu=menu
    )

@app.route("/invoice/<int:id>")
def invoice(id):

    cursor = connection.cursor()

    cursor.execute("""
    SELECT

    o.order_id,
    o.quantity,
    o.total_amount,
    o.order_status,
    o.order_date,

    c.customer_name,

    t.table_number,

    m.item_name

    FROM orders o

    JOIN customers c
    ON o.customer_id=c.customer_id

    JOIN restaurant_tables t
    ON o.table_id=t.table_id

    JOIN menu m
    ON o.menu_id=m.menu_id

    WHERE o.order_id=%s
    """, (id,))

    order = cursor.fetchone()

    cursor.close()

    return render_template(
        "invoice.html",
        order=order
    )

@app.route("/mark_served/<int:id>")
def mark_served(id):

    cursor = connection.cursor()

    cursor.execute("""
    UPDATE orders
    SET order_status='Served'
    WHERE order_id=%s
    """, (id,))

    connection.commit()

    cursor.close()

    return redirect(f"/invoice/{id}")

@app.route("/mark_paid/<int:id>")
def mark_paid(id):

    cursor = connection.cursor()

    cursor.execute("""
    UPDATE orders
    SET order_status='Paid'
    WHERE order_id=%s
    """, (id,))

    connection.commit()

    cursor.close()

    return redirect(f"/invoice/{id}")

@app.route("/billing")
def billing():

    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        o.order_id,
        c.customer_name,
        o.total_amount,
        o.order_status,
        o.order_date

    FROM orders o

    JOIN customers c
    ON o.customer_id = c.customer_id

    WHERE o.order_status='Paid'

    ORDER BY o.order_date DESC
    """)

    bills = cursor.fetchall()

    cursor.close()

    return render_template(
        "billing.html",
        bills=bills
    )

@app.route("/reports")
def reports():

    cursor = connection.cursor()

    # Total Revenue
    cursor.execute("""
        SELECT SUM(total_amount) AS revenue
        FROM orders
        WHERE order_status='Paid'
    """)
    revenue = cursor.fetchone()["revenue"]

    if revenue is None:
        revenue = 0

    # Total Paid Orders
    cursor.execute("""
        SELECT COUNT(*) AS total_paid
        FROM orders
        WHERE order_status='Paid'
    """)
    total_paid = cursor.fetchone()["total_paid"]

    # Average Bill
    cursor.execute("""
        SELECT AVG(total_amount) AS average_bill
        FROM orders
        WHERE order_status='Paid'
    """)
    average_bill = cursor.fetchone()["average_bill"]

    if average_bill is None:
        average_bill = 0

    # Get all paid orders
    cursor.execute("""
        SELECT
            o.order_id,
            c.customer_name,
            o.total_amount,
            o.order_date
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        WHERE o.order_status = 'Paid'
        ORDER BY o.order_date DESC
    """)

    orders = cursor.fetchall()

    cursor.close()

    return render_template(
        "reports.html",
        revenue=revenue,
        total_paid=total_paid,
        average_bill=average_bill,
        orders=orders
    )

@app.route("/customer_menu")
def customer_menu():

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM menu")

    menu_items = cursor.fetchall()

    cursor.close()

    return render_template(
        "customer_menu.html",
        menu_items=menu_items
    )

@app.route("/place_order/<int:menu_id>")
def place_order(menu_id):

    # Get logged-in customer
    customer_id = session.get("customer_id")

    if not customer_id:
        return redirect("/")

    cursor = connection.cursor()

    # Get menu item price
    cursor.execute(
        "SELECT price FROM menu WHERE menu_id=%s",
        (menu_id,)
    )

    item = cursor.fetchone()

    if not item:
        cursor.close()
        return "Menu item not found"

    price = item["price"]

    # Create order for the logged-in customer
    cursor.execute("""
        INSERT INTO orders
        (
            customer_id,
            menu_id,
            quantity,
            total_amount,
            order_status
        )
        VALUES
        (
            %s,
            %s,
            1,
            %s,
            'Preparing'
        )
    """, (
        customer_id,
        menu_id,
        price
    ))

    connection.commit()

    cursor.close()

    return redirect("/my_orders")


@app.route("/my_orders")
def my_orders():

    customer_id = session.get("customer_id")

    if not customer_id:
        return redirect("/")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            o.order_id,
            m.item_name,
            o.quantity,
            o.total_amount,
            o.order_status,
            o.order_date

        FROM orders o

        JOIN menu m
        ON o.menu_id = m.menu_id

        WHERE o.customer_id = %s

        ORDER BY o.order_id DESC
    """, (customer_id,))

    orders = cursor.fetchall()

    cursor.close()

    return render_template(
        "my_orders.html",
        orders=orders
    )

@app.route("/my_bills")
def my_bills():

    customer_id = session.get("customer_id")

    if not customer_id:
        return redirect("/")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            o.order_id,
            m.item_name,
            o.quantity,
            o.total_amount,
            o.order_status,
            o.order_date

        FROM orders o

        JOIN menu m
        ON o.menu_id = m.menu_id

        WHERE o.customer_id = %s

        ORDER BY o.order_id DESC
    """, (customer_id,))

    bills = cursor.fetchall()

    cursor.close()

    return render_template(
        "my_bills.html",
        bills=bills
    )

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        rating = request.form["rating"]
        comments = request.form["comments"]

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO feedback
            (
                customer_name,
                rating,
                comments
            )
            VALUES
            (%s, %s, %s)
        """, (customer_name, rating, comments))

        connection.commit()

        cursor.close()

        return "Feedback Submitted Successfully!"

    return render_template("feedback.html")


@app.route("/view_feedback")
def view_feedback():

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM feedback
        ORDER BY feedback_id DESC
    """)

    feedbacks = cursor.fetchall()

    cursor.close()

    return render_template(
        "view_feedback.html",
        feedbacks=feedbacks
    )

@app.route("/logout")
def logout():

    return redirect("/")

@app.route("/pay_order/<int:order_id>")
def pay_order(order_id):

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE orders
        SET order_status='Paid'
        WHERE order_id=%s
    """, (order_id,))

    connection.commit()

    cursor.close()

    return redirect("/my_bills")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        username = request.form["username"]
        password = request.form["password"]

        cursor = connection.cursor()

        # Check whether username already exists
        cursor.execute(
            "SELECT * FROM customers WHERE username=%s",
            (username,)
        )

        existing_customer = cursor.fetchone()

        if existing_customer:
            cursor.close()
            return "Username already exists. Please choose another username."

        # Insert new customer
        cursor.execute("""
            INSERT INTO customers
            (customer_name, phone, username, password)
            VALUES (%s, %s, %s, %s)
        """, (
            customer_name,
            phone,
            username,
            password
        ))

        connection.commit()

        cursor.close()

        return redirect("/")

    return render_template("register.html")
    

if __name__ == "__main__":
    app.run(debug=True)