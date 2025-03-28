from django.core.cache import cache
from deep_translator import GoogleTranslator
import hashlib
from celery import shared_task

def translate_text(text, target_lang):
    if not text or not target_lang or target_lang == 'en':
        return text

    cache_key = f"translation_{hashlib.md5((text + target_lang).encode()).hexdigest()}"

    translation = cache.get(cache_key)
    if translation:
        return translation

    try:
        translation = GoogleTranslator(source='auto', target=target_lang).translate(text)
        cache.set(cache_key, translation, timeout=86400)  # cache for 24 hours
        return translation
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return text



@shared_task
def pretranslate_text(text_list, target_lang):
    translator = GoogleTranslator(source='auto', target=target_lang)
    for text in text_list:
        cache_key = f"translation_{hashlib.md5((text + target_lang).encode()).hexdigest()}"
        if not cache.get(cache_key):
            try:
                translation = translator.translate(text)
                cache.set(cache_key, translation, timeout=86400)  # 24 hours
                print(f"✅ Pretranslated '{text}' to '{translation}'")
            except Exception as e:
                print(f"❌ Pretranslation error for '{text}': {e}")
