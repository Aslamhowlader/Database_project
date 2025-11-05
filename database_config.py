import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime

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
            print("✅ Database connected successfully")
            return True
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
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
            print("✅ Database created successfully")
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
            print(f"❌ Error creating database: {e}")
            return False

    def create_tables(self):
        """Create all necessary tables"""
        try:
            cursor = self.connection.cursor()

            # Users table
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
                    department VARCHAR(100),
                    status ENUM('Active', 'Inactive', 'Suspended') DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    profile_picture VARCHAR(255) DEFAULT NULL
                )
            ''')

            # Services table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    category VARCHAR(100),
                    department VARCHAR(100),
                    requirements JSON,
                    processing_time VARCHAR(50),
                    fee DECIMAL(10,2) DEFAULT 0.00,
                    status ENUM('Active', 'Inactive') DEFAULT 'Active',
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            ''')

            # Applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    service_id INT NOT NULL,
                    application_data JSON,
                    status ENUM('Pending', 'Approved', 'Rejected', 'In Review') DEFAULT 'Pending',
                    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_date TIMESTAMP NULL,
                    processed_by INT NULL,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (service_id) REFERENCES services(id),
                    FOREIGN KEY (processed_by) REFERENCES users(id)
                )
            ''')

            # Reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    category ENUM('Infrastructure', 'Health', 'Education', 'Utility', 'Environment', 'Other') NOT NULL,
                    location VARCHAR(255),
                    image_url VARCHAR(500),
                    status ENUM('Pending', 'In Progress', 'Resolved', 'Rejected') DEFAULT 'Pending',
                    priority ENUM('Low', 'Medium', 'High', 'Emergency') DEFAULT 'Medium',
                    assigned_to INT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP NULL,
                    feedback TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (assigned_to) REFERENCES users(id)
                )
            ''')

            self.connection.commit()
            cursor.close()
            print("✅ Tables created successfully")
            return True

        except Error as e:
            print(f"❌ Error creating tables: {e}")
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
                print("✅ Default admin account created")
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"❌ Error creating default admin: {e}")
            return False

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    # User Management Methods
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
                INSERT INTO users (full_name, email, phone, nid, date_of_birth, address, username, password_hash, role, department)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                user_data['full_name'],
                user_data['email'],
                user_data['phone'],
                user_data['nid'],
                user_data['date_of_birth'],
                user_data['address'],
                user_data['username'],
                password_hash,
                user_data['role'],
                user_data.get('department')
            ))
            
            self.connection.commit()
            cursor.close()
            return True, "Registration successful! Please login."
            
        except Error as e:
            return False, f"Database error: {str(e)}"

    def login_user(self, username, password):
        """Authenticate user login"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute('''
                SELECT id, full_name, username, password_hash, role, email, status, department
                FROM users WHERE username = %s
            ''', (username,))
            
            user = cursor.fetchone()
            
            if user:
                if user['status'] != 'Active':
                    cursor.close()
                    return False, "Your account is not active. Please contact administrator."
                
                if self.hash_password(password) == user['password_hash']:
                    # Update last login
                    cursor.execute('''
                        UPDATE users SET last_login = NOW() WHERE id = %s
                    ''', (user['id'],))
                    self.connection.commit()
                    cursor.close()
                    
                    return True, {
                        "id": user['id'],
                        "name": user['full_name'],
                        "username": user['username'],
                        "role": user['role'],
                        "email": user['email'],
                        "status": user['status'],
                        "department": user['department']
                    }
                else:
                    cursor.close()
                    return False, "Invalid password"
            else:
                cursor.close()
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

    def get_all_users(self, current_admin_id=None):
        """Get all users (admin only)"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if current_admin_id:
                cursor.execute('''
                    SELECT id, full_name, email, phone, nid, date_of_birth, 
                           address, username, role, department, status, created_at, last_login
                    FROM users WHERE id != %s ORDER BY created_at DESC
                ''', (current_admin_id,))
            else:
                cursor.execute('''
                    SELECT id, full_name, email, phone, nid, date_of_birth, 
                           address, username, role, department, status, created_at, last_login
                    FROM users ORDER BY created_at DESC
                ''')
            users = cursor.fetchall()
            cursor.close()
            return True, users
        except Error as e:
            return False, f"Database error: {str(e)}"

    def update_user_status(self, user_id, status):
        """Update user status (Active/Inactive/Suspended)"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE users SET status = %s WHERE id = %s
            ''', (status, user_id))
            self.connection.commit()
            cursor.close()
            return True, "User status updated successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def delete_user(self, user_id):
        """Delete a user"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            self.connection.commit()
            cursor.close()
            return True, "User deleted successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def update_user_role(self, user_id, new_role):
        """Update user role"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE users SET role = %s WHERE id = %s
            ''', (new_role, user_id))
            self.connection.commit()
            cursor.close()
            return True, "User role updated successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_user_stats(self):
        """Get user statistics for admin dashboard"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Total users
            cursor.execute('SELECT COUNT(*) as total FROM users')
            total_users = cursor.fetchone()['total']
            
            # Users by role
            cursor.execute('''
                SELECT role, COUNT(*) as count 
                FROM users 
                GROUP BY role
            ''')
            users_by_role = cursor.fetchall()
            
            # Users by status
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM users 
                GROUP BY status
            ''')
            users_by_status = cursor.fetchall()
            
            # Recent registrations (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) as recent 
                FROM users 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ''')
            recent_registrations = cursor.fetchone()['recent']
            
            cursor.close()
            
            stats = {
                'total_users': total_users,
                'users_by_role': users_by_role,
                'users_by_status': users_by_status,
                'recent_registrations': recent_registrations
            }
            
            return True, stats
        except Error as e:
            return False, f"Database error: {str(e)}"

    # Service Management Methods
    def create_service(self, service_data):
        """Create a new service"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO services (name, description, category, department, requirements, processing_time, fee, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (service_data['name'], service_data['description'], 
                  service_data['category'], service_data.get('department'),
                  service_data.get('requirements'), service_data.get('processing_time'),
                  service_data.get('fee', 0.00), service_data['created_by']))
            
            self.connection.commit()
            service_id = cursor.lastrowid
            cursor.close()
            return True, f"Service created successfully (ID: {service_id})"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_all_services(self):
        """Get all services"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT s.*, u.full_name as created_by_name 
                FROM services s 
                LEFT JOIN users u ON s.created_by = u.id 
                ORDER BY s.created_at DESC
            ''')
            services = cursor.fetchall()
            cursor.close()
            return True, services
        except Error as e:
            return False, f"Database error: {str(e)}"

    # Application Management Methods
    def create_application(self, application_data):
        """Create a new service application"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO applications (user_id, service_id, application_data, status)
                VALUES (%s, %s, %s, %s)
            ''', (application_data['user_id'], application_data['service_id'],
                  application_data['application_data'], 'Pending'))
            
            self.connection.commit()
            application_id = cursor.lastrowid
            cursor.close()
            return True, f"Application submitted successfully (ID: {application_id})"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_user_applications(self, user_id):
        """Get applications for a specific user"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT a.*, s.name as service_name, s.category as service_category
                FROM applications a
                JOIN services s ON a.service_id = s.id
                WHERE a.user_id = %s
                ORDER BY a.applied_date DESC
            ''', (user_id,))
            applications = cursor.fetchall()
            cursor.close()
            return True, applications
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_all_applications(self):
        """Get all applications (for admin/officers)"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT a.*, s.name as service_name, u.full_name as applicant_name,
                       u.username as applicant_username, p.full_name as processor_name
                FROM applications a
                JOIN services s ON a.service_id = s.id
                JOIN users u ON a.user_id = u.id
                LEFT JOIN users p ON a.processed_by = p.id
                ORDER BY a.applied_date DESC
            ''')
            applications = cursor.fetchall()
            cursor.close()
            return True, applications
        except Error as e:
            return False, f"Database error: {str(e)}"

    def update_application_status(self, application_id, status, processed_by, notes=None):
        """Update application status"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE applications 
                SET status = %s, processed_by = %s, processed_date = NOW(), notes = %s
                WHERE id = %s
            ''', (status, processed_by, notes, application_id))
            
            self.connection.commit()
            cursor.close()
            return True, "Application status updated successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    # Report Management Methods - ADMIN ONLY
    def submit_report(self, report_data):
        """Submit a citizen report"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO reports (user_id, title, description, category, location, image_url, priority)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (report_data['user_id'], report_data['title'], report_data['description'],
                  report_data['category'], report_data.get('location'), 
                  report_data.get('image_url'), report_data.get('priority', 'Medium')))
            
            self.connection.commit()
            report_id = cursor.lastrowid
            cursor.close()
            return True, f"Report submitted successfully (ID: {report_id})"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_user_reports(self, user_id):
        """Get reports for a specific user"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT r.*, u.full_name as assigned_officer
                FROM reports r
                LEFT JOIN users u ON r.assigned_to = u.id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
            ''', (user_id,))
            reports = cursor.fetchall()
            cursor.close()
            return True, reports
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_all_reports(self):
        """Get all reports (Admin only)"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT r.*, u1.full_name as reporter_name, u2.full_name as assigned_officer,
                       u1.username as reporter_username, u1.phone as reporter_phone
                FROM reports r
                JOIN users u1 ON r.user_id = u1.id
                LEFT JOIN users u2 ON r.assigned_to = u2.id
                ORDER BY r.created_at DESC
            ''')
            reports = cursor.fetchall()
            cursor.close()
            return True, reports
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_report_by_id(self, report_id):
        """Get specific report by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT r.*, u1.full_name as reporter_name, u2.full_name as assigned_officer,
                       u1.username as reporter_username, u1.phone as reporter_phone,
                       u1.email as reporter_email
                FROM reports r
                JOIN users u1 ON r.user_id = u1.id
                LEFT JOIN users u2 ON r.assigned_to = u2.id
                WHERE r.id = %s
            ''', (report_id,))
            report = cursor.fetchone()
            cursor.close()
            if report:
                return True, report
            else:
                return False, "Report not found"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_reports_by_department(self, department):
        """Get reports by department category"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT r.*, u1.full_name as reporter_name, u2.full_name as assigned_officer
                FROM reports r
                JOIN users u1 ON r.user_id = u1.id
                LEFT JOIN users u2 ON r.assigned_to = u2.id
                WHERE r.category = %s
                ORDER BY r.created_at DESC
            ''', (department,))
            reports = cursor.fetchall()
            cursor.close()
            return True, reports
        except Error as e:
            return False, f"Database error: {str(e)}"

    def update_report_status(self, report_id, status, assigned_to=None, feedback=None):
        """Update report status"""
        try:
            cursor = self.connection.cursor()
            if status == 'Resolved':
                cursor.execute('''
                    UPDATE reports 
                    SET status = %s, assigned_to = %s, resolved_at = NOW(), feedback = %s
                    WHERE id = %s
                ''', (status, assigned_to, feedback, report_id))
            else:
                cursor.execute('''
                    UPDATE reports 
                    SET status = %s, assigned_to = %s, feedback = %s
                    WHERE id = %s
                ''', (status, assigned_to, feedback, report_id))
            
            self.connection.commit()
            cursor.close()
            return True, "Report status updated successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def update_report_details(self, report_id, title, description, category, priority):
        """Update report details"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE reports 
                SET title = %s, description = %s, category = %s, priority = %s
                WHERE id = %s
            ''', (title, description, category, priority, report_id))
            
            self.connection.commit()
            cursor.close()
            return True, "Report details updated successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def delete_report(self, report_id):
        """Delete a report (Admin only)"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM reports WHERE id = %s', (report_id,))
            self.connection.commit()
            cursor.close()
            return True, "Report deleted successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def assign_report_to_officer(self, report_id, officer_id):
        """Assign report to government officer"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE reports 
                SET assigned_to = %s, status = 'In Progress'
                WHERE id = %s
            ''', (officer_id, report_id))
            
            self.connection.commit()
            cursor.close()
            return True, "Report assigned to officer successfully"
        except Error as e:
            return False, f"Database error: {str(e)}"

    def get_report_stats(self):
        """Get report statistics"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Total reports
            cursor.execute('SELECT COUNT(*) as total FROM reports')
            total_reports = cursor.fetchone()['total']
            
            # Reports by status
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM reports 
                GROUP BY status
            ''')
            reports_by_status = cursor.fetchall()
            
            # Reports by category
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM reports 
                GROUP BY category
            ''')
            reports_by_category = cursor.fetchall()
            
            # Recent reports (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) as recent 
                FROM reports 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ''')
            recent_reports = cursor.fetchone()['recent']
            
            cursor.close()
            
            stats = {
                'total_reports': total_reports,
                'reports_by_status': reports_by_status,
                'reports_by_category': reports_by_category,
                'recent_reports': recent_reports
            }
            
            return True, stats
        except Error as e:
            return False, f"Database error: {str(e)}"