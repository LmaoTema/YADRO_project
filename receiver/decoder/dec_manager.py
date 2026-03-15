from core.block import Block
from receiver.decoder.dec_tch import TCHFSSpeechDecoder

class ChannelDecoder(Block):
    def __init__(self, scheme, is_working=True):
        super().__init__(is_working)
        
        if scheme == "TCHFS":
            self.decoder = TCHFSSpeechDecoder()  
        elif scheme == "CS1":
            self.decoder = CS1BlockDecoder()


    def _process(self, bits):
        return self.decoder.process(bits)