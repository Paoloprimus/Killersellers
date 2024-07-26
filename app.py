from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname='commic',
            user='postgres',
            password='CommMic24',
            host='localhost',
            port='5432'
        )
        return conn
    except Exception as e:
        logging.error("Error connecting to the database: %s", e)
        return None

@app.route('/')
def home():
    return render_template('micidiale.html')

@app.route('/gestioneutenti')
def gestioneutenti():
    return render_template('gestioneutenti.html')

@app.route('/listautenti')
def listautenti():
    return render_template('listautenti.html')

@app.route('/nuovoutente')
def nuovoutente():
    return render_template('nuovoutente.html')

@app.route('/modificautente')
def modificautente():
    return render_template('modificautente.html')

@app.route('/cancellautente')
def cancellautente():
    return render_template('cancellautente.html')

@app.route('/gestioneclienti')
def gestioneclienti():
    conn = get_db_connection()
    if not conn:
        return "Errore di connessione al database", 500

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM customers;')
    customers = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('gestioneclienti.html', customers=customers)

@app.route('/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Errore di connessione al database"}), 500

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM customers;')
    customers = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(customers)

@app.route('/listaclienti')
def listaclienti():
    return render_template('listaclienti.html')

@app.route('/nuovocliente')
def nuovocliente():
    return render_template('nuovocliente.html')

@app.route('/modificacliente')
def modificacliente():
    return render_template('modificacliente.html')

@app.route('/cancellacliente')
def cancellacliente():
    return render_template('cancellacliente.html')

@app.route('/gestioneordini')
def gestioneordini():
    return render_template('gestioneordini.html')

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT user_id, name, email, role FROM users;')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT user_id, name, email, role FROM users WHERE user_id = %s;', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'password_hash' not in data or 'role' not in data:
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                    (data['name'], data['email'], data['password_hash'], data['role']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'User added'}), 201
    except Exception as e:
        logging.error("Error executing query: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute('UPDATE users SET name=%s, email=%s, password_hash=%s, role=%s WHERE user_id=%s',
                    (data['name'], data['email'], data['password_hash'], data['role'], user_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'User updated'})
    except Exception as e:
        logging.error("Error executing query: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'User deleted'})
    except Exception as e:
        logging.error("Error executing query: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    if not data or 'name' not in data or 'address' not in data or 'contact_info' not in data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO customers (name, address, contact_info, latitude, longitude) VALUES (%s, %s, %s, %s, %s)',
                    (data['name'], data['address'], data['contact_info'], float(data['latitude']), float(data['longitude'])))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Customer added'}), 201
    except (psycopg2.Error, ValueError) as e:
        logging.error("Error executing query: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM customers WHERE customer_id = %s;', (customer_id,))
        customer = cur.fetchone()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Aggiorna solo i campi forniti nel payload
        updated_name = data.get('name', customer['name'])
        updated_address = data.get('address', customer['address'])
        updated_contact_info = data.get('contact_info', customer['contact_info'])
        updated_latitude = data.get('latitude', customer['latitude'])
        updated_longitude = data.get('longitude', customer['longitude'])

        cur.execute(
            'UPDATE customers SET name=%s, address=%s, contact_info=%s, latitude=%s, longitude=%s WHERE customer_id=%s',
            (updated_name, updated_address, updated_contact_info, float(updated_latitude), float(updated_longitude),
             customer_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Customer updated'})
    except (psycopg2.Error, ValueError) as e:
        logging.error("Error executing query: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM customers WHERE customer_id = %s', (customer_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Customer deleted'})
    except Exception as e:
        logging.error("Error executing query: %s", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
