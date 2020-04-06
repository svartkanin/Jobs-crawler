import logging
import json
import pathlib

from bs4 import BeautifulSoup

from .crawler import JobAd

logger = logging.getLogger(__name__)


class Monster():
    def __init__(self, config_data):
        path = pathlib.Path(__file__).parent.absolute()
        self._mapping_file = f'{path}/monster_mapping.json'

        self._config_data = config_data
        self._domain = None
        # not entirely sure about the page and total parameters
        # but when using them the page seems to retrieve all jobs
        # without having to resent requests for pagination
        self._url = '?q=SEARCH_TERM&where=LOCATION&page=2&total=100'

    def _get_domain(self):
        """
        Check which domain to use, depending on the country that has
        been specified in the configuration

        Returns:
            TYPE: Description

        Raises:
            ValueError: Description
        """
        country = self._config_data.get('country')
        if country is not None:
            with open(self._mapping_file, 'r') as fp:
                mappings = json.load(fp)
                if mappings.get(country, None) is not None:
                    return mappings.get(country, None)

        raise ValueError(f'Country "{country}" not supported')

    def _url_encode(self, s):
        """
        Encode the string for the url

        Args:
            s (str): String to be encoded

        Returns:
            str: Encoded string
        """
        return s.replace(' ', '-')

    def prepare_urls(self):
        """
        Generate the urls to be crawled

        Returns:
            list: List of urls to be crawled
        """
        self._domain = self._get_domain()

        search_terms = self._config_data['search_terms']
        urls = []

        location = self._url_encode(self._config_data['location'])

        for term in search_terms:
            term = self._url_encode(term)
            url = (self._url.replace('SEARCH_TERM',
                                     term).replace('LOCATION', location))
            urls.append(f'{self._domain}/{url}')

        return urls

    def parse_data(self, page_source):
        """
        Parse the html source code for job ads

        Args:
            page_source (str): Full page source code to be parsed

        Returns:
            list: List of job ads found on in the source
        """
        soup = BeautifulSoup(page_source, 'html.parser')

        jobAds = []
        sections = soup.find('div', {'class': 'mux-card mux-job-card'})
        jobDivs = sections.findAll('section', {'class': 'card-content'})

        for jobDiv in jobDivs:
            jobAd = JobAd(self.__class__.__name__)

            titleDiv = jobDiv.find('h2', {'class': 'title'})

            if titleDiv is None:
                continue

            titleDiv = titleDiv.find('a')

            jobAd.title = titleDiv.getText().strip()
            jobAd.link = f'{titleDiv["href"]}'

            locationDiv = jobDiv.find('div', {'class': 'location'})
            jobAd.location = locationDiv.getText().strip()

            companyDiv = jobDiv.find('div', {'class': 'company'})
            jobAd.company = companyDiv.getText().strip()

            jobAds.append(jobAd)

        return jobAds
