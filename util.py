from json import loads
from auth_token import auth_token
import logging


def load_config(file_path):
    with open(file_path, mode='r') as file:
        config = loads(file.read())
        config['auth_token'] = auth_token
        return config


def setup_logger(file_path, logger_name='bot'):
    logging.basicConfig(
        format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s',
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(file_path),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(logger_name)