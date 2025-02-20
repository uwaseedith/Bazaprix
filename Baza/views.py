from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Vendor, PriceAlert, PriceUpdate, SavedProduct, Transaction, Feedback, Notification
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProductForm, RateVendorForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from decimal import Decimal
import json
from django.contrib import messages
from django.db.models import Q

def home(request):
    # Retrieve some featured products (this example uses the first 5)
    featured_products = Product.objects.all()[:5]
    categories = Category.objects.all()
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'Baza/home.html', context)

@login_required
def vendor_profile(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('consumer_dashboard')
    vendor = request.user.vendor
    return render(request, 'Baza/vendor_profile.html', {'vendor': vendor})

@login_required
def consumer_profile(request):
    if hasattr(request.user, 'vendor'):
        return redirect('vendor_profile')
    return render(request, 'Baza/consumer_profile.html')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'Baza/product_detail.html', {'product': product})

def cproduct_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'Baza/cproduct_detail.html', {'product': product})

def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query)
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'Baza/search_results.html', context)


def home(request):
    return render(request, 'Baza/home.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            full_name = form.cleaned_data.get('full_name')
            names = full_name.split(' ', 1)
            user.first_name = names[0]
            if len(names) > 1:
                user.last_name = names[1]
            user.save()
            
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'vendor':
                phone_number = form.cleaned_data.get('phone_number')
                market = form.cleaned_data.get('market')
                Vendor.objects.create(user=user, business_name=full_name, location=market, contact_info=phone_number)
            
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'Baza/signup.html', {'form': form})

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'Baza/login.html'  

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
        

def consumer_terms(request):
    return render(request, 'Baza/consumer_terms.html')

def vendor_terms(request):
    return render(request, 'Baza/vendor_terms.html')


@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('consumer_dashboard')
    
    vendor = request.user.vendor

    price_updates = PriceAlert.objects.filter(product__vendor=vendor, seen=False).order_by('-created_at')
    products = Product.objects.filter(vendor=vendor)
    notifications = Notification.objects.filter(vendor=vendor, seen=False).order_by('-created_at')
    context = {
        'vendor': vendor,
        'price_updates': price_updates,
        'products': products,
        'notifications': notifications,
    }
    return render(request, 'Baza/vendor_dashboard.html', context)

@login_required
def consumer_dashboard(request):
    if hasattr(request.user, 'vendor'):
        return redirect('vendor_dashboard')
    
    saved_products = SavedProduct.objects.filter(user=request.user)
    price_alerts = request.user.price_alerts.filter(seen=False).order_by('-created_at')
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')

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

    context = {
        'saved_products': saved_products,
        'price_alerts': price_alerts,
        'transactions': transactions,
        'selected_product': selected_product,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }
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
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(initial={'vendor': request.user.vendor})
    return render(request, 'Baza/add_product.html', {'form': form})

def product_list(request):
    category_name = request.GET.get('category', None)
    if category_name:
        category = Category.objects.get(name=category_name)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    
    categories = Category.objects.all()
    return render(request, 'Baza/product_list.html', {'products': products, 'categories': categories})

def cproduct_list(request):
    category_name = request.GET.get('category', None)
    if category_name:
        category = Category.objects.get(name=category_name)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    
    categories = Category.objects.all()
    return render(request, 'Baza/consumer-product_list.html', {'products': products, 'categories': categories})

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
            Feedback.objects.create(
                vendor=vendor,
                author=request.user.get_full_name() or request.user.username,
                rating=rating,
                comment=comment,
            )
            
            return redirect('vendor_profile')
    else:
        form = RateVendorForm()
    
    return render(request, 'Baza/rate_vendor.html', {'vendor': vendor, 'form': form})

@login_required
def vendor_list(request):
    """
    View to list all vendors.
    """
    vendors = Vendor.objects.all()
    return render(request, 'Baza/vendor_list.html', {'vendors': vendors})

@login_required
def vendor_detail(request, vendor_id):
    """
    View to show the details of a single vendor.
    """
    vendor = get_object_or_404(Vendor, id=vendor_id)
    range_of_stars = [1, 2, 3, 4, 5]
    return render(request, 'Baza/vendor_detail.html', {'vendor': vendor, 'range_of_stars': range_of_stars, 'feedbacks': vendor.feedbacks.all()})

@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')  
    else:
        form = ProductForm(instance=product)
        
    return render(request, 'Baza/update_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)
    
    if request.method == "POST":
        product.delete()
        return redirect('vendor_dashboard')  
    
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
    return render(request, 'Baza/about_us.html')

def contact_us(request):
    return render(request, 'Baza/contact_us.html')


def faq(request):
    return render(request, 'Baza/faq.html')

def category_products(request, category_name):
    # Get the category object based on the name passed in the URL
    category = get_object_or_404(Category, name=category_name)
    
    # Fetch products that belong to this category
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products,
    }
    
    return render(request, 'Baza/category_products.html', context)


def consumer_category_products(request, category_name):
    # Get the category object based on the name passed in the URL
    category = get_object_or_404(Category, name=category_name)
    
    # Fetch products that belong to this category
    products = Product.objects.filter(category=category)
    
    # Fetch all categories to display on the page
    categories = Category.objects.all()
    
    context = {
        'category': category,
        'products': products,
        'categories': categories,  # Add this to pass categories to the template
    }
    
    return render(request, 'Baza/consumer_category_products.html', context)
