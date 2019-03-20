import logging
from vlogging import VisualRecord


class Logger(object):
    def __init__(self, logger_name, log_destination):
        # log_dims = open(log_dimension_file)
        self.logger = logging.getLogger(logger_name)
        file_handler = logging.FileHandler(log_destination + '/log.html', mode='w')
        # log_dims.readline().strip())
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def log(self, name, image):
        self.logger.debug(VisualRecord(
            name,
            image,
            fmt='png'
        ))