from PIL import Image


# TODO
# Optional CBC-128 encoding
# Choice between typed and .txt input
# Ignore extension and autosearch if not given
# Default key to original file name if no key given
# Check if string fits into image before encoding
# Allow multiple encryption algos
# Decide between CLI args and GUI
# Bulk encode img folder and text folder?
# Bulk decode img folder


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
    iname = input("Enter exact image name(including extension): ")
    image = Image.open(iname, 'r')

    data = input("Enter data to be encoded : ")
    if len(data) == 0:
        raise ValueError('Data is empty :(')

    newimg = image.copy()
    encode_image(newimg, data)
    newname = input("Enter exact name for new image(including extension): ")
    print(newname.split("."))
    newimg.save(newname)


# Driver code for decoding
def decode():
    iname = input("Enter exact image name(including extension): ")
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
            return data


# Allow user to choose between encoding and decoding, probably switch to a loop to allow multiple uses
def main():
    choice = int(input("Press 1 to Encode, 2 to Decode, and 0 to Exit: "))
    if choice == 1:
        encode()
    elif choice == 2:
        print("Decoded word is : " + decode())
    elif choice == 0:
        exit(0)
    else:
        raise Exception("Enter correct input")


# Driver code
if __name__ == '__main__':
    main()
