from app import encrypt_ofb

with open("message.txt", "rb") as f:
    message = f.read()
    key = b'\x2C\x7E\x15\x16\x28\xAE\xD2\xA6\xAB\xF7\x15\x81'
    iv = b'kwdlofkemqla'
    encrypted = encrypt_ofb(bytes(message), bytes(key), iv)

with open("cipher.bin", "wb") as f:
    f.write(encrypted)