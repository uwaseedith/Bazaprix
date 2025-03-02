from deep_translator import GoogleTranslator

def translate_text(text, target_lang):
    """Translates text into the target language using deep-translator."""
    if text and target_lang:
        try:
            # Ensure text is not empty and the target language is valid
            translation = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return translation
        except Exception as e:
            print(f"❌ Translation error: {e}")
    return text  # Return the original text if no translation occurs
