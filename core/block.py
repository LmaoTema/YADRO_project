class Block:

    def __init__(self, is_working=True):
        self.is_working = is_working

    def process(self, bits):
        if not self.is_working:
            return bits

        return self._process(bits)

    def _process(self, bits):
        raise NotImplementedError("Block must implement _process")