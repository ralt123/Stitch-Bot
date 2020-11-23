from Crypto.Cipher import AES
from Crypto.Hash import SHA256

class encryptionAES128:

    def __init__(self, key):
        self.BLOCK_SIZE = 16
        self.KEY = self.hash(key)
        self.CIPHER = AES.new(self.KEY, AES.MODE_ECB)

    def encrypt(self, data):
        encrypted = self.CIPHER.encrypt(bytes(self.pad(data)))
        return encrypted

    def decrypt(self, data):
        decrypted = self.CIPHER.decrypt(data)
        msg = self.depad(decrypted.decode())
        return msg

    def pad(self, data):
        if (len(data) % self.BLOCK_SIZE) != 0:
            data = data + (self.BLOCK_SIZE - (len(data) % self.BLOCK_SIZE)) * '~'
            return data.encode()
        else:
            return data

    @staticmethod
    def depad(data):
        padsize = data.count('~')
        raw_data = data[:len(data) - padsize]
        return raw_data

    def hash(self, data):
        hashing = SHA256.new(bytes(data.encode()))
        return hashing.digest()