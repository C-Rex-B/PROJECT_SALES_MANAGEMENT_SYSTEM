from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, ProductImage, Enquiry, Enquirer, EnquiryStatus

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_admin',)}),
    )

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('product_name', 'description')
    date_hierarchy = 'created_at'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Enquiry)
admin.site.register(Enquirer)
admin.site.register(EnquiryStatus)
