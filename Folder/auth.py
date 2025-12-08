import json
import os
import pathlib

class Auth:
    def __init__(self):
        # Save to Desktop as a txt file containing JSON
        self.desktop = pathlib.Path.home() / "Desktop"
        self.db_file = self.desktop / "users_credentials.txt"
        self.users = self.load_users()

    def load_users(self):
        # Create the file if it doesn't exist
        if not os.path.exists(self.db_file):
            return {}
        try:
            with open(self.db_file, "r") as f:
                content = f.read().strip()
                if not content: return {}
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_users(self):
        with open(self.db_file, "w") as f:
            json.dump(self.users, f, indent=4)

    def login(self, username, password):
        if username in self.users:
            # DIRECT PLAIN TEXT COMPARISON
            if self.users[username] == password:
                return True, "Login successful"
            else:
                return False, "Incorrect password"
        return False, "User not found"

    def signup(self, username, password):
        if not username or not password:
             return False, "Username and password cannot be empty"
        
        if len(password) < 4:
            return False, "Password must be at least 4 characters"

        if username in self.users:
            return False, "Username already exists"
        
        # SAVE PLAIN TEXT PASSWORD
        self.users[username] = password
        self.save_users()
        return True, "Signup successful! Please login."
