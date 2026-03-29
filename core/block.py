class Block:

    def __init__(self, is_working=True):
        self.is_working = is_working

    def process(self, *args):
        if not self.is_working:
            if len(args) == 1:
                return args[0]
            else:
                return args

        return self._process(*args)
    
    def _process(self, *args):
        raise NotImplementedError("Block must implement _process")