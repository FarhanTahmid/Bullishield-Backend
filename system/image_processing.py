import cv2
from PIL import Image
import io
from django.core.files.base import ContentFile


class ProcessImageForOCR:
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
        