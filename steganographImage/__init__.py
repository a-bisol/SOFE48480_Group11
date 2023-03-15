from PIL import Image
from Crypto.Protocol.KDF import scrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
import json


# TODO
# Pyscript
# Work with JPG/headers
# Allow multiple encryption algos

# Encrypt the given string using CBC
# Scrypt is used to ensure that the password properly fits AES requirements
def CBC_encrypt(data, password):
    salt = get_random_bytes(16)
    key = scrypt(password, salt, 16, N=2 ** 14, r=8, p=1)
    cipher = AES.new(key, AES.MODE_CBC)
    data = data.encode('utf-8')
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    st = b64encode(salt).decode('utf-8')
    result = json.dumps({'iv': iv, 'salt': st})
    with open('AES.json', 'w') as out:
        out.write(result)
    return ct


# Decrypt the given string using CBC
def CBC_decrypt(data, password):
    with open('AES.json', 'r') as jsonIn:
        b64 = json.load(jsonIn)
    iv = b64decode(b64['iv'])
    st = b64decode(b64['salt'])
    key = scrypt(password, st, 16, N=2 ** 14, r=8, p=1)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(data), AES.block_size)
    return pt


# Convert string into binary
def enc_string(data):
    new_data = []
    for i in data:
        new_data.append(format(ord(i), '08b'))
    return new_data


# Modifies given pixels to encode data within them
def modify_pix(pixels, data):
    enc_string_list = enc_string(data)
    str_len = len(enc_string_list)
    image_data = iter(pixels)

    for i in range(str_len):
        pix = [value for value in image_data.__next__()[:3]
               + image_data.__next__()[:3] + image_data.__next__()[:3]]

        for j in range(0, 8):
            if enc_string_list[i][j] == '0' and pix[j] % 2 != 0:
                pix[j] -= 1
            elif enc_string_list[i][j] == '1' and pix[j] % 2 == 0:
                if pix[j] != 0:
                    pix[j] -= 1
                else:
                    pix[j] += 1

        if i == str_len - 1:
            if pix[-1] % 2 == 0:
                if pix[-1] != 0:
                    pix[-1] -= 1
                else:
                    pix[-1] += 1
        else:
            if pix[-1] % 2 != 0:
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]


# Traverse the image row by row and encode string within
def encode_image(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)

    for pixel in modify_pix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        if x == w - 1:
            x = 0
            y += 1
        else:
            x += 1


# Main driver code for encoding
def encode():
    iname = input("Enter exact image name (including extension): ")
    image = Image.open(iname, 'r')
    totalSpace = int((image.width * image.height) / 3)

    choice = int(input("Press 1 to use .txt for input, or 2 to type your message: "))
    if choice == 1:
        fname = input("Please enter the exact file name: ")
        with open(fname, 'r') as file:
            data = file.read().replace('\n', '')
    else:
        data = input("Enter data to be encoded: ")

    if len(data) == 0:
        raise ValueError('No data entered')

    choice = int(input("Press 1 to Encrypt with CBC: "))
    if choice == 1:
        password = input("Please enter the password to use for encryption: ")
        data = CBC_encrypt(data, password)
        print("IV and salt saved to AES.json")

    if len(data) >= (totalSpace):
        raise Exception(
            "Data longer than available space in image. Please select a shorter message or use a larger image.")
    newimg = image.copy()
    encode_image(newimg, data)
    newname = input("Enter exact name for new image (including extension): ")
    newimg.save(newname)


# Driver code for decoding
def decode():
    iname = input("Enter exact image name (including extension): ")
    image = Image.open(iname, 'r')
    data = ''
    imgdata = iter(image.getdata())

    while True:
        pixels = [value for value in imgdata.__next__()[:3]
                  + imgdata.__next__()[:3] + imgdata.__next__()[:3]]

        bin_string = ''

        for i in pixels[:8]:
            if i % 2 == 0:
                bin_string += '0'
            else:
                bin_string += '1'

        data += chr(int(bin_string, 2))
        if pixels[-1] % 2 != 0:
            break
    choice = int(input("Press 1 to decrypt with CBC (Ensure AES.json exists): "))
    if choice == 1:
        password = input("Please enter the password used for encryption: ")
        data = CBC_decrypt(b64decode(data), password).decode('utf-8')
    return data


# Driver code
if __name__ == '__main__':
    print("Please note that only .png and .bmp files are currently supported.")
    choice = int(input("Press 1 to Encode or 2 to Decode: "))
    if choice == 1:
        encode()
    elif choice == 2:
        print("Decoded message is : " + decode())
    else:
        print("Exiting")
