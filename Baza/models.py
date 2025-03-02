from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models import Avg
from .utils import translate_text

USER_TYPE_CHOICES = [
    ('consumer', 'Consumer'),
    ('vendor', 'Vendor'),
]

CURRENCY_CHOICES = (
    ('USD', 'US Dollars'),
    ('RWF', 'Rwandan Francs'),
    ('BIF', 'Burundian Francs'),
    
)

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('es', 'Spanish'),
    ('sw', 'Swahili'),
    ('rw', 'Kinyarwanda'),
    ('rn', 'Rundi')
]  

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('electronics', 'Electronics'),
        ('apparel_fashion', 'Apparel & Fashion'),
        ('health_beauty', 'Health & Beauty'),
        ('home_garden', 'Home & Garden'),
        ('sports_outdoors', 'Sports & Outdoors'),
        ('automotive', 'Automotive'),
        ('toys_games', 'Toys & Games'),
        ('books_music_media', 'Books, Music & Media'),
        ('office_supplies', 'Office Supplies'),
        ('tools_hardware', 'Tools & Hardware'),
        ('pet_supplies', 'Pet Supplies'),
        ('baby_kids_products', 'Baby & Kids’ Products'),
        ('jewelry_accessories', 'Jewelry & Accessories'),
        ('arts_crafts_hobbies', 'Arts, Crafts & Hobbies'),
        ('industrial_scientific', 'Industrial & Scientific'),
    ]
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField()

    def __str__(self):
        return self.get_name_display()

class Consumer(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='consumer')
    language_preference = models.CharField(max_length=10, default='en')
    
class User(AbstractUser):
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='consumer'
    )
    language_preference = models.CharField(
        max_length=2,
        choices=[('en', 'English'), ('fr', 'French'), ('es', 'Spanish'), ('sw', 'Swahili')],
        default='en'
    )

    def __str__(self):
        return self.username
    


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    language_preference = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="en")
    def translate_business_name(self, target_lang):
        """Translates the business name dynamically."""
        return translate_text(self.business_name, target_lang)


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

    def translate_name(self, target_lang):
        """Translates the product name dynamically."""
        return translate_text(self.name, target_lang)

    def translate_description(self, target_lang):
        """Translates the product description dynamically."""
        return translate_text(self.description, target_lang)

    def __str__(self):
        return self.name
    
    def get_preferred_price(self):
        """
        Calculate the average price of all products with the same name (case-insensitive).
        This value is suggested as the price a consumer might expect to pay.
        """
        similar_products = Product.objects.filter(name__iexact=self.name)
        if similar_products.exists():
            avg_price = similar_products.aggregate(avg=Avg('price'))['avg']
            return avg_price
        return self.price

class PriceUpdate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_updates')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.product.name} - {self.price} at {self.timestamp}"
    

class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  
    change_amount = models.DecimalField(max_digits=10, decimal_places=2)
    change_type = models.CharField(max_length=20, default='increased')  
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
    author = models.CharField(max_length=255)  
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()  
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
    