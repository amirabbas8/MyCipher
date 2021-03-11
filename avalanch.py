#! /usr/bin/python3
import secrets
import numpy as np
import sys
from app import encrypt, decrypt
key = b'\x2C\x7E\x15\x16\x28\xAE\xD2\xA6\xAB\xF7\x15\x81'
N = 100


def encrypt_with_key(message):
    return encrypt(bytes(message), key)


vectorized_encrypt_with_key = np.vectorize(encrypt_with_key)

np.set_printoptions(threshold=sys.maxsize)


def runner():
    table = np.zeros((96, 96))
    for i in range(N):
        bits = np.random.randint(2, size=(96,))
        message = bytes(np.packbits(bits))
        cipher = encrypt_with_key(message)
        cipher_bit = np.unpackbits(np.frombuffer(cipher, dtype=np.uint8))
        X = np.empty((96, 96))
        for j in range(96):
            if j != 0:
                bits[j-1] = not bits[j-1]
            bits[j] = not bits[j]
            X[j] = bits

        different_bits = np.packbits(X.astype(int), axis=-1)

        messages = np.apply_along_axis(bytes, -1, different_bits)

        ciphers = vectorized_encrypt_with_key(messages)
        ciphers_bits = np.unpackbits(np.frombuffer(
            ciphers, dtype=np.uint8)).reshape(96, 96)

        table += (cipher_bit ^ ciphers_bits).astype(int)
        if i % 1 == 0:
            print(
                f'**************************{int((i/N)*100)}%**************************')

    print(table)


runner()
