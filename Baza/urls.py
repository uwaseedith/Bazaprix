from django.urls import path
from . import views
from .views import CustomLoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('consumer-terms/', views.consumer_terms, name='consumer_terms'),
    path('vendor-terms/', views.vendor_terms, name='vendor_terms'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cproduct/<int:product_id>/', views.cproduct_detail, name='cproduct_detail'),
    path('search/', views.search, name='search'),
    path('vendor-dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('consumer-dashboard/', views.consumer_dashboard, name='consumer_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.product_list, name='product_list'),
    path('cproducts/', views.cproduct_list, name='cproduct_list'),
    path('vendor-profile/', views.vendor_profile, name='vendor_profile'),
    path('consumer-profile/', views.consumer_profile, name='consumer_profile'),
    path('rate-vendor/<int:vendor_id>/', views.rate_vendor, name='rate_vendor'),
    path('vendor-list/', views.vendor_list, name='vendor_list'),
    path('vendor-detail/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('update-product/<int:product_id>/', views.update_product, name='update_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('save-product/<int:product_id>/', views.save_product, name='save_product'),
    path('mark-alert-seen/<int:alert_id>/', views.mark_alert_seen, name='mark_alert_seen'),
    path('mark-vendor-alert-seen/<int:alert_id>/', views.mark_vendor_alert_seen, name='mark_vendor_alert_seen'),
    path('price-comparison/<int:product_id>/', views.price_comparison, name='price_comparison'),
    path('price-history/<int:product_id>/', views.price_history, name='price_history'),
    path('product-comparison/', views.product_comparison, name='product_comparison'),
    path('search/', views.product_search, name='product_search'),
    path('csearch/', views.cproduct_search, name='cproduct_search'),
    path('mark-notification-seen/<int:notification_id>/', views.mark_notification_seen, name='mark_notification_seen'),
    path('about-us/', views.about_us, name='about_us'),
    path('faq/', views.faq, name='faq'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('category/<str:category_name>/', views.category_products, name='category_products'),
    path('consumer_category/<str:category_name>/', views.consumer_category_products, name='consumer_category_products'),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)