class recordWriter(object):
    def __init__(self, filename):
        self.outputs = []
        self.filename = filename

    def add(self, output):
        self.outputs.append(output)

    def write(self, mode):
        with open(self.filename, mode=mode) as output:
            output.write("\n".join(self.outputs))