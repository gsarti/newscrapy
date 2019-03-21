"""Utility methods used for various purposes inside the project"""

from datetime import timedelta
import logging


def datespan(start_date, end_date, delta=timedelta(days=1)):
    """Iterates over each day comprised in the datespan.

    Parameters
    ----------
    start_date: date
        The first day to be returned.
    end_date: date
        The day after the last one that should be returned.
    delta: timedelta
        The step of the generator.

    Returns
    -------
    date
        The currently yelded date.
    """
    current_date = start_date
    while current_date < end_date:
        yield current_date
        current_date += delta


def get_logger(module_name):
    """Generates a logger for each module of the project.

    By default, the logger logs debug-level information into a
    newscrapy.log file and info-level information in console.

    Parameters
    ----------
    module_name: str
        The name of the module for which the logger should
        be generated, in snakecase.

    Returns
    -------
    Logger
        A logger for a specific module.
    """
    logger = logging.getLogger('%s_logger' % (module_name))
    file_handler = logging.FileHandler('newscrapy.log')
    console_handler = logging.StreamHandler()
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                       '%(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(message)s')
    logger.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
