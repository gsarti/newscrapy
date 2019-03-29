# Newscrapy [![Build Status](https://travis-ci.org/gsarti/newscrapy.svg?branch=master)](https://travis-ci.org/gsarti/newscrapy)

## Batch scrape articles from online newspaper archives

### A quick overview

The purpose of this tool is to enable quick and precise extractions of large sets of newspaper articles from online archives, to enable various language-related tasks. See the [Motivation behind the project](#motivation-behind-the-project) section for more info.

**News:**

* [La Repubblica](repubblica.it) news scraping is up and running!

### Setup

The dependencies of the project are the following:

```
Python 3.5 or higher

Certifi (for web certificates)
Urllib3 (to perform web requests)
tqdm (for progress bars in console)
BeautifulSoup (for scraping)
```

Simply run `pip install -r requirements.txt` to install all the dependencies automatically.

### How to use

As for now, three modes of execution are supported:

* `python run.py filename newspaper_name day month year` will generate a CSV file named `filename` containing all articles scraped from newspaper `ǹewspaper_name`'s archives for date `day/month/year`.

* `python run.py filename newspaper_name day month year page_num` does the same, but for a specific page of the archives of that day.

* `python run.py filename newspaper_name day month year day_end month_end year_end` is like the first command, but extract all articles in between `day/month/year` and `day_end/month_end/year_end`.

Examples:

```bash
# Scrapes all articles published on March 8, 2019 on
# La Repubblica and saves them in 8-march-articles.csv.
python run.py 8-march-articles.csv LaRepubblica 8 3 2019

# Scrapes all articles in the second page of March 8, 2019 archives
# of La Repubblica and saves them in 8-march-articles.csv.
python run.py 8-march-page-2-articles.csv LaRepubblica 8 3 2019 2

# Scrapes all articles published in March 2019 on
# La Repubblica and saves them in march-articles.csv.
python run.py march-articles.csv LaRepubblica 1 3 2019 1 4 2019
```

### Motivation behind the project

While very effective article scraping tools already exist (most notably the [Newspaper3k](https://github.com/codelucas/newspaper) library by codelucas), they are mostly specialized in the scraping of single articles, using general scraping directives that generally perform well, but often cannot harvest all the different metadata from all media websites in a precise way.

In this sense, Newscrapy provides an easily-customizable interface to perform ad-hoc article scraping: by creating new `Article` and `Extractor` child classes for a specific newspaper, one can specify how articles of the latter should be extracted from its archives and which peculiar information should be retained from them.

**Currently supported:**

<img src="images/larepubblicait.png" style="width:300px"/>

[Contribute and add yours!](https://github.com/gsarti/newscrapy/pulls)
