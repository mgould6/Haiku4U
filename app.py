from flask import Flask, session, request, jsonify, render_template, abort
import pyodbc
import hashlib
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = 'some_random_secret_key'


# Update with your SQL Server credentials and database details
connection_string = (
    'DRIVER={SQL Server};'
    'SERVER=MGOULD;'  # Update server_name
    'DATABASE=HaikuDB;'  # Update database_name
    'Trusted_Connection=yes;'  # Use Windows Authentication

)

# Establish a database connection
connection = pyodbc.connect(connection_string)
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify(status="success", message="Logout successful"), 200

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
        SELECT * FROM UsersTable 
        WHERE UserName = '{username}' AND PasswordHash = '{hashed_password}'
    """
    
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    
    # Check if a result was returned
    if result:
        session['username'] = username
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
            SELECT * FROM UsersTable
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
            INSERT INTO UsersTable (UserName, Email, PasswordHash)
            VALUES ('{username}', '{email}', '{hashed_password}')
        """
        
        cursor.execute(insert_query)
        connection.commit()  # Commit the transaction

        return jsonify(status="success", message="Signup successful"), 201
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred", 500

@app.route('/user/<username>', methods=['GET', 'PUT', 'DELETE'])
def user_profile(username):
     # Check if user is logged in and the session username matches the URL username
    session_username = session.get('username')
    if session_username is None or session_username != username:
        return jsonify(status="failure", message="Unauthorized"), 403
    
    try:
        cursor = connection.cursor()

        if request.method == 'GET':
            # Fetch user data code here
            query = "SELECT * FROM UsersTable WHERE UserName = ?"
            cursor.execute(query, (username,))
            user_data = cursor.fetchone()
            user_data_dict = {
                'UserID': user_data.UserID,
                'UserName': user_data.UserName,
                'Email': user_data.Email,
                # ... other fields
            }
            return jsonify(user_data_dict), 200
        
        elif request.method == 'PUT':
            # Update user data code here
            data = request.get_json()
            if 'email' not in data:
                abort(400, description="Missing email field")
            # Assume data contains the fields to be updated
            query = "UPDATE UsersTable SET Email = ? WHERE UserName = ?"
            cursor.execute(query, (data['email'], username))
            connection.commit()
            return jsonify(status="success", message="User updated successfully"), 200    
            
        elif request.method == 'DELETE':
            # Delete user data code here
            query = "DELETE FROM UsersTable WHERE UserName = ?"
            cursor.execute(query, (username,))
            connection.commit()
            return jsonify(status="success", message="User deleted successfully"), 200
        
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred", 500

@app.route('/haiku/create', methods=['POST'])
def create_haiku():
    try:
        data = request.get_json()  # Get data from request
        if not data:
            return jsonify(status="failure", message="No data provided"), 400
        
        # Extract haiku details from the data
        username = data.get('username')  # Assuming the username is being sent in the request
        haiku_text = data.get('haiku_text')
        title = data.get('title')
        
        # Validation: Ensure all required fields are provided
        if not (username and haiku_text and title):
            return jsonify(status="failure", message="Missing required fields"), 400
        
        # Fetch the user_id from the database based on username
        cursor = connection.cursor()
        user_query = "SELECT UserID FROM UsersTable WHERE UserName = ?"
        cursor.execute(user_query, (username,))
        user_id_result = cursor.fetchone()
        if not user_id_result:
            return jsonify(status="failure", message="User not found"), 404
        user_id = user_id_result.UserID

        # Now, insert the haiku into the database
        insert_query = """
            INSERT INTO HaikuTable (UserID, HaikuText, Title, DateCreated, DateModified)
            VALUES (?, ?, ?, GETDATE(), GETDATE())
        """
        cursor.execute(insert_query, (user_id, haiku_text, title))
        connection.commit()

        return jsonify(status="success", message="Haiku created successfully"), 201
        
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred", 500

@app.route('/haiku/<int:haiku_id>', methods=['GET'])
def get_haiku(haiku_id):
    try:
        cursor = connection.cursor()
        
        # Fetch the haiku details from the database based on haiku_id
        query = "SELECT * FROM HaikuTable WHERE HaikuID = ?"
        cursor.execute(query, (haiku_id,))
        haiku_data = cursor.fetchone()

        if not haiku_data:
            return jsonify(status="failure", message="Haiku not found"), 404

        haiku_dict = {
            'HaikuID': haiku_data.HaikuID,
            'UserID': haiku_data.UserID,
            'HaikuText': haiku_data.HaikuText,
            'Title': haiku_data.Title,
            'DateCreated': str(haiku_data.DateCreated),  # Convert datetime to string for serialization
            'DateModified': str(haiku_data.DateModified)
        }

        return jsonify(haiku_dict), 200
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred", 500

@app.route('/haiku/<int:haiku_id>', methods=['PUT'])
def update_haiku(haiku_id):
    try:
        data = request.get_json()
        
        # Extract updated haiku details from the data
        haiku_text = data.get('haiku_text')
        title = data.get('title')

        # Validation: Ensure all required fields are provided
        if not (haiku_text and title):
            return jsonify(status="failure", message="Missing required fields"), 400

        cursor = connection.cursor()

        # Update the haiku details in the database
        update_query = """
            UPDATE HaikuTable 
            SET HaikuText = ?, Title = ?, DateModified = GETDATE()
            WHERE HaikuID = ?
        """
        cursor.execute(update_query, (haiku_text, title, haiku_id))
        connection.commit()

        if cursor.rowcount == 0:  # No rows were updated, indicating the haiku_id was not found
            return jsonify(status="failure", message="Haiku not found"), 404

        return jsonify(status="success", message="Haiku updated successfully"), 200
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred", 500

@app.route('/haiku/<int:haiku_id>', methods=['DELETE'])
def delete_haiku(haiku_id):
    try:
        cursor = connection.cursor()
        
        # Delete the haiku from the database
        delete_query = "DELETE FROM HaikuTable WHERE HaikuID = ?"
        cursor.execute(delete_query, (haiku_id,))
        connection.commit()

        if cursor.rowcount == 0:  # No rows were deleted, indicating the haiku_id was not found
            return jsonify(status="failure", message="Haiku not found"), 404

        return jsonify(status="success", message="Haiku deleted successfully"), 200
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
