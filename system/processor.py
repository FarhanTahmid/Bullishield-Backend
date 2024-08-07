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
        
        # get the image file as FILE
        image=cv2.imread(imageFile)
        
        # convert the image to Gray
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # scale the image
        scaled_image = cv2.resize(gray_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # denoise image
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
        # default to JPEG if no format is found
        pil_format = EXTENSION_TO_PIL_FORMAT.get(fileExtension, 'JPEG')
        
        # save the image
        pil_image.save(img_io, format=pil_format)
        processed_image_file=ContentFile(img_io.getvalue(), f'{filename}.{pil_format}')
        
        return processed_image_file
    
    
    
    def cyberBullyingFlaggedImageProcess(imageFile,fileExtension,filename,bbox_list):
        # get the image
        image = cv2.imread(imageFile)
        
        # as their can be multiple strings to highlight
        for line in bbox_list:
            # top left margin of a line is the first element of the list
            line_top_left=line[0]
            # bottom right margin of a line is the first element of the list
            line_bottom_right=line[1]
            # draw rectangles ((255, 0, 255)denotes magenta color
            cv2.rectangle(image, tuple(line_top_left), tuple(line_bottom_right), (255, 0, 255), 2)

        # Convert the OpenCV image to a PIL image
        pil_image = Image.fromarray(image)
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
        processed_flagged_image=ContentFile(img_io.getvalue(), f'{filename}.{pil_format}')

        return processed_flagged_image
    
    
    
    
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
                if abs(current_y - previous_y) < 20:
                    current_line.append((text, bbox, prob))
                else:
                    # Otherwise, start a new line
                    lines.append(current_line)
                    # merge text bbox and probabilty together
                    current_line = [(text, bbox, prob)]

            previous_y = current_y

        # Add the last line
        if current_line:
            lines.append(current_line)

        return lines

    
    def convertListToString(bbox_list):
        '''converts a list to json string'''
        # to convert list to string, check if the elements are the same
        python_bbox_list = [[int(element) for element in sublist] for sublist in bbox_list]
        # dump as json string
        bboxToString=json.dumps(python_bbox_list)
        return bboxToString
    
    def extractTexts(image,proof_object):
        image_file=Path(image)
        # define OCR reader language
        text_reader=easyocr.Reader(['en','bn'])
        if image_file.is_file():
            
            # get the line results from readtexts, this identifies all the texts
            results=text_reader.readtext(image,detail=1)
            
            # Get the lines from the OCR results
            lines = OCRActions.merge_words_into_lines(results=results)
            
            # Store and print the bounding boxes and probabilities of each whole line
            line_bboxes_probs = []
            
            for line in lines:
                line_text = ' '.join([text for text, bbox, prob in line])
                # Calculate a bounding box around the whole line
                line_bboxes_coords = [bbox for text, bbox, prob in line]
                line_top_left = [min(bbox[0][0] for bbox in line_bboxes_coords), min(bbox[0][1] for bbox in line_bboxes_coords)]
                line_bottom_right = [max(bbox[2][0] for bbox in line_bboxes_coords), max(bbox[2][1] for bbox in line_bboxes_coords)]
                
                # Calculate the average probability for the line
                avg_prob = np.mean([prob for text, bbox, prob in line])
                
                # Store the bounding box and probability for the whole line as lists
                line_bbox_prob = [line_top_left, line_bottom_right, avg_prob,line_text]
                line_bboxes_probs.append(line_bbox_prob)
    
            #  store bounding boxes to extract later while generating bullying flagged picture
            for i, bbox_prob in enumerate(line_bboxes_probs):
                new_object=ComplainProofExtractedStrings.objects.create(
                        image_id=UserComplainProof.objects.get(pk=proof_object.pk),
                        extracted_strings=bbox_prob[3],
                        prediction_confidence=bbox_prob[2],
                        bbox=OCRActions.convertListToString(bbox_prob[:2])
                )
                new_object.save() 
            return True
        else:
            return False

class TextProcessor:
    
    def banglaTextProcessor(string):
        '''Processes bangla texts'''
        clean_punctuation=bangla_nlp.clean_punctuations(text=string)
        clean_emoji=bangla_nlp.clean_emoji(text=clean_punctuation)
        clean_url=bangla_nlp.clean_url_and_email(clean_emoji)
        clean_text=bangla_nlp.clean_digits(text=clean_url)
        return clean_text
    
    def englishTextProcessor(text):
        '''Processes english texts'''
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

