"""Article base and child classes.

This module defines the Article abstract base class alongside with
many specific classes used to store articles scraped from various
newspapers of interest.

Supported newspaper in alphabetical order:

La Repubblica (LaRepubblicaArticle)

"""

import abc
from parser import get_page_html
from bs4 import BeautifulSoup
from utility import get_logger

LOGGER = get_logger('article')


class ArticleException(Exception):
    """Custom exception for the Article class.

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


class Article(abc.ABC):
    """Abstract Article base class.

    Base class for newspaper articles. Download method is standard,
    while parse and as_dict must be redefined in child classes.

    Attributes
    ----------
    url: str
        The URL at which the article can be found.
    title: str
        The title of the article.
    description: str
        Article's summary/incipit.
    authors: str
        The article's authors names.
    publish_date: str
        The date of publishing.
    text: string
        The whole text contained in the article.
    section: str
        The name of the newspaper section containing the article.
    subsection: str
        The name of the newspaper subsection containing the article.
    keywords: list of str
        A list of keywords used to identify article's topics.
    characters: list of str
        A list of characters presented or discussed in the article.
    image_url: str
        The URL of the top image contained in the article.
    html: HTML
        The raw HTML extracted from the article webpage.

    """
    def __init__(self, url):
        """Initializer for the Article class.

        Parameters
        ----------
        url: str
            The URL at which the article can be found.

        """
        if url is None or url == '':
            raise ArticleException('ArticleException: Invalid URL')
        self.url = url
        self.title = ''
        self.description = ''
        self.authors = ''
        self.publish_date = ''
        self.text = ''
        self.section = ''
        self.subsection = ''
        self.keywords = []
        self.characters = []
        self.image_url = ''
        self.html = ''

    @abc.abstractmethod
    def as_dict(self):
        """Dictionary containing Article attributes.

        Returns
        -------
        dict
            A dictionary with all attributes specified in the child class.
        """
        pass

    def download(self):
        """Gets the article HTML

        Saves the article HTML inside the html attribute.

        Returns
        -------
        void
            Fills the html attribute of the class.
        """
        html = get_page_html(self.url)
        if html is not None and html != '':
            self.html = html
        else:
            raise ArticleException('ArticleException: Article HTML is empty.')

    @abc.abstractmethod
    def parse(self, preview_soup=''):
        """Parse article from stored html.

        Parses the content of the article from the html stored by using download,
        filling the attributes of the Article object following the rules specified
        in the child class.

        The methods allows for preemptive extraction of article preview in the archive,
        in order to extract more structured and reliable information.

        Parameters
        ----------
        preview_soup: BeautifulSoup
            The BeautifulSoup object containing the HTML of article preview
            inside the archive.
        """
        pass


class LaRepubblicaArticle(Article):
    """A specialized text article extracted from La Repubblica newspaper.

    Notes
    -----
    The parse method is based on the La Repubblica article structure, which is
    highly inconsistent over time.

    """
    def __init__(self, url):
        """Initializer for the LaRepubblicaArticle class.

        Filters out unnecessary search query after url.

        Parameters
        ----------
        url: str
            The URL at which the article can be found.

        """
        super().__init__(url)
        self.url = url[:-10]

    def as_dict(self):
        """Dictionary containing Article attributes.

        The html attribute was excluded since deemed useless for our purposes
        and too heavy to be stored easily in high quantity.

        Returns
        -------
        dict
            A dictionary with all attributes specified in the child class.

        """
        return {
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'authors': self.authors,
            'publish_date': self.publish_date,
            'text': self.text,
            'section': self.section,
            'subsection': self.subsection,
            'keywords': self.keywords,
            'characters': self.characters,
            'image_url': self.image_url
        }

    def parse(self, preview_soup=''):
        """Parse method for La Repubblica articles

        See Article base method docstring for more information about parameters
        and return. Performs trial-and-error until all fields are filled, if possible.
        Rules come from an empyrical study of extraction errors and since the newspaper
        structure is a mess, many are probably still missing. Don't hesitate to add
        new ones.

        """
        try:
            soup = BeautifulSoup(self.html, 'html.parser')

            # Title
            self.title = soup.article.h1.text

            # Description
            description = soup.find('p', {'itemprop': 'description'})
            if description is not None:
                self.description = description.text
            elif preview_soup != '':
                description = preview_soup.p

            # Authors
            authors = soup.find('em', {'itemprop': 'author'})
            if authors is not None:
                self.authors = authors.text
            elif preview_soup != '':
                authors = preview_soup.find('em', {'class': 'author'})

            # Date
            if preview_soup != '':
                self.publish_date = preview_soup.find('time').text
            else:
                self.publish_date = soup.find('time', {'itemprop': 'datePublished'}).text

            # Text
            article_body = soup.find('span', {'itemprop': 'articleBody'})
            if article_body is None:
                article_body = soup.find('div', {'class': 'detail_body'})
            if article_body is None:
                article_body = soup.find('div',
                                         {'class': 'body-text'}).find('div',
                                                                      {'class': 'content'}).p
            if article_body is not None:
                self.text = article_body.text

            # Section
            section_logo = soup.find('a', {'class': 'section-logo'})
            sport_logo = soup.find('a', {'class': 'sport-logo'})
            if section_logo is not None:
                self.section = section_logo.text
            elif sport_logo is not None:
                self.section = sport_logo.text

            # Subsection
            if preview_soup != '':
                self.subsection = preview_soup.span.text[5:]

            # Keywords
            keywords = soup.find('dl', {'class': 'args'})
            if keywords is None:
                keywords = soup.find('div', {'class': 'detail_tag'})
                if keywords is not None:
                    for keyword in keywords.find_all('a'):
                        self.keywords.append(keyword.text)
            else:
                for keyword in keywords.find_all('dd'):
                    self.keywords.append(keyword.text)

            # Characters
            characters = soup.find('dl', {'class': 'character'})
            if characters is not None:
                for character in characters.find_all('dd'):
                    self.characters.append(character.text)

            # Image
            image = soup.figure
            if image is not None and image.img is not None:
                self.image_url = soup.figure.img['src']
        except:
            raise ArticleException('Error: Invalid parsing of article' \
                                   '"%s" (%s)' % (self.title, self.url))
