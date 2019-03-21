""" Allows for quick article extraction in console """

import sys
from extractor import ExtractorException, LaRepubblicaExtractor


def choose_extractor(newspaper_name):
    """Factory method for choosing the right extractor.

    Factory design pattern used to choose the correct extractor
    to be used given the newspaper name.

    Supported names in alphabetic order:
        LaRepubblica (La Repubblica)

    Parameters
    ----------
    newspaper_name: str
        The name of the newspaper from which we want to extract articles.
    """
    if newspaper_name == 'LaRepubblica':
        return LaRepubblicaExtractor()
    return None


def run():
    """ Script to perform article extraction """
    arg_len = len(sys.argv)
    if arg_len not in [6, 7, 9]:
        print(
            """
            Error: Insufficient number of arguments: %d.\n
            Use one of the following syntaxes:
            * To extract all articles from a newspaper for a specific day:
                main.py filename newspaper_name day month year
            * To extract all article in a specific archive page
              of a newspaper for a specific day:
                main.py filename newspaper_name day month year page_num
            * To extract all articles from a newspaper between two dates:
                main.py filename newspaper_name day month year day_end month_end year_end
            With parameters:
                filename: The name of the file in which extracted articles will be saved.
                newspaper_name: The name of the newspaper.
                   Now supported: 'LaRepubblica'
                day: The day of extraction.
                month: The month of extraction.
                year: The year of extraction.
                page_num: The number of archive page.
                day_end: The last day of extraction.
                month_end: The last month of extraction.
                year: The last year of extraction.
            """ % arg_len)
        return
    filename = sys.argv[1]
    newspaper = sys.argv[2]
    extractor = choose_extractor(newspaper)
    if extractor is None:
        raise ExtractorException('ExtractorException: Selected newspaper' \
                                 'is not supported (yet!)')
    day = int(sys.argv[3])
    month = int(sys.argv[4])
    year = int(sys.argv[5])
    if arg_len == 6:
        extractor.extract_articles(day, month, year)
    elif arg_len == 7:
        page_num = int(sys.argv[6])
        extractor.extract_articles(day, month, year, page_num=page_num)
    elif arg_len == 9:
        day_end = int(sys.argv[6])
        month_end = int(sys.argv[7])
        year_end = int(sys.argv[8])
        extractor.extract_articles(day, month, year,
                                   day_end=day_end, month_end=month_end, year_end=year_end)
    extractor.articles_to_csv(filename)
    print("The request was completed.")

if __name__ == '__main__':
    run()
