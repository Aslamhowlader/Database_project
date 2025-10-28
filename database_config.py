import mysql.connector
from mysql.connector import Error
import hashlib

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
        self.create_default_admin()

    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='citizen_portal_db'
            )
            print(" Database connected successfully")
            return True
        except Error as e:
            print(f" Error connecting to MySQL: {e}")
            return self.create_database()

    def create_database(self):
        """Create database if it doesn't exist"""
        try:
            temp_connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password=''
            )
            cursor = temp_connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS citizen_portal_db")
            print("Database created successfully")
            cursor.close()
            temp_connection.close()
            
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='citizen_portal_db'
            )
            return True
        except Error as e:
            print(f" Error creating database: {e}")
            return False

    def create_tables(self):
        """Create all necessary tables"""
        try:
            cursor = self.connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    phone VARCHAR(20) NOT NULL,
                    nid VARCHAR(50) UNIQUE NOT NULL,
                    date_of_birth DATE NOT NULL,
                    address TEXT NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('Citizen', 'Government Officer', 'Administrator') NOT NULL,
                    status ENUM('Active', 'Inactive') DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.connection.commit()
            cursor.close()
            print("Tables created successfully")
            return True

        except Error as e:
            print(f" Error creating tables: {e}")
            return False

    def create_default_admin(self):
        """Create default admin account"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                password_hash = self.hash_password("admin123")
                cursor.execute('''
                    INSERT INTO users (full_name, email, phone, nid, date_of_birth, address, username, password_hash, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', ("System Administrator", "admin@gov.bd", "01700000000", 
                      "0000000000000", "2000-01-01", "Government Building", 
                      "admin", password_hash, "Administrator"))
                
                self.connection.commit()
                print(" Default admin account created")
            
            cursor.close()
            return True
            
        except Error as e:
            print(f" Error creating default admin: {e}")
            return False

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, user_data):
        """Register a new user"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = %s", (user_data['username'],))
            if cursor.fetchone():
                return False, "Username already exists"
            
            cursor.execute("SELECT id FROM users WHERE nid = %s", (user_data['nid'],))
            if cursor.fetchone():
                return False, "NID already registered"
            
            if user_data['email']:
                cursor.execute("SELECT id FROM users WHERE email = %s", (user_data['email'],))
                if cursor.fetchone():
                    return False, "Email already registered"
            
            password_hash = self.hash_password(user_data['password'])
            
            cursor.execute('''
                INSERT INTO users (full_name, email, phone, nid, date_of_birth, address, username, password_hash, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                user_data['full_name'],
                user_data['email'],
                user_data['phone'],
                user_data['nid'],
                user_data['date_of_birth'],
                user_data['address'],
                user_data['username'],
                password_hash,
                user_data['role']
            ))
            
            self.connection.commit()
            cursor.close()
            return True, "Registration successful! Please login."
            
        except Error as e:
            return False, f"Database error: {str(e)}"

    def login_user(self, username, password):
        """Authenticate user login"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT id, full_name, username, password_hash, role, email 
                FROM users WHERE username = %s AND status = 'Active'
            ''', (username,))
            
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                user_id, full_name, username_db, password_hash, role, email = user
                if self.hash_password(password) == password_hash:
                    return True, {
                        "id": user_id,
                        "name": full_name,
                        "username": username_db,
                        "role": role,
                        "email": email
                    }
                else:
                    return False, "Invalid password"
            else:
                return False, "User not found"
                
        except Error as e:
            return False, f"Database error: {str(e)}"

    def check_username_availability(self, username):
        """Check if username is available"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone() is None
            cursor.close()
            return result
        except Error:
            return False

    def check_nid_availability(self, nid):
        """Check if NID is available"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM users WHERE nid = %s", (nid,))
            result = cursor.fetchone() is None
            cursor.close()
            return result
        except Error:
            return False