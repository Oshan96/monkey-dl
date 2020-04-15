from requests.utils import requote_uri
from base64 import b64decode
from hashlib import md5
from Crypto.Cipher import AES


class TwistSourceDecryptor:
    BLOCK_SIZE = 16
    SECRET_KEY = b'LXgIVP&PorO68Rq7dTx8N^lP!Fa5sGJ^*XK'

    def __init__(self, enc_src):
        self.enc_src = enc_src.encode('utf-8')

    def __pad(self, data):
        length = self.BLOCK_SIZE - (len(data) % self.BLOCK_SIZE)
        return data + (chr(length) * length).encode()

    def __unpad(self, data):
        # print(data[-1])
        return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

    def __get_key_iv(self, data, salt, output=48):
        assert len(salt) == 8, len(salt)
        data += salt
        key = md5(data).digest()
        key_iv_data = key
        while len(key_iv_data) < output:
            key = md5(key + data).digest()
            key_iv_data += key

        return key_iv_data[:output]

    def decrypt(self):
        enc_data = b64decode(self.enc_src)
        # print("b64decode enc :", enc_data)
        assert enc_data[:8] == b'Salted__'

        salt = enc_data[8:16]  # 8byte salt
        key_iv = self.__get_key_iv(self.SECRET_KEY, salt)  # key+iv is 48bytes
        key = key_iv[:32]  # key is 32byte
        iv = key_iv[32:]  # 16byte iv
        # print("key :", key)
        # print("iv :", iv)

        aes = AES.new(key, AES.MODE_CBC, iv)

        decrypt_data = aes.decrypt(enc_data[16:])  # actual data are after first 16bytes (which is salt)
        decrypt_data = self.__unpad(decrypt_data).decode('utf-8').lstrip(' ')
        # print(decrypt_data)
        return requote_uri(decrypt_data)  # parse to url safe value

# if __name__ == "__main__":
#     enc = "U2FsdGVkX19HQClvPEOzwC/GB0VRwqWykgOTB+xGwpi7Tu6uTdSUbBsiKOJ5KH0udjYE/10xinA7Km/nGm88txhTYb/oqSksAaBBV8xM0XQ="
#     dec = TwistSourceDecryptor(enc).decrypt()
#     print(dec)
