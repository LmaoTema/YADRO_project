from .tch_fs import TCHFSBlockCoder
from .cs1 import CS1BlockCoder
from .msc1 import MSC1Coding
from .msc5 import MSC5Coding
from core.block import Block


    # main class for channnel coding logic
class ChannelCoder(Block):

    def __init__(self, scheme):

        if scheme == "TCHFS":

            self.coder = TCHFSBlockCoder()

        elif scheme == "CS1":

            self.coder = CS1BlockCoder()

        elif scheme in ["MCS1"]:

            self.coder = MSC1Coding(scheme)
            
        elif scheme in ["MCS5"]:
            
            self.coder = MSC5Coding(scheme)
            
        else:

            raise ValueError("Unknown scheme")

    def process(self, bits):

        return self.coder.process(bits)