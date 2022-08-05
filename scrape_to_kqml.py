#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 3.6
# @Filename:    scrape_to_kqml.py
# @Author:      Samuel Hill
# @Email:       samuelhill2022@u.northwestern.edu
# @Date:        2019-03-02 23:35:41
# @Last Modified by:    Samuel Hill
# @Last Modified time:  2019-03-22 06:19:21

"""
Integration of web scraping 'modules' and basic pythonian inserts to have an
easy hook up to companions for delivering web data.
"""

# IMPORTS
from pythonian import Pythonian
from college_scraper import CollegeScraper
from faculty_scraper import FacultyScraper, NorthwesternFaculty
from events_scraper import EventScraper, NorthwesternEvents

# MODULE AUTHORSHIP INFO
__author__ = "Samuel Hill"
__copyright__ = "Copyright 2019, Samuel Hill."
__credits__ = ["Samuel Hill"]


# CLASSES
class ScraperAgent(Pythonian):
    """docstring for ScraperAgent"""
    name = "TestAgent"  # This is the name of the agent to register with

    def __init__(self, **kwargs):
        super(ScraperAgent, self).__init__(**kwargs)
        self.add_achieve('scrape_achieve', self.scrape_achieve)
        self.SCRAPE_FLAG = False
        self.PICKLE_FLAG = False
        self.KRF_FLAG = False
        self.LOAD_FLAG = False
        self.COLLEGE_FLAG = False
        self.FACULTY_FLAG = False
        self.EVENTS_FLAG = False

    def set_option_flags(self, scrape, pickle, krf, load):
        self.SCRAPE_FLAG = scrape
        self.PICKLE_FLAG = pickle
        self.KRF_FLAG = krf
        self.LOAD_FLAG = load

    def set_data_types_flags(self, college, faculty, event):
        self.COLLEGE_FLAG = college
        self.FACULTY_FLAG = faculty
        self.EVENTS_FLAG = event

    def parse_flags(self, options, data_types):
        if str(options) == 'scrape':
            self.set_option_flags(True, False, False, False)
        elif str(options) == 'pickle':
            self.set_option_flags(True, True, False, False)
        elif str(options) == 'krf':
            self.set_option_flags(True, False, True, False)
        elif str(options) == 'saveScrape':
            self.set_option_flags(True, True, True, False)
        elif str(options) == 'load':
            self.set_option_flags(False, False, False, True)
        if str(data_types) == 'all':
            self.set_data_types_flags(True, True, True)
        elif str(data_types) == 'college':
            self.set_data_types_flags(True, False, False)
        elif str(data_types) == 'faculty':
            self.set_data_types_flags(False, True, False)
        elif str(data_types) == 'events':
            self.set_data_types_flags(False, False, True)

    def scrape_achieve(self, options, data_types):
        self.parse_flags(options, data_types)
        if self.FACULTY_FLAG:
            nu_fac = NorthwesternFaculty()
        if self.EVENTS_FLAG:
            nu_event = NorthwesternEvents()
        if self.COLLEGE_FLAG:
            colleges = CollegeScraper()
        if self.SCRAPE_FLAG:
            if self.FACULTY_FLAG:
                nu_fac.scrape_all()
            if self.EVENTS_FLAG:
                nu_event.scrape_num_weeks()
            if self.COLLEGE_FLAG:
                colleges.scrape()
        if self.PICKLE_FLAG:
            if self.FACULTY_FLAG:
                nu_fac.to_pickle()
            if self.EVENTS_FLAG:
                nu_event.to_pickle()
            if self.COLLEGE_FLAG:
                colleges.to_pickle()
        if self.KRF_FLAG:
            if self.FACULTY_FLAG:
                nu_fac.to_krf()
            if self.EVENTS_FLAG:
                nu_event.to_krf()
            if self.COLLEGE_FLAG:
                colleges.to_krf()
        if self.LOAD_FLAG:
            if self.FACULTY_FLAG:
                nu_fac.from_pickle()
            if self.EVENTS_FLAG:
                nu_event.from_pickle()
            if self.COLLEGE_FLAG:
                colleges.from_pickle()
        if self.FACULTY_FLAG:
            self.insert_facts(''.join([str(fac) for fac in nu_fac.all_faculty]))
        if self.EVENTS_FLAG:
            self.insert_facts(''.join([str(e) for e in nu_event.all_events]))
        if self.COLLEGE_FLAG:
            self.insert_facts(colleges.no_newline_string())

    def insert_fact(self, data):
        Pythonian.insert_data(self, 'session-reasoner', data)

    def insert_facts(self, data):
        facts = data.split('\n')
        for fact in facts:
            Pythonian.insert_data(self, 'session-reasoner', fact)


if __name__ == '__main__':  # code to execute if called from command-line
    SCRAPER = ScraperAgent(host='localhost', port=9000,
                           localPort=8950, debug=True)
    # (achieve :receiver TestAgent :content (task :action (scrape_achieve scrape faculty)))
