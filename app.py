#! /usr/bin/python3

from permutations import permutation, byte_permutation
sbox_table = [
    [3, 8, 15, 1, 10, 6, 5, 11, 14, 13, 4, 2, 7, 0, 9, 12],  # S0
    [15, 12, 2, 7, 9, 0, 5, 10, 1, 11, 14, 8, 6, 13, 3, 4],  # S1
    [8, 6, 7, 9, 3, 12, 10, 15, 13, 1, 14, 4, 0, 11, 5, 2],  # S2
    [3, 8, 15, 1, 10, 6, 5, 11, 14, 13, 4, 2, 7, 0, 9, 12],  # S0
    [1, 15, 8, 3, 12, 0, 11, 6, 2, 5, 4, 10, 9, 14, 7, 13],  # S4
    [0, 15, 11, 8, 12, 9, 6, 3, 13, 1, 2, 4, 10, 7, 5, 14],  # S3
    [1, 15, 8, 3, 12, 0, 11, 6, 2, 5, 4, 10, 9, 14, 7, 13],  # S4
    [1, 13, 15, 0, 14, 8, 2, 11, 7, 4, 12, 10, 9, 3, 5, 6],  # S7
    [15, 12, 2, 7, 9, 0, 5, 10, 1, 11, 14, 8, 6, 13, 3, 4],  # S1
    [15, 5, 2, 11, 4, 10, 9, 12, 0, 3, 14, 8, 13, 6, 7, 1],  # S5
    [7, 2, 12, 5, 8, 4, 6, 11, 14, 9, 1, 15, 13, 3, 10, 0],  # S6
    [1, 13, 15, 0, 14, 8, 2, 11, 7, 4, 12, 10, 9, 3, 5, 6],  # S7
]


def rotate_bytes(text, rotate):
    binary_string = "{:08b}".format(int(text.hex(), 16)).zfill(96)
    while rotate > 0:
        binary_string = binary_string[1:]+binary_string[:1]
        rotate = rotate-1

    bytes_string = bytes([int(binary_string[i:i+8].zfill(8), 2)
                          for i in range(0, 96, 8)])
    return bytes_string


def get_round_key(key: bytes, round_i: int):
    rotated = rotate_bytes(key, round_i*25)
    return rotated[0:6]


def xor(first: bytes, second: bytes):
    return bytes(i ^ j for i, j in zip(first, second))


def bytes2matrix(text):
    """ Converts a 6-byte array into a 4x4 matrix.  """
    binary_string = "{:08b}".format(int(text.hex(), 16)).zfill(48)
    bytes_string = [int(binary_string[i:i+3].zfill(8), 2)
                    for i in range(0, 48, 3)]
    return [bytes_string[i:i+4] for i in range(0, len(bytes_string), 4)]


def matrix2bytes(matrix):
    """ Converts a 4x4 matrix into a 6-byte array.  """
    return bytes(sum(matrix, []))


def apply_sbox(input_text: bytes, round: int):
    output_text = []
    for b in input_text:
        high, low = b >> 4, b & 0x0F
        output_text.append(int(hex(sbox_table[round][high])[2:] +
                               hex(sbox_table[round][low])[2:], 16))
    return bytes(output_text)


def shift_row(s):
    s = bytes2matrix(s)
    s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]
    return s


def xtime(a):
    return (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)


def mix_single_column(a):
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)
    return a


def mix_columns(s):
    for i in range(4):
        s[i] = mix_single_column(s[i])
    return s


def byte_permute(s, round_i):
    s = permutation[round_i](s)
    for i in range(4):
        for j in range(4):
            s[i][j] = byte_permutation(s[i][j])
    return s


def round_f(input_text: bytes, key: bytes, round_i: int):
    round_key = get_round_key(key, round_i)
    key_applied = xor(input_text, round_key)
    sbox_applied = apply_sbox(key_applied, round_i)
    row_shifted = shift_row(sbox_applied)
    column_mixed = mix_columns(row_shifted)
    permuted = byte_permute(column_mixed, round_i)
    return matrix2bytes(permuted)


def round_encrypt(input_text: bytes, key: bytes, round_i: int):
    left = input_text[:6]
    right = input_text[6:]
    return right, xor(left, round_f(right, key, round_i))


def round_decrypt(input_text: bytes, key: bytes, round_i: int):
    left = input_text[:6]
    right = input_text[6:]
    return xor(right, round_f(left, key, round_i)), left


def encrypt(input_text: bytes, key: bytes):
    next_round_input = input_text

    for i in range(12):
        next_round_input = round_encrypt(
            next_round_input, key, i)
        next_round_input = next_round_input[0]+next_round_input[1]
    return next_round_input


def decrypt(input_text: bytes, key: bytes):
    next_round_input = input_text

    for i in range(12):
        next_round_input = round_decrypt(
            next_round_input, key, 11-i)
        next_round_input = next_round_input[0]+next_round_input[1]

    return next_round_input


def split_blocks(message, block_size=12):
    return [message[i:i+16] for i in range(0, len(message), block_size)]


def encrypt_ofb(plaintext, key: bytes, iv):
    assert len(iv) == 12
    blocks = []
    previous = iv
    for plaintext_block in split_blocks(plaintext):
        block = encrypt(previous, key)
        ciphertext_block = xor(plaintext_block, block)
        blocks.append(ciphertext_block)
        previous = block

    return b''.join(blocks)


def decrypt_ofb(ciphertext, key: bytes, iv):
    assert len(iv) == 12

    blocks = []
    previous = iv
    for ciphertext_block in split_blocks(ciphertext):
        block = encrypt(previous, key)
        plaintext_block = xor(ciphertext_block, block)
        blocks.append(plaintext_block)
        previous = block

    return b''.join(blocks)


def main():
    message = b'let\'s encrypt one message. hi to all. ataaaaaack'
    key = b'\x2C\x7E\x15\x16\x28\xAE\xD2\xA6\xAB\xF7\x15\x81'
    print("  message:", message)
    iv = b'kwdlofkemqla'
    encrypted = encrypt_ofb(bytes(message), bytes(key), iv)
    print("encrypted:", encrypted)
    decrypted = decrypt_ofb(bytes(encrypted), bytes(key), iv)
    print("decrypted:", decrypted)


if __name__ == "__main__":
    main()
