import re
from database_config import DatabaseManager

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()

    def validate_email(self, email):
        """Validate email format"""
        if not email:
            return True
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
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