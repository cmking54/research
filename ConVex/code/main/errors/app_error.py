class AppError(Exception):
    def __init__(self, value):
        self.value = value
        # app.exit()

    def __str__(self):
        return repr(self.value)
