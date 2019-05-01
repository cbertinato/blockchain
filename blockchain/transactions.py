import requests

from blockchain.etc import (little_endian_to_int, hash256, read_varint, encode_varint,
                            int_to_little_endian)
from blockchain.script import Script


class FetchError(Exception):
    pass


class Transaction:
    """
    Transaction structure
    ---------------------
    - version (4 bytes)
    - inputs
        - number of inputs (varint)
        - inputs
    - outputs
        - number of outputs (varint)
        - outputs
    - locktime
    """
    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet

    def __repr__(self):
        inputs = '\n'.join(repr(tx_in) for tx_in in self.tx_ins)
        outputs = '\n'.join(repr(tx_out) for tx_out in self.tx_outs)

        return ('Transaction: {}\n'
                'version: {}\n'
                'inputs:\n'
                '{}\n'
                'outputs:\n'
                '{}\n'
                'locktime: {}'.format(self.id(), self.version, inputs, outputs, self.locktime))

    def id(self):
        """ Human-readable hexadecimal of the transaction hash """
        return self.hash().hex()

    def hash(self):
        """ Binary hash of the serialization """
        return hash256(self.serialize())[::-1]

    @classmethod
    def parse(cls, s, testnet=False):
        version = little_endian_to_int(s.read(4))

        # parse inputs
        num_inputs = read_varint(s)
        inputs = []

        for _ in range(num_inputs):
            inputs.append(TransactionInput.parse(s))

        # parse outputs
        num_outputs = read_varint(s)
        outputs = []

        for _ in range(num_outputs):
            outputs.append(TransactionOutput.parse(s))

        locktime = little_endian_to_int(s.read(4))

        return cls(version, inputs, outputs, locktime, testnet)

    def serialize(self):
        result = int_to_little_endian(self.version, 4)

        result += encode_varint(len(self.tx_ins))
        for tx_in in self.tx_ins:
            result += tx_in.serialize()

        result += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            result += tx_out.serialize()

        result += int_to_little_endian(self.locktime, 4)

        return result

    def fee(self):
        """
        The transaction fee is the sum of the inputs minus the sum of the outputs
        """
        input_sum = sum([tx_in.value(testnet=self.testnet) for tx_in in self.tx_ins])
        output_sum = sum([tx_out.amount for tx_out in self.tx_outs])
        return input_sum - output_sum


class TransactionInput:
    """
    Transaction input structure
    ---------------------------
    - previous transaction id: hash256 of previous transaction's contents (32 bytes)
    - previous transaction index (4 bytes)
    - scriptsig
    - sequence (4 bytes)

    NOTE: Note that locktime is ignored if the sequence numbers for every input are ffffffff.
    """
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index

        if script_sig is None:
            self.script_sig = Script()
            pass

        else:
            self.script_sig = script_sig

        self.sequence = sequence

    def __repr__(self):
        return '{}:{}'.format(self.prev_tx.hex(), self.prev_index)

    @classmethod
    def parse(cls, s):
        prev_tx = s.read(32)[::-1]
        prev_index = little_endian_to_int(s.read(4))
        script_sig = Script.parse(s)
        sequence = little_endian_to_int(s.read(4))
        return cls(prev_tx, prev_index, script_sig, sequence)

    def serialize(self):
        result = self.prev_tx[::-1]
        result += int_to_little_endian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += int_to_little_endian(self.sequence, 4)

        return result

    def _fetch_tx(self, testnet=False):
        return TransactionFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False) -> int:
        """ Value in bitcoins of transaction input """
        tx = self._fetch_tx(testnet=testnet)
        return tx.tx_outs[self.prev_index].amount

    def script_pubkey(self, testnet=False) -> Script:
        tx = self._fetch_tx(testnet=testnet)
        return tx.tx_outs[self.prev_index].script_pubkey


class TransactionOutput:
    """
    Transaction output structure
    ----------------------------
    - amount (8 bytes)
    - ScriptPubKey
        - length of script pubkey (varint)
        - Script
    """
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{!r}'.format(self.amount, self.script_pubkey)

    @classmethod
    def parse(cls, s):
        amount = little_endian_to_int(s.read(8))
        script_pubkey = Script.parse(s)

        return cls(amount, script_pubkey)

    def serialize(self):
        result = int_to_little_endian(self.amount, 8)
        result += self.script_pubkey.serialize()

        return result


class TransactionFetcher:
    cache = {}

    @staticmethod
    def get_url(testnet=False):
        if testnet:
            return 'https://api.bitaps.com/btc/testnet/v1/blockchain'
        else:
            return 'https://api.bitaps.com/btc/v1/blockchain'

    @classmethod
    def fetch(cls, tx_id, testnet=False, fresh=False) -> Transaction:
        if fresh or tx_id not in cls.cache:
            url = '{base_url}/transaction/{tx_id}'.format(base_url=cls.get_url(testnet),
                                                          tx_id=tx_id)
            response = requests.get(url)

            if response.status_code != 200:
                raise FetchError(response.text)

            raw_tx = bytes.fromhex(response.json()['data']['rawTx'].strip())
            if raw_tx[4] == 0:
                raw_tx = raw_tx[:4] + raw_tx[6:]
                tx = Transaction.parse(raw_tx, testnet=testnet)
                tx.locktime = little_endian_to_int(raw_tx[-4:])
            else:
                tx = Transaction.parse(raw_tx, testnet=testnet)

            if tx.id() != tx_id:
                raise ValueError('Not the same id: {} vs {}'.format(tx_id, tx.id()))

            cls.cache[tx_id] = tx

        cls.cache[tx_id].testnet = testnet
        return cls.cache[tx_id]
