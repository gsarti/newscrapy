"""Extractor base and child classes.

This module defines the Extractor abstract base class alongside with
many specific classes used to extract articles from many newspapers
of interest.

Supported newspapers in alphabetical order:

La Repubblica (LaRepubblicaExtractor)

"""

import re
import abc
from parser import get_page_html
from datetime import date, timedelta
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from article import ArticleException, LaRepubblicaArticle
from utility import datespan, get_logger

LOGGER = get_logger('extractor')


class ExtractorException(Exception):
    """Custom exception for the Extractor class.

    Attributes
    ----------
    msg: str
        Human readable string describing the exception.

    """
    def __init__(self, msg):
        """Initializer for the ExtractorException class.

        Parameters
        ----------
        msg: str
            Human readable string describing the exception.

        """
        super().__init__(msg)
        self.msg = msg


class Extractor(abc.ABC):
    """Abstract Extractor base class.

    Base class for the specialized extractors for each newspaper.
    The method to export articles to CSV format is defined, while
    those to extract articles and archive sizes should be redefined
    in child classes.

    Attributes
    ----------
    articles: list of Article objects
        A list of all the articles extracted by the extractor.

    """
    def __init__(self):
        self.articles = []

    @abc.abstractmethod
    def archive_size(self, day, month, year):
        """The archive size for date.

        Returns the total number of pages in the archive of the
        newspaper for the specified date.

        Parameters
        ----------
        day: int
            The day of the date for which the number of archive
            pages should be found.
        month: int
            The month of the date for which the number of archive
            pages should be found.
        year: int
            The year of the date for which the number of archive
            pages should be found.

        Returns
        -------
        int
            The total number of pages in the archive for the date.

        """
        pass

    @abc.abstractmethod
    def extract_articles(self, day, month, year, page_num=None,
                         day_end=None, month_end=None, year_end=None):
        """Extract newspaper articles multimodally based on parameters.

        If only day, month and year are passed as parameters, the method
        extracts all articles from newspaper archives for day-month-year date.

        If page_num is specified, the method extracts all articles from the
        specified newspaper archive page for the specified day-month-year date.

        If day_end, month_end and year_end are specified, the method extracts
        all articles from newspaper archives between the first and last date.

        Parameters
        ----------
        day: int
            The day of publication of the articles that should be extracted,
            or the first day of publication of the articles that should be
            extracted.
        month: int
            The month of publication of the articles that should be extracted,
            or the first month of publication of the articles that should be
            extracted.
        year: int
            The year of publication of the articles that should be extracted,
            or the first year of publication of the articles that should be
            extracted.
        page_num: int, optional
            The page number from which articles should be extracted.
        day_end: int, optional
            The last day of publication of the articles that should be
            extracted.
        month_end: int, optional
            The last month of publication of the articles that should be
            extracted.
        year_end: int, optional
            The last year of publication of the articles that should be
            extracted.

        Returns
        -------
        void
            Fills the article attribute of the class.

        """
        pass

    def articles_to_csv(self, filename):
        """Writes extracted articles to a CSV file.

        The column names are respectively:
        url, title, description, authors, publish_date, text, section,
        subsection, keywords, characters, image_url.

        Parameters
        ----------
        filename: str
            The name of the file to which the articles should be saved
            (e.g. "articles.csv").

        Returns
        -------
        void
            Produces a csv file in the current folder.

        """
        data = pd.DataFrame.from_records(
            [article.as_dict() for article in self.articles])
        data.to_csv(filename)


class LaRepubblicaExtractor(Extractor):
    """A specialized extractor for La Repubblica articles

    The extractor methods are based on the La Repubblica archives structure,
    which can be found here:
        https://ricerca.repubblica.it/repubblica/archivio/repubblica

    The class has no specific attributes with respect to the abstract base
    class, since the latter was modeled based on the former in the first place.

    Notes
    -----
    La Repubblica first entry in the archive is on January 1st, 1984. However,
    since archived articles structure is highly inconsistent, this extractor is
    not guaranteed to work for all articles. For the moment, it was tested for
    articles after March 4th, 2015.
    """

    def archive_size(self, day, month, year):
        """La Repubblica archive size for date.

        Returns the total number of La Repubblica archive pages
        for the specified date. See Extractor base method docstring
        for more information about parameters and return.

        """
        data = get_page_html(
            'http://ricerca.repubblica.it/repubblica/archivio/' \
            'repubblica/%d/%d/%d?page=1' % (year, month, day))
        if data is None:
            return -1
        soup = BeautifulSoup(data, 'html.parser')
        pagination = soup.find('div', {"class": "pagination"})
        tot_pages = int(re.findall(r'\d+', pagination.p.text)[-1])
        return tot_pages

    def extract_articles(self, day, month, year, page_num=None,
                         day_end=None, month_end=None, year_end=None):
        """Extract articles multimodally for La Repubblica newspaper.

        See Extractor base method docstring for more information about
        modes of use, parameters and return.

        Notes
        -----
        We exclude:
            La Repubblica TV, caricatures and photo articles identified by span.
            Il Cruciverba (crosswords) articles.
            Searches, identified by html?ref=search.
            Private content for paying users articles from Catalogo generale.
            Articles with empty preview (usually empty placeholders).
        """
        if page_num is not None:
            data = get_page_html(
                'http://ricerca.repubblica.it/repubblica/archivio/' \
                'repubblica/%d/%d/%d?page=%d' % (year, month, day, page_num))
            if data is None:
                return
            soup = BeautifulSoup(data, 'html.parser')
            articles_html = soup.find_all("article")
            for art_html in articles_html:
                if (art_html.p.span is None and
                        art_html.span.text[5:] != 'Il Cruciverba' and
                        art_html.a['href'][-16:] != '.html?ref=search' and
                        art_html.a['href'] != 'https://quotidiano.repubblica'
                        '.it/edicola/catalogogenerale.jsp?ref=search' and
                        art_html.p is not None and
                        len(art_html.p.text) > 5):
                    try:
                        article = LaRepubblicaArticle(art_html.a['href'])
                        article.download()
                        article.parse(art_html)
                        self.articles.append(article)
                    except ArticleException as ex:
                        LOGGER.debug(ex.msg)
        elif all(v is not None for v in [day_end, month_end, year_end]):
            for curr in datespan(date(year, month, day),
                                 date(year_end, month_end, day_end),
                                 delta=timedelta(days=1)):
                self.extract_articles(curr.day, curr.month, curr.year)
        else:
            pages = self.archive_size(day, month, year)
            LOGGER.info('Extracting articles for %d-%d-%d...', day, month, year)
            for i in tqdm(range(1, pages + 1)):
                self.extract_articles(day, month, year, page_num=i)
