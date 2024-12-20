import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from math import sqrt, ceil
from PIL import Image


# resize the image if it's too small for string
def resize_img(img, bin_str_size):
    pixels_required = ceil(bin_str_size / 3) # each pixel has 3 channels
    aspect_ratio = img.shape[1] / img.shape[0]
    height_required = ceil(sqrt(pixels_required / aspect_ratio))
    width_required = ceil(height_required * aspect_ratio)

    # Ensure RGB mode, resize, and convert back to NumPy array
    resized_img = Image.fromarray(img).convert('RGB').resize((width_required, height_required))
    return np.array(resized_img)


# convert character to binary using ASCII 
def get_bin_char(character):
    result = [int(x) for x in bin(ord(character))[2:]]
    result = [0]*(7-len(result)) + result
    return result


# convert string to binary
def get_bin_str(string):
    result = [get_bin_char(char) for char in string]
    result = [i for sub_list in result for i in sub_list]
    result += [0]*7
    return result


# encrypt text using AES algorithm
def encrypt_text(text, password):
    key = password.zfill(16).encode('utf-8')[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(text.encode('utf-8'), 16))
    return base64.b64encode(encrypted).decode('utf-8')


# decrypt text using AES algorithm
def decrypt_text(encrypted_text, password):
    key = password.zfill(16).encode('utf-8')[:16]  # Ensure 16-byte key
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), 16)
    return decrypted.decode('utf-8')


# encode text into image using Steganography
def encode(img, string, password=None):
    string = string if not password else encrypt_text(string, password)
    
    # conver string to binary
    bin_str = get_bin_str(string)
    bin_str = np.array(bin_str, dtype=np.uint8)
    
    # resize the image if it's too small for string
    if img.size < bin_str.size:
        img = resize_img(img, bin_str.size)
    
    imground = img - img % 2 # ensure that LSB (least significant bit) is zero
    imground = imground.flatten() # convert image to a list
    
    # add binary string to image
    imground[:bin_str.size] += bin_str 
    
    # turn image back to its original shape
    return np.reshape(imground, img.shape)


# extract text from image
def decode(img, password=None):
    reading = True
    places = np.array([2**(6-i) for i in range(7)])
    i = 0 
    img = img.flatten()
    img = img % 2 # take list of LSB (least significant bit)
    string = ""
    while reading:
        bin_char = img[i:i+7]
        dec_char = np.sum(places*bin_char) # convert binary to decimal
        i += 7
        if dec_char == 0:
            reading = False
        else:
            string += chr(dec_char)
    
    string = string if not password else decrypt_text(string, password)
    
    return string