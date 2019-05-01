import io

import pytest

import blockchain.etc as etc


@pytest.mark.parametrize('test_input,expected', [
    ('7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d',
     '9MA8fRQrT4u8Zj8ZRd6MAiiyaxb2Y1CMpvVkHQu5hVM6'),
    ('eff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c',
     '4fE3H2E6XMp4SsxtwinF7w9a34ooUrwWe4WsW1458Pd'),
    ('c7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab6',
     'EQJsjkd6JaGwxrjEhfeqPenqHwrBmPQZjJGNSCHBkcF7')
])
def test_encode_base58(test_input, expected):
    result = etc.encode_base58(bytes.fromhex(test_input))
    assert result == expected


@pytest.mark.parametrize('test_input,expected', [
    ('mzx5YhAH9kNHtcN481u6WkjeHjYtVeKVh2', 'd52ad7ca9b3d096a38e752c2018e6fbc40cdf26f'),
    ('mnrVtF8DWjMu839VW3rBfgYaAfKk8983Xf', '507b27411ccf7f16f10297de6cef3f291623eddf')
])
def test_decode_base58(test_input, expected):
    result = etc.decode_base58(test_input)
    assert result == bytes.fromhex(expected)


@pytest.mark.parametrize('test_input,expected', [
    (int.to_bytes(200, 1, 'little'), 200),
    (b'\xfd' + int.to_bytes(300, 2, 'little'), 300),
    (b'\xfe' + int.to_bytes(2**17, 4, 'little'), 2**17),
    (b'\xff' + int.to_bytes(2**33, 8, 'little'), 2**33)
])
def test_read_varint(test_input, expected):
    stream = io.BytesIO(test_input)
    result = etc.read_varint(stream)

    assert result == expected
