import cv2
import pytesseract
import re
from pymongo import MongoClient
from fuzzywuzzy import process

image_path = "Opencv/1 (2).png"
pytesseract.pytesseract.tesseract_cmd = r'C:/Users/249387/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

# Define a list of possible nutrient keywords (include common synonyms and variations)
possible_nutrient_keywords = [
    "calories", "fat", "saturated fat", "trans fat", "protein", "cholesterol", "carbohydrate", "sodium", "vitamin d", "vitamin a", "vitamin c", "calcium", "iron"
]

# Construct a regular expression pattern to match nutrient names and their values
nutrient_pattern = re.compile(rf'({"|".join(possible_nutrient_keywords)})[^\d\n]*([\d.]+)([a-zA-Z]*)')


def extract_text_from_image(image_path):
    try:

        img = cv2.imread(image_path)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh, image_th = cv2.threshold(img_gray, 150, 180, cv2.THRESH_BINARY)
        # print(thresh)
        # cv2.imshow("Window Title", image_th)
        # cv2.waitKey(0)
        text = pytesseract.image_to_string(image_th)
        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return ""


def correct_nutrient_name(nutrient_name, possible_keywords):
    best_match, score = process.extractOne(nutrient_name, possible_keywords)
    # print(score)
    if score >= 85:
        return best_match
    else:
        return nutrient_name


def extract_nutrients(ocr_text):
    nutrients = {}
    matches = nutrient_pattern.findall(ocr_text.lower())
    print(matches)
    for match in matches:
        nutrient_name, nutrient_value, nutrient_units = match
        corrected_name = correct_nutrient_name(nutrient_name, possible_nutrient_keywords)
        nutrients[corrected_name] = f"{nutrient_value} {nutrient_units}"
    return nutrients

# Upload nutrient information to MongoDB


def upload_to_mongodb(nutrient_info):
    try:
        client = MongoClient('mongodb+srv://shyma:z3iIfgcL3MpIzwQD@cluster0.xdxddba.mongodb.net/?retryWrites=true&w=majority')
        db = client['semicon']
        collection = db['Data']
        collection.insert_one(nutrient_info)
        print("Data uploaded to MongoDB successfully.")
    except Exception as e:
        print(f"Error uploading data to MongoDB: {str(e)}")


if __name__ == "__main__":
    ocr_text = extract_text_from_image(image_path)
    print(ocr_text)
    extracted_nutrients = extract_nutrients(ocr_text)

    if extracted_nutrients:
        print("Extracted Nutrient Information:")
        for nutrient, value in extracted_nutrients.items():
            print(f"{nutrient.capitalize()}: {value}")
        # Upload the nutrient information to MongoDB
        upload_to_mongodb(extracted_nutrients)
    else:
        print("No nutrient information found in the image.")