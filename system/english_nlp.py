import re
from collections import Counter
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
import emoji

# Function to remove numbers from a list of words
def remove_numbers(text):
    """
    removees any numbers from the text
    """
    clean_text=''.join([i for i in text if not i.isdigit()])
    return clean_text

def remove_emoji(text):
    emoji_list = [c for c in text if c in emoji.UNICODE_EMOJI['en']]
    return text.translate({ord(c): None for c in emoji_list})


# Function to remove URLs from a list of words
def remove_urls(text, replacement_text=""):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    urls = url_pattern.findall(text)
 
    for url in urls:
        text = text.replace(url, replacement_text)
 
    return text


