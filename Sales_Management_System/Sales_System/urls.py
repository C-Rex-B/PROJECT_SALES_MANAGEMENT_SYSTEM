# from django.urls import path
# from .views import (
#     ProductListView, EnquiryView, ProductUpdateView, ProductDeleteView, Index, SignUpView, CustomLogoutView, Dashboard,
#     FilterEnquiriesByDate, EnquirerReportView, ManageProductCategories,
#     ManageProducts, ChangePasswordView, CreateEnquirerProfileView, GenerateEnquiryReport, edit_category, delete_category, search_suggestions, product_list
# )
# from django.contrib.auth import views as auth_views

# urlpatterns = [
#     path('', Index.as_view(), name='index'),
#     path('products', product_list, name='product_list'),
#     path('dashboard/', Dashboard.as_view(), name='dashboard'),
#     path('signup/', SignUpView.as_view(), name='signup'),
#     path('login/', auth_views.LoginView.as_view(template_name='Sales_System/login.html'), name='login'),
#     path('logout/', CustomLogoutView.as_view(), name='logout'),
#     path('filter-enquiries/', FilterEnquiriesByDate.as_view(), name='filter_enquiries'),
#     path('enquirer-report/', EnquirerReportView.as_view(), name='enquirer_report'),
#     path('manage-categories/', ManageProductCategories.as_view(), name='manage_categories'),
#     path('manage-products/', ManageProducts.as_view(), name='manage_products'),
#     path('change-password/', ChangePasswordView.as_view(), name='change_password'),
#     path('enquiry/<int:product_id>/', EnquiryView.as_view(), name='enquiry_form'),
#     path('enquiry/<int:product_id>/', EnquiryView.as_view(), name='enquiry'),
#     path('create_enquirer_profile/', CreateEnquirerProfileView.as_view(), name='create_enquirer_profile'),
#     path('products/', ProductListView.as_view(), name='product_list'),
#     path('category/<int:category_id>/', ProductListView.as_view(), name='product_list_by_category'),
#     path('edit-product/<int:pk>/', ProductUpdateView.as_view(), name='edit_product'),
#     path('edit-category/<int:pk>/', edit_category, name='edit_category'),
#     path('delete-product/<int:pk>/', ProductDeleteView.as_view(), name='delete_product'),
#     path('delete-category/<int:pk>/', delete_category, name='delete_category'),
#     path('admin/enquiry-report-pdf/', GenerateEnquiryReport.as_view(), name='generate_enquiry_report_pdf'),
#     path('search_suggestions/', search_suggestions, name='search_suggestions'),
# ]







from django.urls import path
from .views import (
    ProductListView, EnquiryView, ProductUpdateView, ProductDeleteView, Index, SignUpView, CustomLogoutView, Dashboard,
    FilterEnquiriesByDate, EnquirerReportView, ManageProductCategories,
    ManageProducts, ChangePasswordView, CreateEnquirerProfileView, GenerateEnquiryReport, edit_category, delete_category, search_suggestions, product_list
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', product_list, name='index'),
    path('products/', product_list, name='product_list'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='Sales_System/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('filter-enquiries/', FilterEnquiriesByDate.as_view(), name='filter_enquiries'),
    path('enquirer-report/', EnquirerReportView.as_view(), name='enquirer_report'),
    path('manage-categories/', ManageProductCategories.as_view(), name='manage_categories'),
    path('manage-products/', ManageProducts.as_view(), name='manage_products'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('enquiry/<int:product_id>/', EnquiryView.as_view(), name='enquiry_form'),
    path('create_enquirer_profile/', CreateEnquirerProfileView.as_view(), name='create_enquirer_profile'),
    path('edit-product/<int:pk>/', ProductUpdateView.as_view(), name='edit_product'),
    path('edit-category/<int:pk>/', edit_category, name='edit_category'),
    path('delete-product/<int:pk>/', ProductDeleteView.as_view(), name='delete_product'),
    path('delete-category/<int:pk>/', delete_category, name='delete_category'),
    path('search_suggestions/', search_suggestions, name='search_suggestions'),
    path('category/<int:category_id>/', ProductListView.as_view(), name='product_list_by_category'),
    path('enquiry-report-pdf/', GenerateEnquiryReport.as_view(), name='generate_enquiry_report_pdf'),
    path('admin/enquiry-report-pdf/', GenerateEnquiryReport.as_view(), name='admin_enquiry_report_pdf'),
]


