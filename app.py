from flask import Flask, request, jsonify, render_template
import pyodbc
import hashlib
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)

# Update with your SQL Server credentials and database details
connection_string = (
    'DRIVER={SQL Server};'
    'SERVER=MGOULD;'  # Update server_name
    'DATABASE=HaikuDB;'  # Update database_name
    'Trusted_Connection=yes;'  # Use Windows Authentication

)

# Establish a database connection
connection = pyodbc.connect(connection_string)

@app.route('/login', methods=['POST'])
def login():
    # Retrieve data from the request
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')  # Assuming plaintext, you should hash this before querying

    # Hash the password (using SHA-256 for this example)
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Your SQL query to check credentials. Update table_name and column names
    query = f"""
        SELECT * FROM Table_1 
        WHERE UserName = '{username}' AND PasswordHash = '{hashed_password}'
    """
    
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    
    # Check if a result was returned
    if result:
        return jsonify(status="success", message="Login successful"), 200
    else:
        return jsonify(status="failure", message="Invalid credentials"), 401

@app.route('/signup', methods=['POST'])
def signup():
    try:
        # Retrieve data from the request
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')  # Assuming plaintext, you should hash this before storing

        # Hash the password (using SHA-256 for this example)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Your SQL query to check for duplicate usernames or emails.
        check_query = f"""
            SELECT * FROM Table_1
            WHERE UserName = '{username}' OR Email = '{email}'
        """

        cursor = connection.cursor()
        cursor.execute(check_query)
        result = cursor.fetchone()

        # Check if a result was returned indicating a duplicate username or email
        if result:
            return jsonify(status="failure", message="Username or email already exists"), 400

        # Your SQL query to insert the new user data. Update table_name and column names
        insert_query = f"""
            INSERT INTO Table_1 (UserName, Email, PasswordHash)
            VALUES ('{username}', '{email}', '{hashed_password}')
        """
        
        cursor.execute(insert_query)
        connection.commit()  # Commit the transaction

        return jsonify(status="success", message="Signup successful"), 201
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred", 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run the Flask app on localhost, port 5000. Update if necessary
    app.run(debug=True)
