import os
from flask import redirect, url_for

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

class User:
    def __init__(self):
        self.user_profile = None
        self.access_token = None
    
    def set_user_profile(self, user_profile):
        self.user_profile = user_profile
    
    def get_user_profile(self):
        return self.user_profile

    def set_access_token(self, access_token):
        self.access_token = access_token

    def get_access_token(self):
        return self.access_token
    
    def validate_access_token(self, func):
        """
        Validate the access token associated with the user.
        """
        def wrapper(*args, **kwargs):
            # Ensure the user has a valid access token
            if self.get_access_token() is None:
                return redirect(url_for('auth.login'))

            # Additional validation logic can be added here if needed

            return func(*args, **kwargs)  # Access token is valid, continue with the request
        wrapper.__name__ = func.__name__
        return wrapper

user_manager = User()
