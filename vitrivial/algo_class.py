from t_logging import TextLogger


class AlgoClass(object):
    def __init__(self):
        self.name = self.__class__.__name__

    def log_text(self, text):
        TextLogger.log_text(text, self.name)
