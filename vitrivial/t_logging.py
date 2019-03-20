class TextLogger(object):
    all_logs = []
    logs_by_origin = {}

    def __init__(self):
        pass

    @staticmethod
    def log_text(text, origin):
        # TODO: add tickets/ enumerate the lines to have order
        TextLogger.all_logs += [text]
        if origin in TextLogger.logs_by_origin:
            TextLogger.logs_by_origin[origin] += [text]
        else:
            TextLogger.logs_by_origin[origin] = [text]

    @staticmethod
    def dump_text(dest=None):
        if dest is None:
            print
            for log in TextLogger.all_logs:
                print log
        else:
            # file storage
            save_locale = open(dest, 'w')
            save_locale.writelines(TextLogger.all_logs)

    @staticmethod
    def dump_text_by_origin(dest=None):
        def dump(text):
            print text if dest is None else save_locale.write(text)

        # save_locale = None
        if dest is not None:
            save_locale = open(dest, 'w')
        else:
            print
        for origin in TextLogger.logs_by_origin:
            dump(origin)
            for log in TextLogger.logs_by_origin[origin]:
                dump('\t' + log)
