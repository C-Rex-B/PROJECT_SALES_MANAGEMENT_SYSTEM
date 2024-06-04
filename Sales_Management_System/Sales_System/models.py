from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  # Use settings.AUTH_USER_MODEL
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.product_name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.product_name}"

class Enquirer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use settings.AUTH_USER_MODEL
    address = models.TextField()
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class Enquiry(models.Model):
    enquiry_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='enquiries')
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='enquiries')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contact_person_name = models.CharField(max_length=255)
    address = models.TextField()
    quantity = models.IntegerField()
    mobile_number = models.CharField(max_length=15)
    enquirer = models.ForeignKey(Enquirer, on_delete=models.CASCADE, related_name='enquiries')

    def __str__(self):
        return f"Enquiry for {self.product.product_name}"

class EnquiryStatus(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_COMPLETED = 'Completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    enquiry = models.OneToOneField(Enquiry, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_PENDING)
    remark = models.TextField()

    def __str__(self):
        return f"Status of enquiry for {self.enquiry.product.product_name}"

