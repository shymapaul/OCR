import cv2
import pytesseract
import re
from pymongo import MongoClient

# Sample image path (replace with your image)
image_path = 'first.png'
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/249387/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

# Define a list of possible nutrient keywords (include common synonyms and variations)
possible_nutrient_keywords = [
    "calories", "fat", "protein", "cholesterol", "carbohydrate", "sodium", "vitamin", "calcium", "iron"
]

# Construct a regular expression pattern to match nutrient names and their values
nutrient_pattern = re.compile(rf'({"|".join(possible_nutrient_keywords)})[^\d\n]*([\d.]+)')


def extract_text_from_image(image_path):
    try:
        img = cv2.imread(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return ""


def extract_nutrients(ocr_text):
    nutrients = {}
    matches = nutrient_pattern.findall(ocr_text.lower())
    print(matches)
    for match in matches:
        nutrient_name, nutrient_value = match
        nutrients[nutrient_name] = f"{float(nutrient_value)} g"
    return nutrients

# Upload nutrient information to MongoDB


def upload_to_mongodb(nutrient_info):
    try:
        client = MongoClient('mongodb+srv://shyma:z3iIfgcL3MpIzwQD@cluster0.xdxddba.mongodb.net/?retryWrites=true&w=majority')  # Replace with your MongoDB URI
        db = client['semicon']
        collection = db['Data']
        collection.insert_one(nutrient_info)
        print("Data uploaded to MongoDB successfully.")
    except Exception as e:
        print(f"Error uploading data to MongoDB: {str(e)}")


if __name__ == "__main__":
    ocr_text = extract_text_from_image(image_path)
    # print(ocr_text)
    extracted_nutrients = extract_nutrients(ocr_text)
    # print(extracted_nutrients)
    if extracted_nutrients:
        print("Extracted Nutrient Information:")
        for nutrient, value in extracted_nutrients.items():
            print(f"{nutrient.capitalize()}: {value}")
        # Upload the nutrient information to MongoDB
        upload_to_mongodb(extracted_nutrients)
    else:
        print("No nutrient information found in the image.")
