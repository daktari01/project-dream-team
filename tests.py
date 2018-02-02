# tests.py

import os
import unittest

from flask import abort, url_for
from flask_testing import TestCase

from app import create_app, db
from app.models import Employee, Department, Role

class TestBase(TestCase):

    def create_app(self):
        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='mysql://dt_admin:dt2016@localhost/dreamteam_test')
        return app

    def setUp(self):
        """
        Will be called before every test
        """
        db.create_all()

        # Create test admin user
        admin = Employee(username="admin", password="admin2016", is_admin=True)

        # Create test non-admin user
        employee = Employee(username="test_user", password="test2016") 

        # Save users to database
        db.session.add(admin)
        db.session.add(employee)
        db.session.commit()

    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()

class TestModels(TestBase):

    def test_employee_model(self):
        """
        Test number of records in Employee table
        """
        self.assertEqual(Employee.query.count(), 2)

    def test_department_model(self):
        """
        Test number of records in Department table
        """
        # Create test department
        department = Department(name="IT", description="The IT Department")

        # Save department to database
        db.session.add(department)
        db.commit()

        self.assertEqual(Department.query.count(), 1)

    def test_role_model(self):
        """
        Test the number of records in the Role table
        """
        # Create test role
        role = Role(name="CEO", description="Run the whole company")

        # Save role to database
        db.session.add(role)
        db.session.commit()

        self.assertEqual(Role.query.conut(), 1)

class TestViews(TestBase):

    def test_homepage_view(self):
        """
        Test that homepage is accessible without login
        """
        response = self.client.get(url_for('home.homepage'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        """
        Test that login page is accessible without login
        """
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """
        Test that logout link is inaccessible without login 
        and redirects to login page then to logout
        """
        target_url = url_for('auth.logout')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_dashboard_view(self):
        """
        Test that dashboard is inaccessible without login
        and redirects to login page the to dashboard
        """
        target_url = url_for('home.dashboard')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    

if __name__ == '__main__':
    unittest.main()