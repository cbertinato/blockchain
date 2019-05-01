from blockchain.crypto import PrivateKeyS256, G_S256, Signature


def test_sec_s256_uncompressed():
    secret = 5000
    private_key = PrivateKeyS256(secret)
    assert private_key.point == secret * G_S256

    result = private_key.point.sec(compressed=False).hex()
    expected = ('04ffe558e388852f0120e46af2d1b370f85854a8eb0841811ece0e3e03d282d57c315dc72890'
                'a4f10a1481c031b03b351b0dc79901ca18a00cf009dbdb157a1d10')

    assert result == expected


def test_sec_s256_compressed():
    secret = 5001
    private_key = PrivateKeyS256(secret)
    assert private_key.point == secret * G_S256

    result = private_key.point.sec(compressed=True).hex()
    expected = '0357a4f368868a8a6d572991e484e664810ff14c05c0fa023275251151fe0e53d1'

    assert result == expected


def test_sig_der_serialize():
    r = 0x37206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c6
    s = 0x8ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec

    sig = Signature(r, s)
    result = sig.der().hex()

    expected = ('3045022037206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c602210'
                '08ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec')
    assert result == expected


def test_sig_der_parse():
    der_signature = bytes.fromhex('3045022037206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d28'
                                  '2047a7c60221008ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c8'
                                  '41c8e2738cdaec')

    sig = Signature.parse(der_signature)

    expected_r = 0x37206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c6
    expected_s = 0x8ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec

    assert sig.r == expected_r
    assert sig.s == expected_s
