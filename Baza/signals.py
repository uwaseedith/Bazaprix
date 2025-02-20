from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, SavedProduct, PriceAlert, Notification, Feedback

@receiver(post_save, sender=Product)
def preferred_price_change_alert(sender, instance, **kwargs):
    new_preferred_price = instance.get_preferred_price()
    

    saved_products = SavedProduct.objects.filter(product__name__iexact=instance.name)
    
    for saved in saved_products:
        previous_preferred_price = saved.saved_preferred_price
        if previous_preferred_price != new_preferred_price:
            change_amount = new_preferred_price - previous_preferred_price
            change_type = "increased" if change_amount > 0 else "diminished"
            
            PriceAlert.objects.create(
                user=saved.user,
                product=saved.product,
                previous_price=previous_preferred_price,
                new_price=new_preferred_price,
                change_amount=abs(change_amount),
                change_type=change_type,
            )
            saved.saved_preferred_price = new_preferred_price
            saved.save()


@receiver(post_save, sender=Feedback)
def create_vendor_notification(sender, instance, created, **kwargs):
    if created:
        vendor = instance.vendor
        message = f"{instance.author} rated you {instance.rating} stars: {instance.comment}"
        Notification.objects.create(vendor=vendor, message=message)