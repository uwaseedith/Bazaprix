from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

# Define currency choices
CURRENCY_CHOICES = (
    ('USD', 'US Dollars'),
    ('RWF', 'Rwandan Francs'),
    ('BIF', 'Burundian Francs'),
    
)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)

    def __str__(self):
        return self.business_name

class Product(models.Model):
    name = models.CharField(max_length=255)
    vendor = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL,
                               help_text="Vendor offering this product (optional)")
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BIF')
    market = models.CharField(max_length=255, blank=True, null=True) 
    door_number = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_preferred_price(self):
        """
        Calculate the average price of all products with the same name (case-insensitive).
        This value is suggested as the price a consumer might expect to pay.
        """
        similar_products = Product.objects.filter(name__iexact=self.name)
        # If at least one exists, calculate the average.
        if similar_products.exists():
            avg_price = similar_products.aggregate(avg=Avg('price'))['avg']
            return avg_price
        # Fallback: return this product's price
        return self.price

class PriceUpdate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_updates')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    # For crowdsourced submissions, this can be null if submitted by a vendor
    submitted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.product.name} - {self.price} at {self.timestamp}"
    

class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Added default
    change_amount = models.DecimalField(max_digits=10, decimal_places=2)
    change_type = models.CharField(max_length=20, default='increased')  # Added default, e.g., 'increased'
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False) 

    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"Transaction {self.id} - {self.user.username}"

    
class Feedback(models.Model):
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name='feedbacks')
    author = models.CharField(max_length=255)  # You can store the consumer's name or username
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()  # e.g., 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.author} - {self.rating}/5"
    
class SavedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_products')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    saved_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    saved_preferred_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} saved {self.product.name}"
    
class Notification(models.Model):
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification for {self.vendor.business_name} at {self.created_at}"