#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 3.6
# @Filename:    college_scraper.py
# @Author:      Samuel Hill
# @Email:       samuelhill2022@u.northwestern.edu
# @Date:        2019-03-10 17:10:37
# @Last Modified by:    Samuel Hill
# @Last Modified time:  2019-03-22 04:28:56

"""
Scrapes college data from the web, knows about all the colleges that there are.
"""

# IMPORTS
import string
import os
import pickle
from requests_html import HTMLSession

# MODULE AUTHORSHIP INFO
__author__ = "Samuel Hill"
__copyright__ = "Copyright 2019, Samuel Hill."
__credits__ = ["Samuel Hill"]


# CLASSES
class CollegeScraper(object):
    """Uses an internal dictionary to store every college name (as well as a
    special unique id for later identification and the url the fact was
    gathered from for later reference). Scrapes the table of college names
    found at the index#.htm pages (on the base url listed in the CollegeScraper
    class) to get every table entry (specified by the xpath string) and saves
    these names to the internal dict. This dictionary can be pickled for later
    use, and the class can load a pickle file into the dictionary so this class
    can be used as a dictionary of colleges without needing to scrape the data
    from the web, fresh on every usage. The data can also be saved as a krf
    file and the object has a string representation that is used as the
    contents of the krf. This tactic is not so pythonic in that we avoid
    defining repr (as it isn't important for our use of objects) but the ease
    of using the scraper as the knowledge itself (passing it around like a
    string) is beneficial and more important than that norm."""

    def __init__(self, session=None):
        super(CollegeScraper, self).__init__()
        self.session = session if session is not None else HTMLSession()
        self.BASE_URL = 'https://www.4icu.org/reviews/index'
        self.colleges_dict = {}

    def __str__(self):
        ontologized = '(in-microtheory CollegeNamesMt)\n'
        horn = '(<== {0}\n\t(reportSources-Prop {0}\n\t(URLFn "{1}")))\n'
        report = '(reportSources-Prop {0}\n\t(URLFn "{1}"))\n'
        for _, college in self.colleges_dict.items():
            isa = '(isa {} {})'.format(college['id'], 'College')
            ontologized += horn.format(isa, college['url'])
            ontologized += report.format(isa, college['url'])
            quoted_name = '"{}"'.format(college['name'].strip())
            args = ' '.join([college['id'], quoted_name])
            ontologized += '({} {})\n\n'.format('prettyString', args)
        return ontologized.strip()

    def no_newline_string(self):
        ontologized = '(in-microtheory CollegeNamesMt)\n'
        horn = '(<== {0}(reportSources-Prop {0}(URLFn "{1}")))\n'
        report = '(reportSources-Prop {0}(URLFn "{1}"))\n'
        for _, college in self.colleges_dict.items():
            isa = '(isa {} {})'.format(college['id'], 'College')
            ontologized += horn.format(isa, college['url'])
            ontologized += report.format(isa, college['url'])
            quoted_name = '"{}"'.format(college['name'].strip())
            args = ' '.join([college['id'], quoted_name])
            ontologized += '({} {})\n'.format('prettyString', args)
        return ontologized.strip()

    def scrape(self):
        """Modifies the internal dictionary of colleges by scraping all pages
        from the master list (specified by base_url + page numbers up to 28)
        and adding the college name, unique id, and assoc. url to the
        dictionary of all colleges.
        """
        urls = ['{}{}{}'.format(self.BASE_URL, i, '.htm') for i in range(28)]
        count = 0
        for url in urls:
            content = self.session.get(url).html
            table_row_location = '//tbody/tr/td/a[@href]/text()'
            for i, college in enumerate(content.xpath(table_row_location)):
                self.colleges_dict[count] = {'id': self.make_unique(college),
                                             'name': college,
                                             'url': url}
                count += 1

    def to_krf(self):
        """Outputs the internal college data (as a string) to the filename
        specified in a path relative to where this program was called from."""
        real_dir = os.path.dirname(os.path.realpath(__file__))
        with open('{0}/{1}'.format(real_dir, 'colleges.krf'), 'w+') as outfile:
            outfile.write(str(self))

    def to_pickle(self):
        """Pickles the colleges_dict into a compressed binary file for easy
        reading in by other python programs."""
        with open('colleges.pickle', 'wb') as outfile:
            pickle.dump(self.colleges_dict, outfile)

    def from_pickle(self):
        """Reads the previously pickled scraped college data back in as if the
        data was scraped again."""
        with open('colleges.pickle', 'rb') as data_file:
            self.colleges_dict = pickle.load(data_file)

    @staticmethod
    def make_unique(to_print):
        """Takes a string and removes all 'unfriendly' - not printable -
        characters and punctuation, then returns that string without whitespace

        Args:
            to_print (string): string with punctuation, whitespace, and non-
                printable letters (like those outside utf-8).

        Returns:
            string: clean string without 'bad' chars, punctation, or spaces
        """
        filtered = ''.join([x for x in to_print if x in set(string.printable)])
        no_punc = filtered.translate(str.maketrans('', '', string.punctuation))
        return no_punc.replace(' ', '')


if __name__ == '__main__':  # code to execute if called from command-line
    CS = CollegeScraper()
    # CS.scrape()
    # CS.to_pickle()
    # CS.to_krf()
    CS.from_pickle()
    print(CS)
    # for i in range(len(CS.colleges_dict)):
    #     print(CS.colleges_dict[i]['name'])
