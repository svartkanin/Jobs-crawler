import pathlib
import json

from bs4 import BeautifulSoup

from .crawler import JobAd


class Neuvoo():
    def __init__(self, config_data):
        path = pathlib.Path(__file__).parent.absolute()
        self._mapping_file = f'{path}/neuvoo_mapping.json'

        self._config_data = config_data
        self._domain = None
        self._url = 'jobs/?k=SEARCH_TERM&l=LOCATION&p=PAGE_NR&date=1d&field=&company=&source_type=&radius=&from=&test=&iam=&is_category=no'

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
        return s.replace(' ', '+')

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
            for page_nr in range(1, 10):
                # html encoding
                term = self._url_encode(term)
                url = (self._url.replace('SEARCH_TERM', term).replace(
                    'LOCATION', location).replace('PAGE_NR', str(page_nr)))
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

        jobDivs = soup.findAll('div', {'class': 'card card__job'})

        jobAds = []

        for jobDiv in jobDivs:
            jobAd = JobAd(self.__class__.__name__)

            titleDiv = (jobDiv.find('div', {
                'class': 'card__job-title'
            }).find('a', {'class': 'card__job-link gojob'}))
            jobAd.link = f'{self._domain}{titleDiv["href"]}'
            jobAd.title = titleDiv.getText()

            locationDiv = jobDiv.find('div', {'class': 'card__job-location'})
            jobAd.location = locationDiv.getText()

            companyDiv = jobDiv.find('div',
                                     {'class': 'card__job-empname-label'})
            jobAd.company = companyDiv.getText()

            jobAds.append(jobAd)

        return jobAds
