import os
import json
import re
import requests
import google.generativeai as genai
from django.core.files.base import ContentFile
from dotenv import load_dotenv
import time
import re


# ✅ Load API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ✅ Configure Gemini AI
genai.configure(api_key=GOOGLE_API_KEY)

def generate_product_details(category_name, country):
    """
    Uses Google Gemini AI to generate structured product details in JSON format.
    """
    prompt = f"""
    Generate details for a **popular product** in the **{category_name}** category available in **{country}**.
    The response **must** be a valid JSON object, without markdown or explanations.

    **Expected JSON structure:**
    {{
        "name": "Product Name",
        "description": "Short description...",
        "price": 5000,
        "currency": "BIF",
        "image_prompt": "Photo of the product in a real-world setting."
    }}
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
        response = model.generate_content(prompt)

        print(f"🔍 RAW AI RESPONSE:\n{response.text}")

        # ✅ Ensure the response is valid JSON
        clean_json = re.sub(r"```json|```", "", response.text).strip()
        product_data = json.loads(clean_json)

        return {
            "name": product_data.get("name", "Unknown Product"),
            "description": product_data.get("description", "No description available."),
            "price": product_data.get("price", 0),
            "currency": product_data.get("currency", "BIF"),
            "image_prompt": product_data.get("image_prompt", ""),
        }

    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: AI response is not valid JSON. Raw response: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Error generating product details: {e}")
        return None

def generate_product_image(image_prompt, product_name):
    """
    Uses Google Gemini AI to generate a product image URL and downloads the image.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")

        # ✅ Force AI to return a valid image URL only
        prompt = f"""
        Generate a **direct URL** to an image representing:
        "{image_prompt}".

        Return **ONLY** the image URL without any extra text, explanations, or markdown formatting.
        """

        response = model.generate_content(prompt)

        # ✅ Print full response for debugging
        print(f"🖼 RAW AI IMAGE RESPONSE:\n{response.text}")

        # ✅ Remove markdown formatting if present
        clean_response = re.sub(r"```.*?```", "", response.text, flags=re.DOTALL).strip()

        # ✅ Check if AI response is a valid image URL
        if validate_image_url(clean_response):
            print(f"✅ AI returned a valid image URL: {clean_response}")
            return download_and_save_image(clean_response, product_name)
        else:
            print(f"❌ AI did not return a valid image URL. Using default image instead.")
            return None  

    except Exception as e:
        print(f"❌ Error generating product image: {e}")
        return None

def validate_image_url(url):
    """
    Ensures the URL is an actual image file (ends in .jpg, .png, etc.).
    """
    return url.startswith("http") and any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"])

import time

def download_and_save_image(image_url, product_name):
    """
    Downloads an image from the given URL and saves it to Django's media storage.
    Adds headers to mimic a browser request and handles rate limits.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
    }

    try:
        print(f"🔄 Attempting to download image from: {image_url}")

        response = requests.get(image_url, stream=True, headers=headers)
        
        # ✅ If rate-limited, wait and retry
        if response.status_code == 429:
            print("🔄 Rate limit hit. Retrying after 5 seconds...")
            time.sleep(5)  # Wait 5 seconds before retrying
            response = requests.get(image_url, stream=True, headers=headers)

        if response.status_code == 200:
            filename = f"ai_products/{product_name.replace(' ', '_').lower()}.jpg"
            image_file = ContentFile(response.content, name=filename)
            print(f"✅ Image successfully downloaded and saved as: {filename}")
            return image_file
        else:
            print(f"❌ Failed to download image. HTTP Status: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
    
    return None  # Return None if download fails

def generate_price_trends(category_name, country):
    """
    Uses Google Gemini AI to generate price trends, predictions, and insights.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
        
        prompt = f"""
        Analyze the market trends for {category_name} in {country}. 
        - Are prices increasing or decreasing?
        - Why is this happening?
        - When will prices stabilize?
        - What external factors (inflation, economy, demand, etc.) are influencing the prices?
        """

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"❌ Error generating price trends: {e}")
        return None
    

def format_insights(text):
    """
    Converts AI-generated text into a structured format.
    """
    text = text.replace("**", "").replace("*", "- ")  # Remove markdown bold and convert bullets

    # Replace numbered markdown lists (1., 2., etc.)
    text = re.sub(r"\d\.\s", "\n<h5>", text)  # Make numbered points bigger
    text = text.replace("\n<h5>", "<h5>")  # Prevent unnecessary new lines

    return text

def process_ai_insights(insights):
    """
    Processes AI-generated insights, splitting sections and converting Markdown formatting.
    """
    if not insights:
        return []

    sections = insights.split("**")  # Split by bold sections
    formatted_sections = []

    for section in sections:
        section = section.strip()

        if section.startswith("1.") or section.startswith("2.") or section.startswith("3."):
            formatted_sections.append({"type": "heading", "content": section})
        elif section.startswith("*"):
            formatted_sections.append({"type": "bullet", "content": section.lstrip("*").strip()})
        else:
            formatted_sections.append({"type": "paragraph", "content": section})

    return formatted_sections

