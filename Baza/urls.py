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
    path('basecategory/<str:category_name>/', views.basecategory_products, name='basecategory_products'),
    path('consumer_category/<str:category_name>/', views.consumer_category_products, name='consumer_category_products'),
    path('vendor/profile-settings/', views.vendor_profile_settings, name='vendor_profile_settings'),
    path('consumer/profile-settings/', views.consumer_profile_settings, name='consumer_profile_settings'),
    path("set-language/", views.set_language_preference, name="set_language_preference"),
    path('generate-product/', views.generate_product_data, name='generate_product'),
    path('cgenerate-product/', views.cgenerate_product_data, name='cgenerate_product'),
    path('ai-product/<int:product_id>/', views.view_ai_details, name='view_ai_details'),
    path('generate-price-info/', views.generate_price_info, name='generate_price_info'),
    path('price-information/<str:country>/<str:category_name>/', views.price_information, name='price_information'),
    path('view-price-information/', views.view_price_information, name='view_price_information'),
    path('delete-price-info/<int:info_id>/', views.delete_price_info, name='delete_price_info'),
    path('price-information/', views.price_information_list, name='price_information_list'),
    path('price-information/<int:info_id>/', views.price_information_detail, name='price_information_detail'),
    path('cai-product/<int:product_id>/', views.cview_ai_details, name='cview_ai_details'),
    path('cgenerate-price-info/', views.cgenerate_price_info, name='cgenerate_price_info'),
    path('cprice-information/<str:country>/<str:category_name>/', views.cprice_information, name='cprice_information'),
    path('cview-price-information/', views.cview_price_information, name='cview_price_information'),
    path('cdelete-price-info/<int:info_id>/', views.cdelete_price_info, name='cdelete_price_info'),
    path('cprice-information/', views.cprice_information_list, name='cprice_information_list'),
    path('cprice-information/<int:info_id>/', views.cprice_information_detail, name='cprice_information_detail'),
    path('generate-suggested-price/', views.generate_suggested_price_view, name='generate_suggested_price'),
    path('suggested-price-list/', views.suggested_price_list, name='suggested_price_list'),
    path('vgenerate-suggested-price/', views.vgenerate_suggested_price_view, name='vgenerate_suggested_price'),
    path('vsuggested-price-list/', views.vsuggested_price_list, name='vsuggested_price_list'),
    path('delete-suggested-price/<int:price_id>/', views.delete_suggested_price, name='delete_suggested_price'),
    path('vdelete-suggested-price/<int:price_id>/', views.delete_suggested_price, name='vdelete_suggested_price'),






]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)