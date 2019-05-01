""" Various utilities """
import hashlib
from typing.io import BinaryIO

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def encode_base58(s: bytes) -> str:
    """
    Encode address using base58

    Parameters
    ----------
    s: bytes
        Byte string to encode

    Returns
    -------
    str

    """
    count = 0
    for c in s:
        if c == 0:
            count += 1
        else:
            break

    prefix = '1' * count
    num = int.from_bytes(s, 'big')
    result = ''

    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result

    return prefix + result


def decode_base58(s: str) -> bytes:
    """
    Get hash from encoded address

    The first byte is the network prefix and the last 4 are the checksum. The middle 20 are the
    actual 20-byte hash (aka hash160).
    """
    num = 0
    for c in s:
        num *= 58
        num += BASE58_ALPHABET.index(c)

    combined = num.to_bytes(25, byteorder='big')
    checksum = combined[-4:]

    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError('bad address: {} {}'.format(checksum, hash256(combined[:-4])[:4]))

    return combined[1:-4]


def hash256(x: bytes) -> bytes:
    """ sha256 followed by sha256 """
    return hashlib.sha256(hashlib.sha256(x).digest()).digest()


def hash160(x: bytes) -> bytes:
    """ sha256 followed by ripemd160 """
    return hashlib.new('ripemd160', hashlib.sha256(x).digest()).digest()


def encode_base58_checksum(b: bytes) -> str:
    return encode_base58(b + hash256(b)[:4])


def little_endian_to_int(b: bytes) -> int:
    return int.from_bytes(b, 'little')


def int_to_little_endian(n: int, length: int) -> bytes:
    return n.to_bytes(length, 'little')


def read_varint(s: BinaryIO) -> int:
    """ reads a variable integer from a stream """
    i = s.read(1)[0]

    if i == 0xfd:
        # 2 bytes
        return little_endian_to_int(s.read(2))

    elif i == 0xfe:
        # 4 bytes
        return little_endian_to_int(s.read(4))

    elif i == 0xff:
        # 8 bytes
        return little_endian_to_int(s.read(8))
    else:
        return i


def encode_varint(i: int) -> bytes:
    """ encodes an integer as a varint """
    if i < 0xfd:
        return bytes([i])

    elif i < 0x10000:
        return b'\xfd' + int_to_little_endian(i, 2)

    elif i < 0x100000000:
        return b'\xfe' + int_to_little_endian(i, 4)

    elif i < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)

    else:
        raise ValueError('Integer too large: {}'.format(i))
