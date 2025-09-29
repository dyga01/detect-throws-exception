"""In this file we show an exception handling method that is implemented wrong"""



class NoExcept:
    def __init__(self, file):
        self.file = file

    def openFile(self):
        """Opening file."""

        with open(self.file, "r") as fn:
            try:
                fn.read()
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Could not open {self.file}") from e
