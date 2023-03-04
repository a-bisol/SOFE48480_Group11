from Crypto.Protocol.KDF import scrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
import json

if __name__ == "__main__":
    data = b"test data"
    password = "testing password"
    with open('AES.json', 'r') as jsonIn:
        b64 = json.load(jsonIn)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    st = b64decode(b64['salt'])
    key = scrypt(password, st, 16, N=2 ** 14, r=8, p=1)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    print(pt)
