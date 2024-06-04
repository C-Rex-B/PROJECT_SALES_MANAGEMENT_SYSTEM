from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, ListView, UpdateView,  DeleteView
from django.views import View
from django import forms
from .forms import UserRegisterForm, EnquiryForm, EnquiryStatusForm, CategoryForm, ProductForm, EnquirerForm
from .models import Product, Category, Enquiry, Enquirer, EnquiryStatus, ProductImage
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.paginator import Paginator
from .utils import admin_required
from .mixins import AdminRequiredMixin
import tempfile
import datetime
from django.conf import settings
import os
from django.utils import timezone
import logging
from django.db.models import Q

@login_required
def search_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        products = Product.objects.filter(product_name__icontains=query)
        categories = Category.objects.filter(name__icontains=query)
        
        suggestions.extend([{'name': product.product_name} for product in products])
        suggestions.extend([{'name': category.name} for category in categories])

    return JsonResponse({'suggestions': suggestions})

@login_required
def product_list(request):
    search_query = request.GET.get('search', '')
    products = Product.objects.all().order_by('created_at')  # Ensure the products are ordered

    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # categories = Category.objects.all()
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Sales_System/index.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

@login_required
@admin_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'Sales_System/edit_category.html', {'form': form, 'category': category})

@login_required
@admin_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('manage_categories')
    return render(request, 'Sales_System/delete_category.html', {'category': category})


class Index(TemplateView):
    template_name = 'Sales_System/index.html'

    def get(self, request):
        products = Product.objects.all()  # Get all products
        categories = Category.objects.all()  # Get all categories
        return render(request, self.template_name, {'products': products, 'categories': categories})

class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        items = Product.objects.all()
        return render(request, 'Sales_System/dashboard.html', {'items': items})

class SignUpView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'Sales_System/signup.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        return render(request, 'Sales_System/signup.html', {'form': form})
    

class CustomLogoutView(LogoutView):
    template_name = 'Sales_System/logout.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            # Handle GET request if needed
            # You can add custom logic or just return the template
            return render(request, self.template_name)
        return super().dispatch(request, *args, **kwargs)

class ChangePasswordView(PasswordChangeView):
    template_name = 'Sales_System/change_password.html'
    success_url = reverse_lazy('index')


class EnquiryView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        enquirer = getattr(request.user, 'enquirer', None)

        if enquirer:
            form = EnquiryForm(initial={
                'product': product,
                'product_category': product.category,
                'amount': product.price,
                'contact_person_name': enquirer.user.get_full_name(),
                'address': enquirer.address,
                'mobile_number': enquirer.mobile_number,
            })
        else:
            messages.warning(request, 'Please create an enquirer profile first.')
            return redirect('create_enquirer_profile')

        return render(request, 'Sales_System/enquiry_form.html', {'product': product, 'form': form})

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        form = EnquiryForm(request.POST)

        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.product = product
            enquiry.product_category = product.category
            enquiry.amount = product.price
            enquirer = getattr(request.user, 'enquirer', None)

            if enquirer:
                enquiry.enquirer = enquirer
                enquiry.save()
                messages.success(request, 'Enquiry submitted successfully.')
                return redirect('index')
            else:
                messages.warning(request, 'Please create an enquirer profile first.')
                return redirect('create_enquirer_profile')
        else:
            messages.error(request, 'Please correct the errors in the form.')

        return render(request, 'Sales_System/enquiry_form.html', {'product': product, 'form': form})

# class CreateEnquirerProfileView(LoginRequiredMixin, View):
#     def get(self, request):
#        # Instantiate the EnquirerForm
#         form = EnquirerForm()
#         # Render the template with the form
#         return render(request, 'Sales_System/create_enquirer_profile.html', {'form': form})
    
#     def post(self, request):
#         form = EnquirerForm(request.POST)
#         if form.is_valid():
#             enquirer = form.save(commit=False)
#             enquirer.user = request.user
#             enquirer.save()
#             return redirect('index')  # Redirect to index after successful profile creation
#         return render(request, 'Sales_System/create_enquirer_profile.html', {'form': form})

class CreateEnquirerProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = EnquirerForm(instance=getattr(request.user, 'enquirer', None))
        return render(request, 'Sales_System/create_enquirer_profile.html', {'form': form})

    def post(self, request):
        enquirer = getattr(request.user, 'enquirer', None)
        form = EnquirerForm(request.POST, instance=enquirer)
        if form.is_valid():
            enquirer = form.save(commit=False)
            enquirer.user = request.user
            enquirer.save()
            messages.success(request, 'Enquirer profile created/updated successfully.')
            return redirect('index')
        return render(request, 'Sales_System/create_enquirer_profile.html', {'form': form})



# class ProductUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
#     model = Product
#     form_class = ProductForm
#     template_name = 'Sales_System/edit_product.html'
#     success_url = reverse_lazy('manage_products')

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         # Handle images
#         for image in self.request.FILES.getlist('images'):
#             ProductImage.objects.create(product=self.object, image=image)
#         messages.success(self.request, 'Product updated successfully.')
#         return response

class ProductUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'Sales_System/edit_product.html'
    success_url = reverse_lazy('manage_products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.object)
        print(self.object.images.all())

        context['images'] = self.object.images.all()  # Use the related name 'images'
        return context

# class ProductDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
#     model = Product
#     template_name = 'Sales_System/delete_product.html'
#     success_url = reverse_lazy('manage_products')

#     def delete(self, request, *args, **kwargs):
#         messages.success(self.request, 'Product deleted successfully.')
#         return super().delete(request, *args, **kwargs)


class ProductDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'Sales_System/delete_product.html'
    success_url = reverse_lazy('manage_products')


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    enquirer = forms.ModelChoiceField(queryset=Enquirer.objects.all(), required=False, empty_label="All Users")

class EnquirerReportView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Enquiry
    template_name = 'Sales_System/enquirer_report.html'
    context_object_name = 'enquiries'

    def get_queryset(self):
        # Get date range and enquirer from GET parameters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        enquirer_id = self.request.GET.get('enquirer')

        queryset = Enquiry.objects.all()

        if enquirer_id:
            queryset = queryset.filter(enquirer_id=enquirer_id)

        if start_date and end_date:
            queryset = queryset.filter(enquiry_date__date__range=[start_date, end_date])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_range_form'] = DateRangeForm(self.request.GET)
        return context



    # def get_queryset(self):
    #     # Try to get the Enquirer object for the logged-in user
    #     try:
    #         enquirer = Enquirer.objects.get(user=self.request.user)
    #     except Enquirer.DoesNotExist:
    #         # Handle the case where Enquirer doesn't exist by creating a new one
    #         enquirer = Enquirer.objects.create(user=self.request.user)

    #     # Get date range from GET parameters
    #     start_date = self.request.GET.get('start_date')
    #     end_date = self.request.GET.get('end_date')

    #     # Filter enquiries based on the enquirer and the selected date range
    #     if start_date and end_date:
    #         return Enquiry.objects.filter(enquirer=enquirer, enquiry_date__date__range=[start_date, end_date])
    #     else:
    #         return Enquiry.objects.filter(enquirer=enquirer)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['date_range_form'] = DateRangeForm(self.request.GET)
    #     return context
# class EnquirerReportView(LoginRequiredMixin, AdminRequiredMixin, View):
#     def get(self, request):
#         return render(request, 'Sales_System/enquirer_report.html')


# logger = logging.getLogger(__name__)

# class GenerateEnquiryReport(LoginRequiredMixin, AdminRequiredMixin, View):
#     def get(self, request):
#         logger.debug("GenerateEnquiryReport view accessed")
#         try:
#             # Fetch all enquiries
#             enquiries = Enquiry.objects.all()
#             # Render the template with enquiries
#             html_string = render_to_string('Sales_System/enquiry_report_pdf.html', {'enquiries': enquiries})
#             # Generate the PDF
#             html = HTML(string=html_string)
#             result = html.write_pdf()

#             # Create a response object with PDF
#             response = HttpResponse(result, content_type='application/pdf')
#             response['Content-Disposition'] = 'attachment; filename=enquiry_report.pdf'
#             logger.debug("PDF generated successfully")
#             return response
#         except Exception as e:
#             logger.error(f"Error generating PDF: {e}")
#             return HttpResponse("Error generating PDF", status=500)

class GenerateEnquiryReport(LoginRequiredMixin, AdminRequiredMixin, View):

    def get(self, request):
        enquiries = Enquiry.objects.all().order_by('-enquiry_date')
        context = {
            'enquiries': enquiries,
        }
        return render(request, 'Sales_System/enquiry_report_pdf.html', context)

    def post(self, request):
        enquiries = Enquiry.objects.all().order_by('-enquiry_date')

        context = {
            'enquiries': enquiries,
        }

        html_string = render_to_string('Sales_System/enquiry_report_pdf.html', context)

        # Create a temporary file path
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file_path = temp_file.name

        # Write the PDF content to the temporary file
        HTML(string=html_string).write_pdf(temp_file_path)

        # Read the PDF content from the temporary file
        with open(temp_file_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()

        # Close and delete the temporary file
        temp_file.close()
        os.unlink(temp_file_path)

        # Create the HTTP response with the PDF content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="enquiry_report.pdf"'

        return response



        # with tempfile.NamedTemporaryFile(suffix='.pdf') as temp_file:
        #     HTML(string=html_string).write_pdf(temp_file.name)
        #     temp_file.seek(0)
        #     response.write(temp_file.read())

        # return response



class ManageProductCategories(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()
        form = CategoryForm()
        return render(request, 'Sales_System/manage_categories.html', {'categories': categories})

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('manage_categories')
        categories = Category.objects.all()
        return render(request, 'Sales_System/manage_categories.html', {'categories': categories, 'form': form})

class ManageProducts(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
        products = Product.objects.filter(user=request.user).order_by('-created_at')  # Order by creation date
        paginator = Paginator(products, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        form = ProductForm()
        return render(request, 'Sales_System/manage_products.html', {'page_obj': page_obj, 'form': form})

    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user  # Associate the product with the logged-in user
            product.save()
            for file in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=file)
            messages.success(request, 'Product added successfully.')
            return redirect('manage_products')
        products = Product.objects.filter(user=request.user).order_by('-created_at')
        paginator = Paginator(products, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'Sales_System/manage_products.html', {'page_obj': page_obj, 'form': form})




    
class ProductListView(View):
    def get(self, request, category_id=None):
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            products = Product.objects.filter(category=category)
        else:
            products = Product.objects.all()
        return render(request, 'Sales_System/product_list.html', {'products': products})


    
class ProductListByCategory(View):
    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
        return render(request, 'Sales_System/product_list_by_category.html', {'products': products, 'category': category})

class FilterEnquiriesByDate(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request):
        # Retrieve query parameters for date filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Perform filtering based on provided dates
        if start_date and end_date:
            try:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                enquiries = Enquiry.objects.filter(
                    Q(enquiry_date__date__gte=start_date) & Q(enquiry_date__date__lte=end_date)
                )
            except ValueError:
                messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
                return redirect('index')
        else:
            enquiries = Enquiry.objects.all()

        return render(request, 'Sales_System/filter_enquiries.html', {'enquiries': enquiries})
            # Assuming date format is DD/MM/YYYY
            # Convert the provided date strings to the format expected by the database query
        #     start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        #     end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        #     enquiries = Enquiry.objects.filter(enquiry_date__range=(start_date, end_date))
        # else:
        #     enquiries = Enquiry.objects.all()

        # Render a template with filtered enquiries or return a JSON response
        # return render(request, 'filter_enquiries.html', {'enquiries': enquiries})



class UpdateEnquiryStatus(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, id=enquiry_id)
        form = EnquiryStatusForm(instance=enquiry.status)
        return render(request, 'Sales_System/update_enquiry_status.html', {'form': form, 'enquiry': enquiry})

    def post(self, request, enquiry_id):
        enquiry = get_object_or_404(Enquiry, id=enquiry_id)
        form = EnquiryStatusForm(request.POST, instance=enquiry.status)

        if form.is_valid():
            # Save the form to update the status of the enquiry
            enquiry_status = form.save(commit=False)
            enquiry_status.enquiry = enquiry
            enquiry_status.save()
            messages.success(request, 'Enquiry status updated successfully.')
            return redirect('index')  # Redirect to index after successfully updating enquiry status
        
        return render(request, 'Sales_System/update_enquiry_status.html', {'form': form, 'enquiry': enquiry})

