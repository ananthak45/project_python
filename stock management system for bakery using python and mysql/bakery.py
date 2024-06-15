from flask import Flask, render_template, request,redirect, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'root',
    'password': 'Praveen@16',
    'host': '127.0.0.1',
    'database': 'cakeshop'
}

# Helper function to get a database connection
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

@app.route('/',methods=['POST','GET'])
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_time = datetime.now()

        # Store login information in the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO login (username, password, login_time) VALUES (%s, %s, %s)",
            (username, password, login_time)
        )
        connection.commit()
        cursor.close()
        connection.close()

        return render_template('home.html')
    return render_template('login.html')

@app.route('/home',methods=['POST','GET'])
def home():
    return render_template('home.html')

@app.route('/billing',methods=['POST'])
def billing():
    return render_template('billing.html')

@app.route('/customers',methods=['POST','GET'])
def customers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT customer_name, customer_phone, bill_date FROM bills")
    customers_data = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('customers.html', customers_data=customers_data)
@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
  
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT category FROM stocks")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('stocks.html', categories=categories)



@app.route('/stocks/<category>')
def get_stocks_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT name, quantity FROM stocks WHERE category = %s"
    cursor.execute(query, (category,))
    stocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('stocks_category.html', category=category, stocks=stocks)


@app.route('/get_categories', methods=['GET'])
def get_categories():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT category FROM stocks")
    categories = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify({'categories': [cat['category'] for cat in categories]})

@app.route('/submit_bill', methods=['POST'])
def submit_bill():
    data = request.get_json()
    customer_name = data['customerName']
    customer_phone = data['customerPhone']
    bill_items = data['billItems']

    connection = get_db_connection()
    cursor = connection.cursor()

    # Insert the bill into the bills table
    bill_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO bills (customer_name, customer_phone, bill_date) VALUES (%s, %s, %s)",
        (customer_name, customer_phone, bill_date)
    )
    bill_id = cursor.lastrowid

    # Insert each bill item into the bill_items table and update the stocks table
    for item in bill_items:
        cursor.execute(
            "INSERT INTO bill_items (bill_id, item_name, category, quantity, price) VALUES (%s, %s, %s, %s, %s)",
            (bill_id, item['itemName'], item['category'], item['quantity'], item['price'])
        )
        cursor.execute(
            "UPDATE stocks SET quantity = quantity - %s WHERE name = %s AND category = %s",
            (item['quantity'], item['itemName'], item['category'])
        )

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Bill saved successfully!"})

@app.route('/suppliers', methods=['GET','POST'])
def supplier():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM supplier")
    suppliers = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('suppliers.html', suppliers=suppliers)

if __name__ == '__main__':
    app.run(debug=True)
