from blockchain.script import Script
from blockchain.op import OP_CODE_NAMES
from blockchain.etc import hash160


def test_p2pk():
    z = 0x7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d
    sec = bytes.fromhex('04887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c6'
                        '1de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34')

    sig = bytes.fromhex('3045022000eff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe'
                        '0529a2c022100c7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fd'
                        'dbdce6feab601')

    script_pubkey = Script([sec, b'\xac'])
    script_sig = Script([sig])
    combined_script = script_sig + script_pubkey

    assert combined_script.evaluate(z)


def test_p2pkh_constructor():
    pub_key = bytes.fromhex('04887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c6'
                            '1de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34')
    pk_hash = hash160(pub_key)
    expected = [OP_CODE_NAMES['OP_DUP'], OP_CODE_NAMES['OP_HASH160'], pk_hash,
                OP_CODE_NAMES['OP_EQUALVERIFY'], OP_CODE_NAMES['OP_CHECKSIG']]

    result = Script.p2pkh(pk_hash).cmds

    assert result == expected
