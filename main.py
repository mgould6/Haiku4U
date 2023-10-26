from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import re
from email_validator import validate_email, EmailNotValidError

# Load the login screen kv file at the module level
Builder.load_file('login_screen.kv')
Builder.load_file('sign_up_screen.kv')

# Define each screen as a class
class LoginScreen(Screen):
    pass

class SignUpScreen(Screen):
    pass

class HomeScreen(Screen):
    pass

class CreateHaikuScreen(Screen):
    pass

class ProfileScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class ExploreScreen(Screen):
    pass

class NotificationsScreen(Screen):
    pass

class MainApp(App):
    def validate_email(self, email):
        try:
            v = validate_email(email)
            print("The email address is valid.")
            return True
        except EmailNotValidError as e:
            print(str(e))
            return False
    
    def username_filter(self, value, undo_operation):
        if 3 <= len(value) <= 30 and re.match('^[a-zA-Z0-9_-]*$', value):
            return value
        return undo_operation

    def password_filter(self, value, undo_operation):
        if len(value) < 8:
            return undo_operation
        has_upper = any(c.isupper() for c in value)
        has_lower = any(c.islower() for c in value)
        has_digit = any(c.isdigit() for c in value)
        has_special = any(not c.isalnum() for c in value)
        if has_upper and has_lower and has_digit and has_special:
            return value
        return undo_operation
    
    def build(self):
        # Create a ScreenManager instance
        self.sm = ScreenManager()

        # Add each screen to the ScreenManager
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(SignUpScreen(name='signup'))
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(CreateHaikuScreen(name='create_haiku'))
        self.sm.add_widget(ProfileScreen(name='profile'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(ExploreScreen(name='explore'))
        self.sm.add_widget(NotificationsScreen(name='notifications'))

        

        return self.sm  # Return the ScreenManager as the root widget
    
    def change_screen(self, screen_name):
        # Change the current screen of the ScreenManager
        self.sm.current = screen_name

    def login(self, *args):
        pass  # Implement login logic

    def show_signup(self, *args):
        self.change_screen('signup')  # Navigate to Sign Up screen

    def show_forgot_password(self, *args):
        pass  # Navigate to Forgot Password screen

    def sign_up(self, *args):
        # Get the user input
        username = self.sm.get_screen('signup').ids.username_input.text
        email = self.sm.get_screen('signup').ids.email_input.text
        password = self.sm.get_screen('signup').ids.password_input.text

        # TODO: You might want to call validate_email here if you haven't validated the email earlier
        if not self.validate_email(email):
            print("Invalid email")
            return
        
        # Call the filter functions to validate the input
        if self.username_filter(username, None) is None:
            print("Invalid username")
            return
        if self.password_filter(password, None) is None:
            print("Invalid password")
            return

        # TODO: Implement sign-up logic here.
        # For now, we'll just print the input values.
        print(f'Username: {username}, Email: {email}, Password: {password}')

        # After sign-up, you might want to navigate to the Home screen
        self.change_screen('home')


    
if __name__ == "__main__":
    MainApp().run()
