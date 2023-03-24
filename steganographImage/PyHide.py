from PIL import Image
from Crypto.Protocol.KDF import scrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
import json
import sys
import os


# Scrypt is used in the following algorithms to ensure that the given password properly fits AES requirements
# Generic encryption function that depends on algorithm input
def encrypt(data, password, algo: str):
    salt = get_random_bytes(16)
    key = scrypt(password, salt, 16, N=2 ** 14, r=8, p=1)
    if algo == "CBC":
        cipher = AES.new(key, AES.MODE_CBC)
    elif algo == "CFB":
        cipher = AES.new(key, AES.MODE_CFB)
    elif algo == "OFB":
        cipher = AES.new(key, AES.MODE_OFB)
    data = data.encode('utf-8')
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    st = b64encode(salt).decode('utf-8')
    result = json.dumps({'iv': iv, 'salt': st})
    with open(algo + '.json', 'w') as out:
        out.write(result)
    return ct


# Decrypt the given string using CBC
def CBC_decrypt(data, password):
    with open('CBC.json', 'r') as jsonIn:
        b64 = json.load(jsonIn)
    iv = b64decode(b64['iv'])
    st = b64decode(b64['salt'])
    key = scrypt(password, st, 16, N=2 ** 14, r=8, p=1)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(data), AES.block_size)
    return pt


# Decrypt the given string using CFB
def CFB_decrypt(data, password):
    with open('CFB.json', 'r') as jsonIn:
        b64 = json.load(jsonIn)
    iv = b64decode(b64['iv'])
    st = b64decode(b64['salt'])
    key = scrypt(password, st, 16, N=2 ** 14, r=8, p=1)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    pt = unpad(cipher.decrypt(data), AES.block_size)
    return pt


# Decrypt the given string using OFB
def OFB_decrypt(data, password):
    with open('OFB.json', 'r') as jsonIn:
        b64 = json.load(jsonIn)
    iv = b64decode(b64['iv'])
    st = b64decode(b64['salt'])
    key = scrypt(password, st, 16, N=2 ** 14, r=8, p=1)
    cipher = AES.new(key, AES.MODE_OFB, iv)
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
    iname = input("\nEnter exact image name (including extension): ")
    image = Image.open(iname, 'r')
    total_space = int((image.width * image.height) / 3)
    enc_choice = -1
    print("Text input")
    while enc_choice != (1 or 2):
        print("\t1 - .txt file input\n\t2 - Type your message\n\t0 - Quit")
        enc_choice = int(input("Choice: "))
        if enc_choice == 1:
            fname = input("\nPlease enter the exact file name: ")
            with open(fname, 'r') as file:
                data = file.read().replace('\n', '')
            break
        elif enc_choice == 2:
            data = input("\nEnter data to be encoded: ")
            break
        elif enc_choice == 0:
            sys.exit(0)
        else:
            print("\nPlease enter a valid choice")

    if len(data) == 0:
        raise ValueError('No data entered')

    alg_choice = -1
    print("\nEncryption algorithm")
    while alg_choice != (1 or 2):
        print('\t1 - Plaintext\n\t2 - CBC\n\t3 - CFB\n\t4 - OFB\n\t0 - Quit')
        alg_choice = int(input("Choice: "))
        if alg_choice == 1:
            break
        elif alg_choice == 2:
            password = input("\nPlease enter the password to use for encryption: ")
            data = encrypt(data, password, "CBC")
            # data = CBC_encrypt(data, password)
            print("IV and salt saved to CBC.json")
            break
        elif alg_choice == 3:
            password = input("\nPlease enter the password to use for encryption: ")
            data = CFB_encrypt(data, password)
            print("IV and salt saved to CFB.json")
            break
        elif alg_choice == 4:
            password = input("\nPlease enter the password to use for encryption: ")
            data = OFB_encrypt(data, password)
            print("IV and salt saved to OFB.json")
            break
        elif alg_choice == 0:
            sys.exit(0)
        else:
            print("Please enter a valid choice")

    if len(data) >= (total_space):
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

    alg_choice = -1
    print("\nEncryption algorithm")
    while alg_choice != (1 or 2):
        print("\t1 - Plaintext\n\t2 - CBC\n\t3 - CFB\n\t4 - OFB\n\t0 - Quit")
        alg_choice = int(input("Choice: "))
        if alg_choice == 1:
            break
        elif alg_choice == 2:
            file_exist = os.path.isfile('./CBC.json')
            if not file_exist:
                raise Exception("CBC.json not found, please place it in the same folder/directory as this file.")
            password = input("Please enter the password used for encryption: ")
            data = CBC_decrypt(b64decode(data), password).decode('utf-8')
            break
        elif alg_choice == 3:
            file_exist = os.path.isfile('./CFB.json')
            if not file_exist:
                raise Exception("CFB.json not found, please place it in the same folder/directory as this file.")
            password = input("Please enter the password used for encryption: ")
            data = CFB_decrypt(b64decode(data), password).decode('utf-8')
            break
        elif alg_choice == 4:
            file_exist = os.path.isfile('./OFB.json')
            if not file_exist:
                raise Exception("OFB.json not found, please place it in the same folder/directory as this file.")
            password = input("Please enter the password used for encryption: ")
            data = OFB_decrypt(b64decode(data), password).decode('utf-8')
            break
        elif alg_choice == 0:
            sys.exit(0)
        else:
            print("Please enter a valid choice")
    return data


# Driver code
if __name__ == '__main__':
    choice = -1
    print("Please note that only .png and .bmp files are currently supported.")
    print("Choose operation mode")
    while choice != 0:
        print("\t1 - Encode\n\t2 - Decode\n\t0 - Quit")
        choice = int(input("Choice: "))
        if choice == 1:
            encode()
            print("Choose operation mode")
        elif choice == 2:
            print("Decoded message is: " + decode())
            print("Choose operation mode")
        elif choice == 0:
            print("Exiting")
            sys.exit(0)
        else:
            print("\nPlease enter a valid choice")
