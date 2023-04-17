class Logger:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'w')
        self.file.write('')

    @staticmethod
    def log(self, text,*args, **kwargs):
        self.file.write(text)