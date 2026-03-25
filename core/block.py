class Block:

    def __init__(self, is_working=True):
        self.is_working = is_working

    def process(self, bits, tx_bits=False):
        if not self.is_working:
                return bits
        
        if tx_bits is not False:
            return self._process(bits, tx_bits)
        else:
            return self._process(bits)

    def _process(self, bits):
        raise NotImplementedError("Block must implement _process")