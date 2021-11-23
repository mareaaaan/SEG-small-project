"""Unit tests of sign up form."""
from django.test import TestCase
from clubs.models import User
from clubs.forms import SignUpForm
from django import forms
from django.contrib.auth.hashers import check_password

class SignUpFormTestCase(TestCase):
    """Unit tests of sign up form."""

    def setUp(self):
        self.form_input = {
            'first_name':'Jane',
            'last_name' : 'Doe',
            'username':'@janedoe',
            'email' : 'janedoe@example.com',
            'bio' : 'My bio',
            'new_password':'Password123',
            'password_confirmation': 'Password123',
            'chess_experience_level': '1',
        }

    #Form accepts valid input data
    def test_valid_sign_up_form(self):
        form_input = {
            'first_name':'Jane',
            'last_name' : 'Doe',
            'username':'@janedoe',
            'email' : 'janedoe@example.com',
            'bio' : 'My bio',
            'new_password':'Password123',
            'password_confirmation': 'Password123',
            'chess_experience_level': '1',

        }
        form = SignUpForm(data = form_input)
        self.assertTrue(form.is_valid())

    #Form has the necessary fields
    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('new_password', form.fields)
        self.assertIn('password_confirmation', form.fields)
        self.assertIn('chess_experience_level',form.fields)

    def test_form_must_save_correctly(self):
        form = SignUpForm(data = self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        user = User.objects.get(username = '@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.com')
        self.assertEqual(user.bio, 'My bio')
        self.assertEqual(user.chess_experience_level,'1')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
