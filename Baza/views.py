from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Vendor, PriceAlert, PriceUpdate, SavedProduct, Transaction, Feedback, Notification, Consumer, AIProduct, PriceInformation, AISuggestedPrice
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProductForm, RateVendorForm, AIPriceInfoGenerationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from decimal import Decimal
import json
from django.contrib import messages
from django.db.models import Q
from .utils import translate_text
from django.utils import translation
from django.conf import settings
from django.utils.translation import activate
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from .forms import AIProductGenerationForm, AISuggestedPriceForm
from .ai_utils import generate_product_details, generate_product_image, generate_price_trends, format_insights, process_ai_insights, generate_suggested_price
from django.core.files.base import ContentFile
import re
from django.http import HttpResponseRedirect
from django.urls import reverse


@login_required
def vendor_profile(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('consumer_dashboard')
    vendor = request.user.vendor
    
    # Get language preference from the vendor object or default to 'en'
    language_preference = vendor.language_preference if hasattr(vendor, 'language_preference') else 'en'
    
    context = {
        'vendor': vendor,
        'language_preference': language_preference  # Pass language preference to the template
    }
    
    return render(request, 'Baza/vendor_profile.html', context)


@login_required
def consumer_profile(request):
    # Redirect to vendor profile if the user has a 'vendor' attribute
    if hasattr(request.user, 'vendor'):
        return redirect('vendor_profile')

    # Get the user's language preference from the Consumer model
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    # Pass the language preference to the template
    context = {
        'language_preference': language_preference
    }

    return render(request, 'Baza/consumer_profile.html', context)



@login_required
def product_detail(request, product_id):
    """
    View to show the details of a single product and its translation.
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Get the user's language preference
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'
    
    # Translate product description based on language preference
    translated_description = translate_text(product.description, language_preference)

    context = {
        'product': product,
        'language_preference': language_preference,  # Pass language preference to the template
        'translated_description': translated_description,  # Add the translated description
    }

    return render(request, 'Baza/product_detail.html', context)

@login_required
def cproduct_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get the user's language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    # Pass the product and language preference to the template context
    context = {
        'product': product,
        'language_preference': language_preference,  # Add language_preference to context
    }

    return render(request, 'Baza/cproduct_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query)
    # Get the user's language preference
    language_preference = request.user.language_preference

    context = {
        'query': query,
        'products': products,
        'language_preference': language_preference, 
    }
    return render(request, 'Baza/search_results.html', context)

def home(request):
    # For authenticated users, use language preference from the Vendor profile
    if request.user.is_authenticated and hasattr(request.user, 'vendor'):
        user_language = request.user.vendor.language_preference
    else:
        # For unauthenticated users, check if language is stored in session
        user_language = request.session.get('language_preference', 'en')  # Default to 'en' if not set

    # Activate the language immediately to ensure it's applied
    translation.activate(user_language)

    # Pass the language preference to the template context
    context = {
        'language_preference': user_language,
    }

    return render(request, 'Baza/home.html', context)



def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't commit yet so you can add fields manually
            user.email = form.cleaned_data.get('email')
            full_name = form.cleaned_data.get('full_name')
            names = full_name.split(' ', 1)
            user.first_name = names[0]
            if len(names) > 1:
                user.last_name = names[1]
            user.save()  # Save the user first so that the ID is generated

            # Determine the user type
            user_type = form.cleaned_data.get('user_type')

            if user_type == 'vendor':
                phone_number = form.cleaned_data.get('phone_number')
                market = form.cleaned_data.get('market')
                Vendor.objects.create(user=user, business_name=full_name, location=market, contact_info=phone_number)

                # Send notification emails to consumers
                consumers = Consumer.objects.all()
                subject = f"New Vendor Registered: {full_name}"
                message = f"Hello, a new vendor has registered: {full_name}.\n\nCheck out their profile on BazaPrix."

                for consumer in consumers:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [consumer.user.email], fail_silently=False)

                # Welcome email for vendors
                subject_user = "Welcome to BazaPrix as a Vendor!"
                message_user = f"Hello {full_name},\n\nThank you for registering as a vendor with BazaPrix. You can now manage your products and interact with consumers. Visit your profile at BazaPrix."

                dashboard_redirect = 'vendor_dashboard'  # Redirect vendor to vendor dashboard

            else:  # Consumer
                # Send notification emails to vendors
                vendors = Vendor.objects.all()
                subject = f"New Consumer Registered: {full_name}"
                message = f"Hello, a new consumer has signed up: {full_name}.\n\nCheck out their profile at BazaPrix."

                for vendor in vendors:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [vendor.user.email], fail_silently=False)

                # Welcome email for consumers
                subject_user = "Welcome to BazaPrix as a Consumer!"
                message_user = f"Hello {full_name},\n\nThank you for signing up as a consumer with BazaPrix. You can now explore products, vendors, and more. Visit your profile at BazaPrix to get started."

                dashboard_redirect = 'consumer_dashboard'  # Redirect consumer to consumer dashboard

            # Send the welcome email
            send_mail(subject_user, message_user, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

            # Set language preference
            user_language = user.vendor.language_preference if hasattr(user, 'vendor') else request.session.get('language_preference', 'en')
            activate(user_language)  # Activate the language immediately
            request.session['django_language'] = user_language 

            # Log in the user after signup
            login(request, user)
            messages.success(request, "Signup successful!")

            # Redirect user based on role
            return redirect(dashboard_redirect)  # Redirect to correct dashboard

    else:
        form = CustomUserCreationForm()

    return render(request, 'Baza/signup.html', {'form': form, 'language_preference': request.session.get('django_language', 'en')})

def send_welcome_email(user):
    subject = f"Welcome to BazaPrix, {user.first_name}!"
    message = f"Hello {user.first_name},\n\nThank you for signing up with BazaPrix! We are excited to have you on board. Feel free to explore our platform and start browsing products.\n\nBest regards,\nThe BazaPrix Team"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # Make sure this is configured in your settings
        [user.email],
        fail_silently=False,
    )

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'Baza/login.html'  # Path to the login template

    def get_success_url(self):
        """
        Redirects the user based on their type:
          - If the user has a vendor profile, redirect to vendor dashboard.
          - Otherwise, redirect to consumer dashboard.
        """
        user = self.request.user
        if hasattr(user, 'vendor'):
            return reverse_lazy('vendor_dashboard')
        else:
            return reverse_lazy('consumer_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user's language preference and pass it to the template
        language_preference = self.request.user.consumer.language_preference if hasattr(self.request.user, 'consumer') else 'en'
        context['language_preference'] = language_preference
        return context

        
        

def consumer_terms(request):
    # Set the language preference (use session or default)
    user_language = request.session.get('django_language', 'en')  # Default to 'en' if not set
    translation.activate(user_language)  # Activate the language

    context = {
        'language_preference': user_language
    }

    return render(request, 'Baza/consumer_terms.html', context)


def vendor_terms(request):
    # Set the language preference (use session or default)
    user_language = request.session.get('django_language', 'en')  # Default to 'en' if not set
    translation.activate(user_language)  # Activate the language

    context = {
        'language_preference': user_language
    }

    return render(request, 'Baza/vendor_terms.html', context)


@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('consumer_dashboard')
    
    vendor = request.user.vendor

    price_updates = PriceAlert.objects.filter(product__vendor=vendor, seen=False).order_by('-created_at')
    products = Product.objects.filter(vendor=vendor)
    notifications = Notification.objects.filter(vendor=vendor, seen=False).order_by('-created_at')

    # Access language_preference from the vendor object
    language_preference = vendor.language_preference if hasattr(vendor, 'language_preference') else 'en'

    context = {
        'vendor': vendor,
        'price_updates': price_updates,
        'products': products,
        'notifications': notifications,
        'language_preference': language_preference  # Pass the language_preference correctly
    }

    return render(request, 'Baza/vendor_dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SavedProduct, PriceAlert, Transaction, Product, PriceUpdate, Consumer
import json

@login_required
def consumer_dashboard(request):
    # Redirect vendor to their dashboard
    if hasattr(request.user, 'vendor'):
        return redirect('vendor_dashboard')
    
    # Retrieve saved products, price alerts, and transactions for the logged-in user
    saved_products = SavedProduct.objects.filter(user=request.user)
    price_alerts = request.user.price_alerts.filter(seen=False).order_by('-created_at')
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')

    # Send email if there are new price alerts
    if price_alerts.exists():
        subject = "New Price Alerts for Your Saved Products"
        message = "You have new price alerts for your saved products on BazaPrix. Check your dashboard for the latest updates."
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )

    # Handle selected product and price history
    selected_product_id = request.GET.get('product_id')
    selected_product = None
    labels = []
    data = []
    if selected_product_id:
        try:
            selected_product = Product.objects.get(id=selected_product_id)
            history = PriceUpdate.objects.filter(product=selected_product).order_by('timestamp')
            labels = [update.timestamp.strftime("%Y-%m-%d %H:%M") for update in history]
            data = [float(update.price) for update in history]
        except Product.DoesNotExist:
            selected_product = None

    # Get the language preference for the user (assuming it's stored in the Consumer model)
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    # Prepare context with all necessary data
    context = {
        'saved_products': saved_products,
        'price_alerts': price_alerts,
        'transactions': transactions,
        'selected_product': selected_product,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'language_preference': language_preference,  # Add language_preference to context
    }

    # Render the dashboard with the provided context
    return render(request, 'Baza/consumer_dashboard.html', context)

@login_required
def add_product(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('consumer_dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST or None, request.FILES or None, initial={'vendor': request.user.vendor})
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()

             # Send an email to all consumers who are following this vendor
            consumers = Consumer.objects.all()
            subject = f"New Product Added: {product.name}"
            message = f"Hello, a new product, {product.name}, has been added by {product.vendor.business_name}. Check it out in the Platform"
            
            for consumer in consumers:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # Replace with your email address
                    [consumer.user.email],
                    fail_silently=False,
                )

            return redirect('vendor_dashboard')
    else:
        form = ProductForm(initial={'vendor': request.user.vendor})

    context = {
        'form': form,
        'language_preference': request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'
    }
    
    return render(request, 'Baza/add_product.html', context)


def product_list(request):
    category_name = request.GET.get('category', None)
    
    if category_name:
        # Use filter() instead of get() to handle multiple categories
        categories = Category.objects.filter(name=category_name)  # Returns a queryset
        if categories.exists():
            products = Product.objects.filter(category__in=categories)
        else:
            products = Product.objects.none()  # If no category is found, return an empty queryset
    else:
        products = Product.objects.all()
        categories = Category.objects.all()

    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    return render(request, 'Baza/product_list.html', {
        'products': products,
        'categories': categories,
        'language_preference': language_preference
    })


@login_required
def cproduct_list(request):
    # Get the category name from the query parameters
    category_name = request.GET.get('category', None)
    
    # Fetch products based on the category or all products if no category is selected
    if category_name:
        category = Category.objects.get(name=category_name)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    # Get all categories for the sidebar or filtering options
    categories = Category.objects.all()

    # Get the user's language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    context = {
        'products': products,
        'categories': categories,
        'language_preference': language_preference,  # Pass language preference to the template
    }

    return render(request, 'Baza/consumer-product_list.html', context)


@login_required
def update_product_price(request, product_id):
    
    if not hasattr(request.user, 'vendor'):
        return redirect('consumer_dashboard')
    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)
    if request.method == 'POST':
        new_price = request.POST.get('price')
        try:
            new_price_decimal = Decimal(new_price)
        except Exception:
            new_price_decimal = None
        if new_price_decimal is not None:
            product.price = new_price_decimal
            product.save()
            
            return redirect('vendor_dashboard')
    return render(request, 'Baza/update_product_price.html', {'product': product})



@login_required
def rate_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == "POST":
        form = RateVendorForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            comment = form.cleaned_data['comment']
            
            # Create the feedback object
            feedback = Feedback.objects.create(
                vendor=vendor,
                author=request.user.get_full_name() or request.user.username,
                rating=rating,
                comment=comment,
            )

            # Send an email to the vendor about the new feedback
            subject = f"New Feedback for {vendor.business_name}"
            message = f"You have received new feedback:\n\nRating: {rating}/5\nComment: {comment}"

            # Assuming you want to notify the vendor's email
            

            return redirect('vendor_profile')
    else:
        form = RateVendorForm()

    # Get the user's language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    return render(request, 'Baza/rate_vendor.html', {'vendor': vendor, 'form': form, 'language_preference': language_preference})



@login_required
def vendor_list(request):
    """
    View to list all vendors.
    """
    vendors = Vendor.objects.all()

    # Get the user's language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    context = {
        'vendors': vendors,
        'language_preference': language_preference,  # Add language_preference to context
    }

    return render(request, 'Baza/vendor_list.html', context)



@login_required
def vendor_detail(request, vendor_id):
    """
    View to show the details of a single vendor.
    """
    vendor = get_object_or_404(Vendor, id=vendor_id)
    range_of_stars = [1, 2, 3, 4, 5]

    # Get the user's language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    return render(request, 'Baza/vendor_detail.html', {
        'vendor': vendor,
        'range_of_stars': range_of_stars,
        'language_preference': language_preference,  # Pass language_preference to the template
        'feedbacks': vendor.feedbacks.all()
    })

@login_required
def update_product(request, product_id):
    # Retrieve the product and ensure the logged-in user is the vendor of the product
    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')  
    else:
        form = ProductForm(instance=product)
    
    # Get the language preference for the logged-in vendor
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    # Add vendor info to the context
    context = {
        'form': form,
        'product': product,
        'language_preference': language_preference,  # Pass language preference to the template
        'vendor': product.vendor,  # Pass the vendor who uploaded the product
    }
    
    return render(request, 'Baza/update_product.html', context)


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)
    
    if request.method == "POST":
        product.delete()
        return redirect('product_list')  
    
    return render(request, 'Baza/delete_product_confirm.html', {'product': product})

@login_required
def save_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if SavedProduct.objects.filter(user=request.user, product__name__iexact=product.name).exists():
        messages.info(request, "You have already saved a product with this name.")
    else:
        SavedProduct.objects.create(
            user=request.user,
            product=product,
            saved_price=product.price  
        )
        messages.success(request, "Product saved successfully.")
    
    return redirect(request.META.get('HTTP_REFERER', 'cproduct_list'))

@login_required
def mark_alert_seen(request, alert_id):
    alert = get_object_or_404(PriceAlert, id=alert_id, user=request.user)
    alert.seen = True
    alert.save()
    return redirect('consumer_dashboard')

@login_required
def mark_vendor_alert_seen(request, alert_id):
    alert = get_object_or_404(PriceAlert, id=alert_id, product__vendor=request.user.vendor)
    alert.seen = True
    alert.save()
    return redirect('vendor_dashboard')


def price_comparison(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    price_updates = PriceUpdate.objects.filter(product=product).order_by('vendor__business_name')

    # Check if there's a new price update (assuming you want to notify users about price updates)
    new_price_update = price_updates.last()  # Get the latest price update

    if new_price_update:
        consumers = Consumer.objects.all()  # You can also filter specific consumers who might be following the vendor or the product
        subject = f"New Price Update for {product.name}"
        message = f"The price for {product.name} has been updated.\n\n" \
                  f"New Price: {new_price_update.price} {product.currency}\n" \
                  f"Check it out here: {request.build_absolute_uri(product.get_absolute_url())}"

        # Send email to each consumer
        for consumer in consumers:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # Replace with your email address
                [consumer.user.email],
                fail_silently=False,
            )
    return render(request, 'Baza/price_comparison.html', {'product': product, 'price_updates': price_updates})

def price_history(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    history = PriceUpdate.objects.filter(product=product).order_by('timestamp')
    labels = [update.timestamp.strftime("%Y-%m-%d %H:%M") for update in history]
    data = [float(update.price) for update in history]
    context = {
        'product': product,
        'labels': json.dumps(labels),  
        'data': json.dumps(data),
    }
    return render(request, 'Baza/price_history.html', context)

def product_comparison(request):
    product_ids_str = request.GET.get('products', '')
    if product_ids_str:
        try:
            product_ids = [int(pid.strip()) for pid in product_ids_str.split(',') if pid.strip().isdigit()]
        except ValueError:
            product_ids = []
        products = Product.objects.filter(id__in=product_ids)
    else:
        products = []
    return render(request, 'Baza/product_comparison.html', {'products': products})


def product_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()
    return render(request, 'Baza/product_search.html', {'query': query, 'results': results})

def cproduct_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()
    return render(request, 'Baza/cproduct_search.html', {'query': query, 'results': results})


@login_required
def mark_notification_seen(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, vendor=request.user.vendor)
    notification.seen = True
    notification.save()
    return redirect('vendor_dashboard')


def about_us(request):
    # For authenticated users, use language preference from the Vendor profile
    if request.user.is_authenticated and hasattr(request.user, 'vendor'):
        user_language = request.user.vendor.language_preference
    else:
        # For unauthenticated users, check if language is stored in session
        user_language = request.session.get('language_preference', 'en')  # Default to 'en' if not set

    # Activate the language immediately to ensure it's applied
    translation.activate(user_language)

    # Pass the language preference to the template context
    context = {
        'language_preference': user_language,
    }

    return render(request, 'Baza/about_us.html', context)


def contact_us(request):
    # For authenticated users, use language preference from the Vendor profile
    if request.user.is_authenticated and hasattr(request.user, 'vendor'):
        user_language = request.user.vendor.language_preference
    else:
        # For unauthenticated users, check if language is stored in session
        user_language = request.session.get('language_preference', 'en')  # Default to 'en' if not set

    # Activate the language immediately to ensure it's applied
    translation.activate(user_language)

    # Pass the language preference to the template context
    context = {
        'language_preference': user_language,
    }

    return render(request, 'Baza/contact_us.html', context)


def faq(request):
    # For authenticated users, use language preference from the Vendor profile
    if request.user.is_authenticated and hasattr(request.user, 'vendor'):
        user_language = request.user.vendor.language_preference
    else:
        # For unauthenticated users, check if language is stored in session
        user_language = request.session.get('language_preference', 'en')  # Default to 'en' if not set

    # Activate the language immediately to ensure it's applied
    translation.activate(user_language)

    # Pass the language preference to the template context
    context = {
        'language_preference': user_language,
    }

    return render(request, 'Baza/faq.html', context)


def category_products(request, category_name):
    # Get the category object based on the name passed in the URL
    category = get_object_or_404(Category, name=category_name)
    
    # Fetch products that belong to this category
    products = Product.objects.filter(category=category)
    ai_products = AIProduct.objects.filter(category=category)

    # ✅ Add an `is_ai_product` flag
    all_products = [
        {"product": p, "is_ai_product": False} for p in products
    ] + [
        {"product": p, "is_ai_product": True} for p in ai_products
    ]
    
    # Get the vendor's language preference or default to 'en'
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    # Activate the language based on the user's preference
    translation.activate(language_preference)

    context = {
        'category': category,
        'products': all_products,  # ✅ Now contains both products and AI products
        'language_preference': language_preference,
    }
    
    return render(request, 'Baza/category_products.html', context)


def consumer_category_products(request, category_name):
    # Get the category object based on the name passed in the URL
    category = get_object_or_404(Category, name=category_name)
    
    # Fetch products that belong to this category
    products = list(Product.objects.filter(category=category))
    ai_products = list(AIProduct.objects.filter(category=category))

    # ✅ Ensure `is_ai_product` is set in the model
    for ai_product in ai_products:
        ai_product.is_ai_product = True  # Mark AI-generated products

    for product in products:
        product.is_ai_product = False  # Mark regular products

    all_products = products + ai_products  # Combine the lists

    # ✅ Get consumer's language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    # ✅ Activate the language based on the user's preference
    translation.activate(language_preference)

    context = {
        'category': category,
        'products': all_products,  # ✅ Now all products are objects, not dicts
        'language_preference': language_preference,
    }
    
    return render(request, 'Baza/consumer_category_products.html', context)







@login_required
def vendor_profile_settings(request):
    """Allows vendor to update profile settings including language preference."""
    
    if request.method == "POST":
        # Get the language preference from the POST data
        language = request.POST.get("language_preference")
        
        # Update the user's language preference in the Vendor model
        request.user.vendor.language_preference = language
        request.user.vendor.save()
        
        # Activate the new language for the session
        activate(language)
        
        # Save the session's language preference
        request.session['django_language'] = language

        # Show success message
        messages.success(request, "Profile settings updated successfully!")
        
        # Redirect to the same page to refresh with new language
        return redirect("vendor_profile_settings")

    # Get the current language preference
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    context = {
        'language_preference': language_preference
    }

    return render(request, "Baza/vendor_profile_settings.html", context)


def consumer_profile_settings(request):
    """Allows consumer to update profile settings including language preference."""
    
    if request.method == "POST":
        # Get the language preference from the POST data
        language = request.POST.get("language_preference")
        
        # Ensure the consumer object exists for the user
        if not hasattr(request.user, 'consumer'):
            # Create the consumer object if it doesn't exist
            consumer = Consumer.objects.create(user=request.user, language_preference=language)
        else:
            # Update the user's language preference in the Consumer model
            request.user.consumer.language_preference = language
            request.user.consumer.save()
        
        # Activate the new language for the session
        activate(language)
        
        # Save the session's language preference
        request.session['django_language'] = language

        # Show success message
        messages.success(request, "Profile settings updated successfully!")
        
        # Redirect to the same page to refresh with new language
        return redirect("consumer_profile_settings")

    # Get the current language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    context = {
        'language_preference': language_preference
    }

    return render(request, "Baza/Consumer_profile_settings.html", context)

def set_language_preference(request):
    """Allows both registered and unregistered users to set language preference."""
    if request.method == "POST":
        language = request.POST.get("language_preference")

        if request.user.is_authenticated:
            # For logged-in users, save preference to their profile
            request.user.vendor.language_preference = language
            request.user.vendor.save()
            messages.success(request, "Profile settings updated successfully!")
        else:
            # For unregistered users, store preference in session
            request.session["language_preference"] = language
            messages.success(request, "Language preference saved for this session!")

        # Activate the language immediately
        translation.activate(language)

        # Store the language preference in the session
        request.session['django_language'] = language  # or 'language_preference' if needed

        return redirect("home")  # Redirect user to homepage or another page

    # Pass language_preference to the template
    language_preference = request.session.get('language_preference', None)
    if request.user.is_authenticated:
        language_preference = request.user.vendor.language_preference

    return render(request, "Baza/set_language.html", {'language_preference': language_preference})


def send_notification_email(user, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],  # The recipient's email address
        fail_silently=False,
    )


@login_required
def create_notification(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    notification = Notification.objects.create(
        vendor=vendor,
        message="New product update available!"
    )

    # Send an email notification to the vendor
    subject = f"New Notification for {vendor.business_name}"
    message = f"You have a new notification: {notification.message}"
    send_notification_email(vendor.user, subject, message)

    return redirect('vendor_dashboard')
 # Import AI functions
def generate_product_data(request):
    if request.method == "POST":
        form = AIProductGenerationForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            category = form.cleaned_data['category']

            print(f"🌍 Country Selected: {country}, 🏷 Category Selected: {category}")

            # ✅ Generate AI-powered product details
            product_data = generate_product_details(category.name, country)
            if not product_data:
                messages.error(request, "❌ AI failed to generate product details.")
                return redirect('generate_product')

            product_name = product_data["name"]
            product_description = product_data["description"]
            product_price = product_data["price"]
            image_prompt = product_data["image_prompt"]

            print(f"🛒 Product Name: {product_name}, 📄 Description: {product_description}, 💲 Price: {product_price}")

            # ✅ Generate AI-powered product image and save it
            product_image_file = generate_product_image(image_prompt, product_name)

            # ✅ Ensure a valid image is saved, otherwise use a default
            if not product_image_file:
                print("❌ AI Image Download Failed - Using Default Image")
                product_image_file = "ai_products/default.jpg"  # ✅ Use default image if AI fails

            print(f"🖼 Final Image File to be Stored: {product_image_file}")

            # ✅ Try to Save AI-generated product to database
            try:
                ai_product = AIProduct(
                    country=country,
                    category=category,
                    name=product_name,
                    description=product_description,
                    price=product_price,
                )

                # ✅ Assign image file correctly (Only if it's a file, not a string)
                if isinstance(product_image_file, ContentFile):
                    ai_product.image.save(product_image_file.name, product_image_file)
                    print(f"✅ Image successfully saved in database for {ai_product.name}")
                else:
                    ai_product.image = product_image_file  # Default image

                ai_product.save()

                print(f"✅ Product '{ai_product.name}' successfully saved to database!")

            except Exception as e:
                print(f"❌ Error saving product to database: {e}")
                messages.error(request, f"❌ Failed to save product to database: {e}")
                return redirect('generate_product')

            messages.success(request, f"🎉 New AI-generated product added to {category.name}. Notifications sent.")
            return redirect('category_products', category_name=category.name)

    else:
        form = AIProductGenerationForm()
    
    
    # ✅ Determine the user's language preference
    if request.user.is_authenticated:
        language_preference = (
            request.user.vendor.language_preference if hasattr(request.user, 'vendor')
            else request.user.consumer.language_preference if hasattr(request.user, 'consumer')
            else 'en'
        )
    else:
        language_preference = request.session.get('language_preference', 'en')

    return render(request, 'Baza/generate_product.html', {'form': form, 'language_preference': language_preference})


def cgenerate_product_data(request):
    if request.method == "POST":
        form = AIProductGenerationForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            category = form.cleaned_data['category']

            print(f"🌍 Country Selected: {country}, 🏷 Category Selected: {category}")

            # ✅ Generate AI-powered product details
            product_data = generate_product_details(category.name, country)
            if not product_data:
                messages.error(request, "❌ AI failed to generate product details.")
                return redirect('generate_product')

            product_name = product_data["name"]
            product_description = product_data["description"]
            product_price = product_data["price"]
            image_prompt = product_data["image_prompt"]

            print(f"🛒 Product Name: {product_name}, 📄 Description: {product_description}, 💲 Price: {product_price}")

            # ✅ Generate AI-powered product image and save it
            product_image_file = generate_product_image(image_prompt, product_name)

            # ✅ Ensure a valid image is saved, otherwise use a default
            if not product_image_file:
                print("❌ AI Image Download Failed - Using Default Image")
                product_image_file = "ai_products/default.jpg"  # ✅ Use default image if AI fails

            print(f"🖼 Final Image File to be Stored: {product_image_file}")

            # ✅ Try to Save AI-generated product to database
            try:
                ai_product = AIProduct(
                    country=country,
                    category=category,
                    name=product_name,
                    description=product_description,
                    price=product_price,
                )

                # ✅ Assign image file correctly (Only if it's a file, not a string)
                if isinstance(product_image_file, ContentFile):
                    ai_product.image.save(product_image_file.name, product_image_file)
                    print(f"✅ Image successfully saved in database for {ai_product.name}")
                else:
                    ai_product.image = product_image_file  # Default image

                ai_product.save()

                print(f"✅ Product '{ai_product.name}' successfully saved to database!")

            except Exception as e:
                print(f"❌ Error saving product to database: {e}")
                messages.error(request, f"❌ Failed to save product to database: {e}")
                return redirect('cgenerate_product')

            messages.success(request, f"🎉 New AI-generated product added to {category.name}. Notifications sent.")
            return redirect('consumer_category_products', category_name=category.name)

    else:
        form = AIProductGenerationForm()
    
    
    # ✅ Determine the user's language preference
    if request.user.is_authenticated:
        language_preference = (
            request.user.vendor.language_preference if hasattr(request.user, 'vendor')
            else request.user.consumer.language_preference if hasattr(request.user, 'consumer')
            else 'en'
        )
    else:
        language_preference = request.session.get('language_preference', 'en')

    return render(request, 'Baza/cgenerate_product.html', {'form': form, 'language_preference': language_preference})


def view_ai_details(request, product_id):
    """
    View AI-generated product details.
    """
    product = get_object_or_404(AIProduct, id=product_id)

    # Get user's language preference
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    context = {
        'product': product,
        'language_preference': language_preference,
    }

    return render(request, 'Baza/view_ai_details.html', context)


def cview_ai_details(request, product_id):
    """
    View AI-generated product details.
    """
    product = get_object_or_404(AIProduct, id=product_id)

    # Get user's language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    context = {
        'product': product,
        'language_preference': language_preference,
    }

    return render(request, 'Baza/cview_ai_details.html', context)

def generate_price_info(request):
    """
    View for selecting country and product category for AI-generated price trends.
    """
    if request.method == "POST":
        form = AIPriceInfoGenerationForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            category = form.cleaned_data['category']
            return redirect('price_information', country=country, category_name=category.name)

    else:
        form = AIPriceInfoGenerationForm()
    
     # Get user's language preference
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'


    return render(request, 'Baza/generate_price_info.html', {'form': form, 'language_preference': language_preference,})

def cgenerate_price_info(request):
    """
    View for selecting country and product category for AI-generated price trends.
    """
    if request.method == "POST":
        form = AIPriceInfoGenerationForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            category = form.cleaned_data['category']
            return redirect('cprice_information', country=country, category_name=category.name)

    else:
        form = AIPriceInfoGenerationForm()
    
     # Get user's language preference
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'


    return render(request, 'Baza/cgenerate_price_info.html', {'form': form, 'language_preference': language_preference,})


def price_information(request, country, category_name):
    """
    View to generate AI-powered price trends and insights for a selected category in a country.
    """
    category = get_object_or_404(Category, name=category_name)

    # ✅ Generate AI-powered price trends
    ai_response = generate_price_trends(category.name, country)

    if not ai_response:
        messages.error(request, "❌ AI failed to generate price trends.")
        return redirect('generate_price_info')

    # ✅ Save AI-generated price information to database
    price_info = PriceInformation.objects.create(
        country=country,
        category=category,
        insights=ai_response
    )

def cprice_information(request, country, category_name):
    """
    View to generate AI-powered price trends and insights for a selected category in a country.
    """
    category = get_object_or_404(Category, name=category_name)

    # ✅ Generate AI-powered price trends
    ai_response = generate_price_trends(category.name, country)

    if not ai_response:
        messages.error(request, "❌ AI failed to generate price trends.")
        return redirect('generate_price_info')

    # ✅ Save AI-generated price information to database
    price_info = PriceInformation.objects.create(
        country=country,
        category=category,
        insights=ai_response
    )


    return redirect('cprice_information_list')

def view_price_information(request):
    """
    View to display AI-generated price information.
    """
    price_info_list = PriceInformation.objects.all()

    for info in price_info_list:
        info.insights_list = process_ai_insights(info.insights)

    
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'


    return render(request, 'Baza/price_information.html', {'price_info_list': price_info_list, 'language_preference': language_preference,})

def cview_price_information(request):
    """
    View to display AI-generated price information.
    """
    price_info_list = PriceInformation.objects.all()

    for info in price_info_list:
        info.insights_list = process_ai_insights(info.insights)

    
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'


    return render(request, 'Baza/cprice_information.html', {'price_info_list': price_info_list, 'language_preference': language_preference,})

def delete_price_info(request, info_id):
    """
    View to delete an AI-generated price information entry.
    """
    price_info = get_object_or_404(PriceInformation, id=info_id)

    if request.method == "POST":
        price_info.delete()
        messages.success(request, "✅ Price information deleted successfully.")

    return redirect('view_price_information')


def cdelete_price_info(request, info_id):
    """
    View to delete an AI-generated price information entry.
    """
    price_info = get_object_or_404(PriceInformation, id=info_id)

    if request.method == "POST":
        price_info.delete()
        messages.success(request, "✅ Price information deleted successfully.")

    return redirect('cview_price_information')

def price_information_list(request):
    """
    Displays a list of AI-generated price information in card format.
    """
    price_info_list = PriceInformation.objects.all()

    for info in price_info_list:
        info.overall_trend = extract_overall_trend(info.insights)

    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    return render(request, 'Baza/price_information_list.html', {'price_info_list': price_info_list, 'language_preference': language_preference})

def cprice_information_list(request):
    """
    Displays a list of AI-generated price information in card format.
    """
    price_info_list = PriceInformation.objects.all()

    for info in price_info_list:
        info.overall_trend = extract_overall_trend(info.insights)

    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    return render(request, 'Baza/cprice_information_list.html', {'price_info_list': price_info_list, 'language_preference': language_preference})

def extract_overall_trend(insights):
    """
    Extracts the 'Overall Trend' section from AI-generated insights.
    Returns a short summary or 'Not Available' if not found.
    """

    if not insights:
        return "Not Available"

    # ✅ Try searching for a section labeled as "Overall Trend"
    match = re.search(r"Overall Trend:\s*(.*?)\n\n", insights, re.DOTALL)

    if match:
        return match.group(1).strip()  # ✅ Extract the text after "Overall Trend:"

    # ✅ Try alternative patterns if "Overall Trend:" is missing
    match_alt = re.search(r"\*\*1\.\s*Are prices increasing or decreasing\?\*\*(.*?)\*\*", insights, re.DOTALL)
    
    if match_alt:
        return match_alt.group(1).strip()  # ✅ Extract "Are prices increasing or decreasing?" section

    return "Not Available"

def price_information_detail(request, info_id):
    """
    Displays the full AI-generated price analysis when a user clicks 'See More'.
    """
    info = get_object_or_404(PriceInformation, id=info_id)

    info.insights_list = process_ai_insights(info.insights)

    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    return render(request, 'Baza/price_information_detail.html', {'info': info, 'language_preference': language_preference})

def cprice_information_detail(request, info_id):
    """
    Displays the full AI-generated price analysis when a user clicks 'See More'.
    """
    info = get_object_or_404(PriceInformation, id=info_id)

    info.insights_list = process_ai_insights(info.insights)

    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    return render(request, 'Baza/cprice_information_detail.html', {'info': info, 'language_preference': language_preference})

def generate_suggested_price_view(request):
    """
    View for users to get an AI-suggested price for a product.
    """
    if request.method == "POST":
        form = AISuggestedPriceForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            category = form.cleaned_data['category']
            product_name = form.cleaned_data['product_name']

            # ✅ Get AI-suggested price
            suggested_price = generate_suggested_price(product_name, category.name, country)

            # ✅ Save the AI-suggested price in the database
            ai_price = AISuggestedPrice.objects.create(
                country=country,
                category=category,
                product_name=product_name,
                suggested_price=suggested_price
            )

            messages.success(request, f"✅ Suggested price for {product_name}: {suggested_price} BIF")
            return redirect('suggested_price_list')  # Redirect to price list page

    else:
        form = AISuggestedPriceForm()
    
    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    return render(request, 'Baza/generate_suggested_price.html', {'form': form, 'language_preference': language_preference})

def suggested_price_list(request):
    """
    View to display all AI-generated suggested prices.
    """
    suggested_prices = AISuggestedPrice.objects.all()

    language_preference = request.user.consumer.language_preference if hasattr(request.user, 'consumer') else 'en'

    return render(request, 'Baza/suggested_price_list.html', {'suggested_prices': suggested_prices, 'language_preference': language_preference})

def vgenerate_suggested_price_view(request):
    """
    View for users to get an AI-suggested price for a product.
    """
    if request.method == "POST":
        form = AISuggestedPriceForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            category = form.cleaned_data['category']
            product_name = form.cleaned_data['product_name']

            # ✅ Get AI-suggested price
            suggested_price = generate_suggested_price(product_name, category.name, country)

            # ✅ Save the AI-suggested price in the database
            ai_price = AISuggestedPrice.objects.create(
                country=country,
                category=category,
                product_name=product_name,
                suggested_price=suggested_price
            )

            messages.success(request, f"✅ Suggested price for {product_name}: {suggested_price} BIF")
            return redirect('vsuggested_price_list')  # Redirect to price list page

    else:
        form = AISuggestedPriceForm()
        
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    return render(request, 'Baza/vgenerate_suggested_price.html', {'form': form, 'language_preference': language_preference})

def vsuggested_price_list(request):
    """
    View to display all AI-generated suggested prices.
    """
    suggested_prices = AISuggestedPrice.objects.all()

    
    language_preference = request.user.vendor.language_preference if hasattr(request.user, 'vendor') else 'en'

    return render(request, 'Baza/vsuggested_price_list.html', {'suggested_prices': suggested_prices, 'language_preference': language_preference})

def delete_suggested_price(request, price_id):
    """
    Deletes an AI-generated suggested price.
    """
    price = get_object_or_404(AISuggestedPrice, id=price_id)
    price.delete()
    messages.success(request, f"✅ Suggested price for {price.product_name} has been deleted.")
    return HttpResponseRedirect(reverse('suggested_price_list'))


def vdelete_suggested_price(request, price_id):
    """
    Deletes an AI-generated suggested price.
    """
    price = get_object_or_404(AISuggestedPrice, id=price_id)
    price.delete()
    messages.success(request, f"✅ Suggested price for {price.product_name} has been deleted.")
    return HttpResponseRedirect(reverse('vsuggested_price_list'))


def basecategory_products(request, category_name):
    # Get the category object based on the name passed in the URL
    category = get_object_or_404(Category, name=category_name)
    
    # Fetch products that belong to this category
    products = Product.objects.filter(category=category)
    ai_products = AIProduct.objects.filter(category=category)

    # ✅ Add an `is_ai_product` flag
    all_products = [
        {"product": p, "is_ai_product": False} for p in products
    ] + [
        {"product": p, "is_ai_product": True} for p in ai_products
    ]
    
    # Get the vendor's language preference or default to 'en'
    language_preference = request.user.language_preference 

    # Activate the language based on the user's preference
    translation.activate(language_preference)

    context = {
        'category': category,
        'products': all_products,  # ✅ Now contains both products and AI products
        'language_preference': language_preference,
    }
    
    return render(request, 'Baza/basecategory_products.html', context)
