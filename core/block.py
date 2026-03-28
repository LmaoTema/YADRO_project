class Block:

    def __init__(self, is_working=True):
        self.is_working = is_working

    def process(self, bits, params=None):
        if not self.is_working:
            if params is not None:
                # Для отключения эквалайзера
                return bits, []
            else:
                return bits
        
        if params is not None:
            return self._process(bits, params)
        else:
            return self._process(bits)

    def _process(self, bits):
        raise NotImplementedError("Block must implement _process")