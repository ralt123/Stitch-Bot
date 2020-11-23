from Crypto.Cipher import AES
from Crypto.Hash import SHA256

BLOCK_SIZE = 16


def pad(data):
    if (len(data) % BLOCK_SIZE) != 0:
        data = data + (BLOCK_SIZE - (len(data) % BLOCK_SIZE)) * '~'
        return data.encode()
    else:
        return data


def depad(data):
    padsize = data.count('~')
    raw_data = data[:len(data) - padsize]
    return raw_data


def encrypt(data):
    encrypted = CIPHER.encrypt(bytes(pad(data)))
    return encrypted


def decrypt(data):
    decrypted = CIPHER.decrypt(data)
    msg = depad(decrypted.decode())
    return msg


def hash_(data):
    hashing = SHA256.new(bytes(data.encode()))
    return hashing.digest()


key = '# Enter Decrypt Key you want to use here'
KEY = hash_(key)
CIPHER = AES.new(KEY, AES.MODE_ECB)

x = encrypt('# Enter key you want to encrypt here')
