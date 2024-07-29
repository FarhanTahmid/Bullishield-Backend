import cv2
from pathlib import Path
from PIL import Image
import easyocr
import regex
import io
import json
from django.core.files.base import ContentFile
from .models import *
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
    
    def extractTexts(image,proof_object):
        image_file=Path(image)
        print(f"We are extracting texts from the Image with ID: {proof_object.pk}")
        text_reader=easyocr.Reader(['en','bn'])
        if image_file.is_file():
            print(f"Got the image. Filepath: {image_file}")
            result_from_text = text_reader.readtext(image)
            for (bbox, text, prob) in result_from_text:
                print(f'Text: {text}, Probability: {prob},BBOX:{bbox}')
                python_bbox_list = [[int(element) for element in sublist] for sublist in bbox]
                bboxToString=json.dumps(python_bbox_list)
                if(bool(regex.fullmatch(r'\P{L}*\p{Bengali}+(?:\P{L}+\p{Bengali}+)*\P{L}*', text))):
                    new_object=ComplainProofExtractedStrings.objects.create(
                        image_id=UserComplainProof.objects.get(pk=proof_object.pk),
                        extracted_strings=text + "। ",
                        prediction_confidence=prob,
                        bbox=bboxToString
                    )
                    new_object.save()
                    pass
                else:
                    new_object=ComplainProofExtractedStrings.objects.create(
                        image_id=UserComplainProof.objects.get(pk=proof_object.pk),
                        extracted_strings=text + ". ",
                        prediction_confidence=prob,
                        bbox=bboxToString                        
                    )
                    new_object.save()
                    pass
            return True
        else:
            print("There was no image found with the filepath")
            return False
        