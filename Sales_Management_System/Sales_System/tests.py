from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from .models import Category, Product, Enquiry, Enquirer

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            user=self.user,
            product_name='Test Product',
            price=10.99,
            description='Test description',
            category=self.category
        )
        self.enquirer = Enquirer.objects.create(
            user=self.user,
            address='Test Address',
            mobile_number='1234567890'
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Test Product')

    def test_enquirer_str(self):
        self.assertEqual(str(self.enquirer), 'testuser')

class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            user=self.user,
            product_name='Test Product',
            price=10.99,
            description='Test description',
            category=self.category
        )
        self.enquirer = Enquirer.objects.create(
            user=self.user,
            address='Test Address',
            mobile_number='1234567890'
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Sales_System/index.html')

    def test_enquiry_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('enquiry_form', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Sales_System/enquiry_form.html')

    def test_signup_view(self):
        data = {
            'username': 'newtestuser',
            'email': 'newtestuser@example.com',
            'password1': 'newpassword',
            'password2': 'newpassword',
            'first_name': 'New',
            'last_name': 'User',
            'address': 'New Address',
            'mobile_number': '9876543210',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup

    def test_enquiry_view_post_with_enquirer(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'contact_person_name': 'Test User',
            'address': 'Test Address',
            'quantity': 2,
            'mobile_number': '1234567890',
            'amount': self.product.price,
        }
        response = self.client.post(reverse('enquiry_form', args=[self.product.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful enquiry
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Enquiry submitted successfully.')

    def test_enquiry_view_post_without_enquirer(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'contact_person_name': 'Test User',
            'address': 'Test Address',
            'quantity': 2,
            'mobile_number': '1234567890',
            'amount': self.product.price,
        }
        Enquirer.objects.filter(user=self.user).delete()  # Delete the associated Enquirer instance
        response = self.client.post(reverse('enquiry_form', args=[self.product.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect to create enquirer profile
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Please create an enquirer profile first.')