from PIL import Image
import cv2
import pytesseract
import re
from pymongo import MongoClient

# Sample image path (replace with your image)
image_path = 'image2.jpg'
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/249387/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

# Define a list of possible nutrient keywords (include common synonyms and variations)
possible_nutrient_keywords = [
    "calories", "fat", "protein", "cholesterol", "carbohydrate", "sodium", "vitamin", "calcium", "iron"
]

# Construct a regular expression pattern to match nutrient names and their values
nutrient_pattern = re.compile(rf'({"|".join(possible_nutrient_keywords)})[^\d\n]*([\d.]+)')


# Perform OCR on the image using OpenCV
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        # Check if the image was loaded successfully
        if image is None:
            print("Error: Could not open or read the image")
            return ""

        # Convert the image to grayscale (recommended for OCR)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Perform OCR on the grayscale image
        text = pytesseract.image_to_string(gray_image)
        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return ""


# Convert nutrient values to grams if not already in grams
def convert_to_grams(value):
    try:
        value = float(value)
        return f"{value} g"
    except ValueError:
        return value


# Extract nutrient information from the OCR text
def extract_nutrients(ocr_text):
    nutrients = {}
    matches = nutrient_pattern.findall(ocr_text.lower())
    for match in matches:
        nutrient_name, nutrient_value = match
        nutrient_value_in_grams = convert_to_grams(nutrient_value)
        nutrients[nutrient_name] = nutrient_value_in_grams
    return nutrients


# Upload nutrient information to MongoDB
def upload_to_mongodb(nutrient_info):
    try:
        client = MongoClient('mongodb+srv://root:Shyma%401234@cluster.wlnl9uh.mongodb.net/')  # Replace with your MongoDB URI
        db = client['semicon']
        collection = db['Data']
        collection.insert_one(nutrient_info)
        print("Data uploaded to MongoDB successfully.")
    except Exception as e:
        print(f"Error uploading data to MongoDB: {str(e)}")


# Main function
if __name__ == "__main__":
    ocr_text = extract_text_from_image(image_path)
    extracted_nutrients = extract_nutrients(ocr_text)

    if extracted_nutrients:
        print("Extracted Nutrient Information:")
        for nutrient, value in extracted_nutrients.items():
            print(f"{nutrient.capitalize()}: {value}")

        # Upload the nutrient information to MongoDB
        upload_to_mongodb(extracted_nutrients)
    else:
        print("No nutrient information found in the image.")