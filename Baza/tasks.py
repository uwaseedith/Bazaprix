# tasks.py
from celery import shared_task
import requests
from django.core.cache import cache
import hashlib

# tasks.py
from celery import shared_task
from .models import Category, Product
from .utils import pretranslate_text

@shared_task
def update_api_cache(url):
    response = requests.get(url)
    data = response.json()
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache.set(cache_key, data, timeout=3600)


@shared_task
def daily_pretranslate():
    languages = ['fr', 'es', 'sw', 'rw', 'rn']
    texts_to_translate = set()

    categories = Category.objects.values_list('name', flat=True)
    products = Product.objects.values_list('name', 'description')

    for cat_name in categories:
        texts_to_translate.add(cat_name)

    for prod_name, prod_desc in products:
        texts_to_translate.add(prod_name)
        texts_to_translate.add(prod_desc)

    for lang in languages:
        pretranslate_text.delay(list(texts_to_translate), lang)
