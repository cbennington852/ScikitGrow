import pickle


class Parsel():
    """
    This is a class of things that are savable and loadable to file.
    """

    parsel = None

    def __init__(self):
        # Singleton
        if Parsel.parsel is not None:
            return Parsel.parsel
        self.data = {}
        Parsel.parsel = self

    def add(self , key , thing):
        self.data[key] = thing

    def get(self , key):
        return self.data[key]
    
    def to_pickle(self, file_name):
        try:
            with open(file_name, 'wb') as f:
                pickle.dump(self.data, f)
        except:
            print(f"Failed to read file {file_name}")

    def from_pickle(self , file_name):
        try:
            with open(file_name, 'rb') as f:
                self.data = pickle.load(f)
        except:
            print(f"Failed to read file {file_name}")

    