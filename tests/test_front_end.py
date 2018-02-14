# tests/test_front_end.py

import unittest
import urllib2
import time

from flask import url_for
from flask_testing import LiveServerTestCase
from selenium import webdriver

from app import create_app, db
from app.models import Employee, Role, Department

# Set test variables for test admin user
test_admin_username = "admin"
test_admin_email = "admin@email.com"
test_admin_password = "admin2016"

# Set variables for test employee 1
test_employee1_first_name = "Test"
test_employee1_last_name = "Employee"
test_employee1_username = "employee1"
test_employee1_email = "employee1@email.com"
test_employee1_password = "1test2016"

# Set test variables for test employee 2
test_employee2_first_name = "Test"
test_employee2_last_name = "Employee"
test_employee2_username = "employee2"
test_employee2_email = "employee2@email.com"
test_employee2_password = "2test2016"

# Set variables for test department 1
test_department1_name = "Human Resources"
test_department1_description = "Find and keep the best talent"

# Set variables for test department 2
test_department2_name = "Information Technology"
test_department2_description = "Manage all tech systems and processes"

# Set variables for test role 1
test_role1_name = "Head of Department"
test_role1_description = "Lead the entire department"

# Set variables for test role 2
test_role2_name = "Intern"
test_role2_description = "3-Month learning position"

class TestBase(LiveServerTestCase):
    def create_app(self):
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            # Specify the test database
            SQLALCHEMY_DATABASE_URI="mysql://dt_admin:dt2016@localhost/dreamteam_test",
            # Change the port that the liveserver listens to 
            LIVESERVER_PORT=8943
            )
        return app
        
    def setUp(self):
        """Set up the test driver and create test users"""
        self.driver = webdriver.Chrome()
        self.driver.get(self.get_server_url())
        
        db.session.commit()
        db.drop_all()
        db.create_all()
        
        # Create test admin user
        self.admin = Employee(username=test_admin_username,
                                email=test_admin_email,
                                password=test_admin_password,
                                is_admin=True)
        
        # Create test employee user
        self.employee = Employee(username=test_employee1_username,
                                first_name=test_employee1_first_name,
                                last_name=test_employee1_last_name,
                                email=test_employee1_email,
                                password=test_employee1_password)
        
        # Create test department
        self.department = Department(name=test_department1_name,
                                    description=test_department1_description)
        
        # Create test role
        self.role = Role(name=test_role1_name,
                        description=test_role1_description)
                        
        # Save to database
        db.session.add(self.admin)
        db.session.add(self.employee)
        db.session.add(self.department)
        db.session.add(self.role)
        db.session.commit()
        
    def tearDown(self):
        self.driver.quit()
        
    def test_server_is_up_and_running(self):
        response = urllib2.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

class TestRegistration(TestBase):

    def test_registration(self):
        """
        Test that a user can create an account using the registration form
        if all fields are field correctly, and that they will be 
        redirected to the login page
        """

        # Click register menu link
        self.driver.find_element_by_id("register_link").click()
        time.sleep(1)

        # Fill in registration form
        self.driver.find_element_by_id("email").send_keys(test_employee2_email)
        self.driver.find_element_by_id("username").send_keys(
            test_employee2_username)
        self.driver.find_element_by_id("first_name").send_keys(
            test_employee2_first_name)
        self.driver.find_element_by_id("last_name").send_keys(
            test_employee2_last_name)
        self.driver.find_element_by_id("password").send_keys(
            test_employee2_password)
        self.driver.find_element_by_id("confirm_password").send_keys(
            test_employee2_password)
        self.driver.find_element_by_id("submit").click()
        time.sleep(1)

        # Assert that browser redirects to login page
        assert url_for('auth.login') in self.driver.current_url

        # Assert success message is shown
        success_message = self.driver.find_element_by_class_name("alert").text 
        assert "You have successfully registered" in success_message

        # Assert that there are now 3 employees in the database
        self.assertEqual(Employee.query.count(), 3)

    def test_registration_invalid_email(self):
        """
        Test that a user cannot register using an invalid email format
        and that an appropriate error message will be displayed
        """

        # Click register menu link
        self.driver.find_element_by_id("register_link").click()
        time.sleep(1)

        # Fill in registration form
        self.driver.find_element_by_id("email").send_keys("invalid_email")
        self.driver.find_element_by_id("username").send_keys(
            test_employee2_username)
        self.driver.find_element_by_id("first_name").send_keys(
            test_employee2_first_name)
        self.driver.find_element_by_id("last_name").send_keys(
            test_employee2_last_name)
        self.driver.find_element_by_id("password").send_keys(
            test_employee2_password)
        self.driver.find_element_by_id("confirm_password").send_keys(
            test_employee2_password)
        self.driver.find_element_by_id("submit").click()
        time.sleep(5)

        # Assert error message is shown
        error_message = self.driver.find_element_by_class_name(
            "help-block").text 
        assert "Invalid email address" in error_message

    def test_registration_confirm_password(self):
        """
        Test that an appropriate error message is displayed when the 
        password and confirm password fields do not match
        """

        # Click register menu link
        self.driver.find_element_by_id("register_link").click()
        time.sleep(1)

        # Fill in registration form
        self.driver.find_element_by_id("email").send_keys(test_employee2_email)
        self.driver.find_element_by_id("username").send_keys(
            test_employee2_username)
        self.driver.find_element_by_id("first_name").send_keys(
            test_employee2_first_name)
        self.driver.find_element_by_id("last_name").send_keys(
            test_employee2_last_name)
        self.driver.find_element_by_id("password").send_keys(
            test_employee2_password)
        self.driver.find_element_by_id("confirm_password").send_keys(
            "password-won't-match")
        self.driver.find_element_by_id("submit").click()
        time.sleep(5)

        # Assert error message is shown
        error_message = self.driver.find_element_by_class_name(
            "help-block").text 
        assert "Field must be equal to confirm_password" in error_message

