import cv2
from pathlib import Path
from PIL import Image
import easyocr
import regex
import io
import json
from django.core.files.base import ContentFile
from .models import *
from . import bangla_nlp,english_nlp
import string
from .cyberbullying_classifiers import *
import numpy as np


class OCRActions:
    def processImage(imageFile,fileExtension,filename):
        image=cv2.imread(imageFile)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        scaled_image = cv2.resize(gray_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        final_image = cv2.fastNlMeansDenoising(scaled_image, None, 30, 7, 21)
        
        # Convert the OpenCV image to a PIL image
        pil_image = Image.fromarray(final_image)
        # Save the PIL image to an in-memory file
        img_io = io.BytesIO()
        # Mapping from file extensions to PIL formats
        EXTENSION_TO_PIL_FORMAT = {
            'JPG': 'JPEG',
            'JPEG': 'JPEG',
            'PNG': 'PNG',
            'BMP': 'BMP',
            'GIF': 'GIF',
            'TIFF': 'TIFF',
        }
        pil_format = EXTENSION_TO_PIL_FORMAT.get(fileExtension, 'JPEG')
        
        pil_image.save(img_io, format=pil_format)
        
        processed_image_file=ContentFile(img_io.getvalue(), f'{filename}.{pil_format}')
        
        return processed_image_file
    
    
    # Function to calculate the vertical center of a bounding box
    def vertical_center(bbox):
        return (bbox[0][1] + bbox[2][1]) / 2
    
    # Function to merge words into lines based on y-coordinate proximity
    def merge_words_into_lines(results):
        lines = []
        current_line = []
        previous_y = None

        for result in results:
            bbox, text, prob = result
            current_y = OCRActions.vertical_center(bbox)

            if previous_y is None:
                current_line.append((text, bbox, prob))
            else:
                # If the current word is vertically close to the previous word, append to the current line
                if abs(current_y - previous_y) < 20:  # Adjust this threshold as needed
                    current_line.append((text, bbox, prob))
                else:
                    # Otherwise, start a new line
                    lines.append(current_line)
                    current_line = [(text, bbox, prob)]

            previous_y = current_y

        # Add the last line
        if current_line:
            lines.append(current_line)

        return lines

    
    def convertListToString(bbox_list):
        python_bbox_list = [[int(element) for element in sublist] for sublist in bbox_list]
        bboxToString=json.dumps(python_bbox_list)
        return bboxToString
    
    def extractTexts(image,proof_object):
        image_file=Path(image)
        print(f"We are extracting texts from the Image with ID: {proof_object.pk}")
        text_reader=easyocr.Reader(['en','bn'])
        if image_file.is_file():
            
            results=text_reader.readtext(image,detail=1)
            
            # Get the lines from the OCR results
            lines = OCRActions.merge_words_into_lines(results=results)
            
            # Store and print the bounding boxes and probabilities of each whole line
            line_bboxes_probs = []
            
            for line in lines:
                line_text = ' '.join([text for text, bbox, prob in line])
                print(f"Extracted Line: {line_text}")  # Print the line text

                # Calculate a bounding box around the whole line
                line_bboxes_coords = [bbox for text, bbox, prob in line]
                line_top_left = [min(bbox[0][0] for bbox in line_bboxes_coords), min(bbox[0][1] for bbox in line_bboxes_coords)]
                line_bottom_right = [max(bbox[2][0] for bbox in line_bboxes_coords), max(bbox[2][1] for bbox in line_bboxes_coords)]
                
                # Calculate the average probability for the line
                avg_prob = np.mean([prob for text, bbox, prob in line])
                
                # Store the bounding box and probability for the whole line as lists
                line_bbox_prob = [line_top_left, line_bottom_right, avg_prob,line_text]
                line_bboxes_probs.append(line_bbox_prob)
    
            # Print the stored bounding boxes
            for i, bbox_prob in enumerate(line_bboxes_probs):
                print(f"Line {i + 1} Bounding Box: {bbox_prob[:2]}, Probability: {bbox_prob[2]}")
                new_object=ComplainProofExtractedStrings.objects.create(
                        image_id=UserComplainProof.objects.get(pk=proof_object.pk),
                        extracted_strings=bbox_prob[3],
                        prediction_confidence=bbox_prob[2],
                        bbox=OCRActions.convertListToString(bbox_prob[:2])
                )
                new_object.save() 
                print("New Object created!")
            return True
        else:
            print("There was no image found with the filepath")
            return False

class TextProcessor:
    
    def banglaTextProcessor(string):
        clean_punctuation=bangla_nlp.clean_punctuations(text=string)
        clean_emoji=bangla_nlp.clean_emoji(text=clean_punctuation)
        clean_url=bangla_nlp.clean_url_and_email(clean_emoji)
        clean_text=bangla_nlp.clean_digits(text=clean_url)
        return clean_text
    
    def englishTextProcessor(text):
        clean_emoji=english_nlp.remove_emoji(text)
        clean_punctuation=clean_emoji.translate(str.maketrans('', '', string.punctuation))
        clean_url=english_nlp.remove_urls(clean_punctuation)
        clean_text=english_nlp.remove_numbers(clean_url)
        return clean_text
    
    def textProcessor(string,device,english_model,bangla_model):
        # first identify in which language the text is in
        if(bool(regex.fullmatch(r'\P{L}*\p{Bengali}+(?:\P{L}+\p{Bengali}+)*\P{L}*', string=string))):
            # send it to bangla text processor
            processed_text=TextProcessor.banglaTextProcessor(string)
            bullying_prediction=BullyingProcessor.predict_bangla_cyberbullying(device=device,model=bangla_model,texts=[processed_text])
            bullying_flag=False
            for i in bullying_prediction:
                if(i>=0.5):
                    bullying_flag=True
                    break
            return processed_text,bullying_flag
        else:
            # send it to English Text Processor
            processed_text=TextProcessor.englishTextProcessor(string)
            bullying_prediction=BullyingProcessor.predict_english_cyberbullying(device=device,model=english_model,texts=[processed_text])
            bullying_flag=False
            for i in bullying_prediction:
                if(i>=0.5):
                    bullying_flag=True
                    break
            return processed_text,bullying_flag

