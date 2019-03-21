"""Provides the methods used for parsing HTML"""

import urllib3
import certifi
from utility import get_logger

HTTP = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
LOGGER = get_logger('parser')


def get_page_html(url):
    """Obtains the HTML from a URL.

    Returns the raw HTML for a given web page URL.

    Parameters
    ----------
    url: str
        The URL of the web page that should be downloaded.

    Returns
    -------
    HTML
        The raw HTML of the downloaded webpage.
    """
    try:
        request = HTTP.request('GET', url)
        if request.status == 200:
            return request.data
        LOGGER.debug('ParserError: The request failed for %s', url)
        return None
    except:
        LOGGER.debug('SSLError for %s', url)
