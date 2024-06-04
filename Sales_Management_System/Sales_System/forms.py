from django import forms
from multiupload.fields import MultiFileField
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import EnquiryStatus, Enquiry, Category, Product, ProductImage, Enquirer

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    address = forms.CharField(max_length=100, required=False)
    mobile_number = forms.CharField(max_length=15, required=False, validators=[RegexValidator(r'^\d+$', 'Mobile number should contain only digits.')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'address', 'mobile_number']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ProductForm(forms.ModelForm):
    images = MultiFileField(min_num=1, max_num=10, max_file_size=1024**2 * 5, required=False)

    class Meta:
        model = Product
        fields = ['product_name', 'price', 'description', 'category', 'images']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            for image in self.cleaned_data.get('images', []):
                ProductImage.objects.create(product=instance, image=image)
        return instance

class EnquiryStatusForm(forms.ModelForm):
    class Meta:
        model = EnquiryStatus
        fields = ['status', 'remark']
        widgets = {
            'status': forms.Select(choices=EnquiryStatus.STATUS_CHOICES),
            'remark': forms.Textarea(attrs={'rows': 3})
        }

class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['contact_person_name', 'address', 'quantity', 'mobile_number', 'amount']
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive number.")
        return quantity

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        if not mobile_number.isdigit():
            raise forms.ValidationError("Mobile number should contain only digits.")
        return mobile_number

class EnquirerForm(forms.ModelForm):
    mobile_number = forms.CharField(validators=[RegexValidator(r'^\d+$', 'Mobile number should contain only digits.')])


    class Meta:
        model = Enquirer
        fields = ['address', 'mobile_number']
