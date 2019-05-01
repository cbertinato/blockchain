from io import BytesIO

from blockchain.transactions import Transaction
from blockchain.script import Script


def test_parse_transaction():
    raw_tx = ('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b'
              '483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a98'
              '6d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545'
              'de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b'
              '654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e33216'
              '6702cb75f40df79fea1288ac19430600')

    stream = BytesIO(bytes.fromhex(raw_tx))
    tx = Transaction.parse(stream)

    assert tx.version == 1

    assert len(tx.tx_ins) == 1
    assert len(tx.tx_outs) == 2

    assert tx.locktime == 410393

    pk_hash1 = bytes.fromhex('bc3b654dca7e56b04dca18f2566cdaf02e8d9ada')
    assert tx.tx_outs[0].script_pubkey.cmds == Script.p2pkh(pk_hash1).cmds

    pk_hash2 = bytes.fromhex('1c4bc762dd5423e332166702cb75f40df79fea12')
    assert tx.tx_outs[1].script_pubkey.cmds == Script.p2pkh(pk_hash2).cmds