class TestLogin(TestBase):

    def test_login(self):
        """
        Test that a user can login and that they will be redirected to
        the homepage
        """

        # Click login menu link
        self.driver.find_element_by_id("login_link").click()
        time.sleep(1)

        # Fill in login form 
        self.driver.find_element_by_id("email").send_keys(test_employee1_email)
        self.driver.find_element_by_id("password").send_keys(
            test_employee1_password)
        self.driver.find_element_by_id("submit").click()
        time.sleep(2)

        # Assert that browser redirects to dashboard page
        assert url_for('home.dashboard') in self.driver.current_url

        # Assert that welcome greeting is shown
        username_greeting = self.driver.find_element_by_id(
            "username_greeting").text
        assert "Hi, employee1!" in username_greeting

    def test_admin_login(self):
        """
        Test that an admin user can login and that they will be redirected to
        the admin homepage 
        """

        # Click login menu link
        self.driver.find_element_by_id("login_link").click()
        time.sleep(1)

        # Fill in login form
        self.driver.find_element_by_id("email").send_keys(test_admin_email)
        self.driver.find_element_by_id("password").send_keys(
            test_admin_password)
        self.driver.find_element_by_id("submit").click()
        time.sleep(2)

        # Assert that browser redirects to dashboard page
        assert url_for('home.admin_dashboard') in self.driver.current_url

        # Assert that welcome greeting is shown
        username_greeting = self.driver.find_element_by_id(
            "username_greeting").text
        assert "Hi, admin!" in username_greeting

    def test_login_invalid_email_format(self):
        """
        Test that a user cannot login using an invalid email format
        and that an appropriate error message will be dispalyed
        """

        # Click login menu link
        self.driver.find_element_by_id("login_link").click()
        time.sleep(1)

        # Fill in login form
        self.driver.find_element_by_id("email").send_keys("invalid")
        self.driver.find_element_by_id("password").send_keys(
            test_employee1_password)
        self.driver.find_element_by_id("submit").click()
        time.sleep(2)

        # Assert error message is shown
        error_message = self.driver.find_element_by_class_name(
            "help-block").text
        assert "Invalid email address" in error_message

    def test_login_wrong_email(self):
        """
        Test that a user cannot login using wrong email 
        and that an appropriate error message will be displayed
        """

        # Click login menu link
        self.driver.find_element_by_id("login_link").click()
        time.sleep(1)

        # Fill in login form
        self.driver.find_element_by_id("email").send_keys(test_employee2_email)
        self.driver.find_element_by_id("password").send_keys(
            test_employee1_password)
        self.driver.find_element_by_id("submit").click()
        time.sleep(2)

        # Assert that error message is shown
        error_message = self.driver.find_element_by_class_name("alert").text
        assert "Invalid email or password" in error_message

    def test_login_wrong_password(self):
        """
        Test that a user cannot login using the wrong password
        and that an appropriate error message will be displayed
        """

        # Click login menu link
        self.driver.find_element_by_id("login_link").click()
        time.sleep(1)

        # Fill in login form
        self.driver.find_element_by_id("email").send_keys(test_employee1_email)
        self.driver.find_element_by_id("password").send_keys("invalid")
        self.driver.find_element_by_id("submit").click()
        time.sleep(2)

        # Assert that error message is shown
        error_message = self.driver.find_element_by_class_name("alert").text
        assert "Invalid email or password" in error_message

if __name__ == '__main__':
    unittest.main()