from django.contrib import admin
from .models import Category, Consumer, User, Vendor, Product, PriceUpdate, PriceAlert, Transaction, Feedback, SavedProduct, Notification

# Register your models here.

# Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)

# Consumer Model
@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('user', 'language_preference')
    search_fields = ('user__username',)

# User Model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_type', 'language_preference')
    search_fields = ('username', 'user_type')
    list_filter = ('user_type',)

# Vendor Model
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'location', 'contact_info', 'language_preference')
    search_fields = ('business_name',)
    list_filter = ('language_preference',)

    def get_email(self, obj):
        return obj.user.email  # Assuming the Vendor model has a 'user' field that links to the User model
    get_email.short_description = 'Email'

# Product Model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'currency')
    search_fields = ('name', 'vendor__business_name', 'category__name')
    list_filter = ('category', 'currency')

# PriceUpdate Model
@admin.register(PriceUpdate)
class PriceUpdateAdmin(admin.ModelAdmin):
    list_display = ('product', 'vendor', 'price', 'timestamp', 'submitted_by')
    search_fields = ('product__name', 'vendor__business_name', 'submitted_by__username')
    list_filter = ('timestamp',)

# PriceAlert Model
@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'previous_price', 'new_price', 'change_amount', 'change_type', 'created_at', 'seen')
    search_fields = ('user__username', 'product__name')
    list_filter = ('change_type', 'seen', 'created_at')

# Transaction Model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'vendor', 'transaction_date', 'amount')
    search_fields = ('user__username', 'product__name', 'vendor__business_name')
    list_filter = ('transaction_date',)

# Feedback Model
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'author', 'rating', 'created_at')
    search_fields = ('vendor__business_name', 'author')
    list_filter = ('rating', 'created_at')

# SavedProduct Model
@admin.register(SavedProduct)
class SavedProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'saved_price', 'saved_preferred_price', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('created_at',)

# Notification Model
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'message', 'created_at', 'seen')
    search_fields = ('vendor__business_name', 'message')
    list_filter = ('seen', 'created_at')
