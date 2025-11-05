import re
from database_config import DatabaseManager

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()

    def validate_email(self, email):
        """Validate email format"""
        if not email:
            return True
        pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        """Validate phone number"""
        pattern = r'^01[3-9]\d{8}$'
        return re.match(pattern, phone) is not None

    def validate_nid(self, nid):
        """Validate NID number"""
        return nid.isdigit() and 10 <= len(nid) <= 17

    def validate_date(self, date_str):
        """Validate date format YYYY-MM-DD"""
        try:
            year, month, day = map(int, date_str.split('-'))
            if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
                return False
            if year < 1900 or year > 2023:
                return False
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            return True
        except:
            return False

    def register_user(self, user_data):
        """Register a new user with validation"""
        # Required fields validation
        required_fields = [
            ('full_name', 'Full Name'),
            ('phone', 'Phone Number'),
            ('nid', 'NID Number'),
            ('date_of_birth', 'Date of Birth'),
            ('address', 'Address'),
            ('username', 'Username'),
            ('password', 'Password')
        ]
        
        for field, field_name in required_fields:
            if not user_data.get(field):
                return False, f"{field_name} is required"
        
        # Email validation
        if user_data.get('email') and not self.validate_email(user_data['email']):
            return False, "Please enter a valid email address"
        
        # Phone validation
        if not self.validate_phone(user_data['phone']):
            return False, "Please enter a valid Bangladeshi phone number (01XXXXXXXXX)"
        
        # NID validation
        if not self.validate_nid(user_data['nid']):
            return False, "Please enter a valid NID number (10-17 digits)"
        
        # Date validation
        if not self.validate_date(user_data['date_of_birth']):
            return False, "Please enter date in YYYY-MM-DD format"
        
        # Password strength
        if len(user_data['password']) < 6:
            return False, "Password must be at least 6 characters long"
        
        # Database checks
        if not self.db.check_username_availability(user_data['username']):
            return False, "Username already exists"
        
        if not self.db.check_nid_availability(user_data['nid']):
            return False, "NID already registered"
        
        # Register user in database
        return self.db.register_user(user_data)

    def login_user(self, username, password):
        """Authenticate user login"""
        if not username or not password:
            return False, "Please enter both username and password"
        
        return self.db.login_user(username, password)

    # Admin methods
    def get_all_users(self, admin_id):
        """Get all users (admin only)"""
        return self.db.get_all_users(admin_id)

    def update_user_status(self, user_id, status):
        """Update user status"""
        return self.db.update_user_status(user_id, status)

    def delete_user(self, user_id):
        """Delete a user"""
        return self.db.delete_user(user_id)

    def update_user_role(self, user_id, new_role):
        """Update user role"""
        return self.db.update_user_role(user_id, new_role)

    def get_user_stats(self):
        """Get user statistics"""
        return self.db.get_user_stats()

    # Service methods
    def create_service(self, service_data):
        """Create a new service"""
        return self.db.create_service(service_data)

    def get_all_services(self):
        """Get all services"""
        return self.db.get_all_services()

    # Application methods
    def create_application(self, application_data):
        """Create a new application"""
        return self.db.create_application(application_data)

    def get_user_applications(self, user_id):
        """Get user applications"""
        return self.db.get_user_applications(user_id)

    def get_all_applications(self):
        """Get all applications"""
        return self.db.get_all_applications()

    def update_application_status(self, application_id, status, processed_by, notes=None):
        """Update application status"""
        return self.db.update_application_status(application_id, status, processed_by, notes)

    # Report methods - ADMIN ONLY
    def submit_citizen_report(self, report_data):
        """Submit a citizen report"""
        return self.db.submit_report(report_data)

    def get_user_reports(self, user_id):
        """Get reports for a specific user"""
        return self.db.get_user_reports(user_id)

    def get_all_reports(self):
        """Get all reports (Admin only)"""
        return self.db.get_all_reports()

    def get_department_reports(self, department):
        """Get reports by department"""
        return self.db.get_reports_by_department(department)

    def update_report_status(self, report_id, status, assigned_to=None, feedback=None):
        """Update report status"""
        return self.db.update_report_status(report_id, status, assigned_to, feedback)

    def delete_report(self, report_id):
        """Delete a report (Admin only)"""
        return self.db.delete_report(report_id)

    def get_report_by_id(self, report_id):
        """Get specific report by ID"""
        return self.db.get_report_by_id(report_id)

    def update_report_details(self, report_id, title, description, category, priority):
        """Update report details"""
        return self.db.update_report_details(report_id, title, description, category, priority)

    def get_report_stats(self):
        """Get report statistics"""
        return self.db.get_report_stats()

    def assign_report_to_officer(self, report_id, officer_id):
        """Assign report to government officer"""
        return self.db.assign_report_to_officer(report_id, officer_id)