class Pipeline:

    def __init__(self, blocks):
        self.blocks = blocks

    def run(self, data):

        for block in self.blocks:
            data = block.process(data)

        return data