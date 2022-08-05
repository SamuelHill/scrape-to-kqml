#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 3.6
# @Filename:    events_scraper.py
# @Author:      Samuel Hill
# @Email:       samuelhill2022@u.northwestern.edu
# @Date:        2019-03-11 12:27:31
# @Last Modified by:    Samuel Hill
# @Last Modified time:  2019-03-22 04:30:01

"""
General description of purpose.

More specific lorem ipsum dolor sit amet, consectetur adipiscing elit.
Quisque a lacus nulla. Vestibulum sodales eros ligula. Nullam euismod
libero magna.
"""

# IMPORTS
import io
import os
import pickle
import time
from datetime import datetime, timedelta, date
from selenium import webdriver
from requests_html import HTML
from college_scraper import CollegeScraper

# MODULE AUTHORSHIP INFO
__author__ = "Samuel Hill"
__copyright__ = "Copyright 2019, Samuel Hill."
__credits__ = ["Samuel Hill"]


# CLASSES
class EventScraper(object):
    """docstring for EventScraper"""

    EVENT_NAME = '//div[@class="event_header"]/h2/text()'
    REOCCURRING = '//p[@id="recurring"]'
    WHERE_TEXT = '//span[text()[contains(.,"Where")]]/../text()'
    AUDIENCE_TEXT = '//span[text()[contains(.,"Audience")]]/../text()'
    CONTACT_TEXT = '//span[text()[contains(.,"Contact")]]/../text()'
    CONTACT_MAIL = '//span[text()[contains(.,"Contact")]]/../a/text()'
    GROUP_TEXT = '//span[text()[contains(.,"Group")]]/../a/text()'
    COST_TEXT = '//span[text()[contains(.,"Cost")]]/../text()'
    WHEN_TEXT = '//span[text()[contains(.,"When")]]/../text()'
    CATEGORY_TEXT = '//span[contains(@class, "event_category")]/text()'

    def __init__(self, driver, url=''):
        super(EventScraper, self).__init__()
        self.driver = driver
        self.event_data = {}
        if url != '':
            self.scrape(url)

    def __str__(self):
        date_list = self.event_data['date'].split(',')
        _, month_day, year = [d.strip() for d in date_list]
        month, day = month_day.split(' ')
        event_id = self.event_data['id']
        new_id = 'NUEvent-{}-{}-{}-{}'.format(year, month[:3], day, event_id)
        krf = '(in-microtheory (NUEventMtFn {}))\n'.format(new_id)
        krf += '(isa {} NUEvent)\n'.format(new_id)
        date_text = '(YearFn {})'.format(year)
        date_text = '(MonthFn {} {})'.format(month, date_text)
        date_text = '(DayFn {} {})'.format(day, date_text)
        if 'All' in self.event_data['time']:  # include 'All day'
            duration = '(DaysDuration 1)'
        else:
            start, end = self.event_data['time'].split(' - ')
            start_time, start_meridiem = start.split(' ')
            start_hr, start_minute = start_time.split(':')
            if start_meridiem == 'PM':
                start_hr = int(start_hr) + 12 if int(start_hr) != 12 else 12
            else:
                start_hr = int(start_hr) if int(start_hr) != 12 else 0
            date_text = '(HourFn {} {})'.format(start_hr, date_text)
            date_text = '(MinuteFn {} {})'.format(start_minute, date_text)
            start = '{}:{}'.format(start_hr, start_minute)
            end_time, end_meridiem = end.split(' ')
            end_hr, end_minute = end_time.split(':')
            if end_meridiem == 'PM':
                end_hr = int(end_hr) + 12 if int(end_hr) != 12 else 12
            else:
                end_hr = int(end_hr) if int(end_hr) != 12 else 0
            end = '{}:{}'.format(end_hr, end_minute)
            start = datetime.strptime(start, '%H:%M')
            end = datetime.strptime(end, '%H:%M')
            duration = end - start
            duration = duration.seconds//60
        krf += '(dateOfEvent {} {})\n'.format(new_id, date_text)
        krf += '(durationOfEvent {} {})\n'.format(new_id, duration)
        name = self.event_data['event_name']
        krf += '(eventName {} "{}")\n'.format(new_id, name)
        if self.event_data['location']:
            location = self.event_data['location']
            krf += '(eventLocale {} "{}")\n'.format(new_id, location)
        krf += '(eventHost {} "{}")\n'.format(new_id, self.event_data['group'])
        if self.event_data['contact_name']:
            con_name = self.event_data['contact_name']
            krf += '(eventHost {} "{}")\n'.format(new_id, con_name)
        if self.event_data['contact_phone']:
            con_phone = self.event_data['contact_phone']
            krf += '(eventHost {} "{}")\n'.format(new_id, con_phone)
        if self.event_data['contact_mail']:
            con_mail = self.event_data['contact_mail']
            krf += '(eventHost {} "{}")\n'.format(new_id, con_mail)
        audience_template = '(eventAudience {} {})\n'
        krf += '(eventAudience {} {})\n'.format(new_id, 'NUPerson')
        for audience in self.event_data['audience']:
            if audience == 'Faculty/Staff':
                krf += audience_template.format(new_id, 'NUFaculty')
                krf += audience_template.format(new_id, 'NUStaff')
            elif audience == 'Post Docs/Docs':
                krf += audience_template.format(new_id, 'NUPhDStudent')
                krf += audience_template.format(new_id, 'NUMastersStudent')
            elif audience == 'Student':
                krf += audience_template.format(new_id, 'NUStudent')
                krf += audience_template.format(new_id, 'NUUndergraduate')
            elif audience == 'Public':
                krf += audience_template.format(new_id, 'NUVisitor')
            elif audience == 'Graduate Students':
                krf += audience_template.format(new_id, 'NUGraduateStudent')
        if self.event_data['reoccurring']:
            krf += '(eventReoccurring {} t)\n'.format(new_id)
        if self.event_data['cost']:
            cost = self.event_data['cost']
            krf += '(eventCost {} "{}")\n'.format(new_id, cost)
        if self.event_data['category']:
            category = self.event_data['category']
            krf += '(eventCategory {} "{}")\n'.format(new_id, category)
        return krf

    def scrape(self, url):
        self.driver.get(url)
        content = HTML(html=self.driver.page_source)
        name = content.xpath(self.EVENT_NAME, first=True)
        clean_name = name.replace('“', '\\"').replace('"', '\\"')
        reoccur = content.xpath(self.REOCCURRING, first=True)
        raw_audience = content.xpath(self.AUDIENCE_TEXT, first=True)
        audience = raw_audience.strip().replace('\t', '').split(' - ')
        raw_contact = ''.join(content.xpath(self.CONTACT_TEXT))
        no_space = raw_contact.strip().replace('\t', '').replace('\xa0', '')
        contacts = no_space.split(' \n')
        if len(contacts) == 1:
            contact_name, contact_phone = contacts[0], ''
        else:
            contact_name, contact_phone = contacts
        cost = content.xpath(self.COST_TEXT, first=True)
        raw_when = content.xpath(self.WHEN_TEXT)
        full_date, time_range = [d.strip() for d in raw_when]
        self.event_data = {
            'url': url,
            'id': CollegeScraper.make_unique(name)[:30],
            'event_name': clean_name,
            'reoccurring': False if reoccur else True,
            'location': ''.join(content.xpath(self.WHERE_TEXT)).strip(),
            'audience': audience,
            'contact_name': contact_name,
            'contact_phone': contact_phone,
            'contact_mail': content.xpath(self.CONTACT_MAIL, first=True),
            'group': content.xpath(self.GROUP_TEXT, first=True),
            'cost': cost.strip() if cost else cost,
            'date': full_date,
            'time': time_range,
            'category': content.xpath(self.CATEGORY_TEXT, first=True)
        }


class NorthwesternEvents(object):
    """docstring for NorthwesternEvents"""

    EVENTS_PAGE = 'https://planitpurple.northwestern.edu'
    EVENTS_LIST = '//ul[@class="events"]/li/a/@href'

    def __init__(self, num_weeks=4):
        super(NorthwesternEvents, self).__init__()
        self.num_weeks = num_weeks
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.all_events = []

    def __str__(self):
        return '\n\n'.join([str(event) for event in self.all_events])

    def scrape_num_weeks(self):
        today = date.today()
        for _ in range(self.num_weeks):
            today_search = '/#search={}/0/1+5/1//week'.format(today)
            url = self.EVENTS_PAGE + today_search
            self.driver.get(url)
            time.sleep(1)
            content = HTML(html=self.driver.page_source)
            event_pages = content.xpath(self.EVENTS_LIST)
            for event_page in event_pages:
                url = self.EVENTS_PAGE + event_page
                self.all_events.append(EventScraper(self.driver, url))
            today += timedelta(days=7)

    def to_krf(self):
        """Outputs the internal events data (as a string) to the filename
        specified in a path relative to where this program was called from."""
        real_dir = os.path.dirname(os.path.realpath(__file__))
        filename = '{0}/{1}'.format(real_dir, 'events.krf')
        with io.open(filename, 'w+', encoding='utf-8') as outfile:
            outfile.write(str(self))

    def to_pickle(self):
        """Pickles the all_events into a compressed binary file for easy
        reading in by other python programs."""
        events = [e.event_data for e in self.all_events]
        with open('events.pickle', 'wb') as outfile:
            pickle.dump(events, outfile)

    def from_pickle(self):
        """Reads the previously pickled scraped events data back in as if the
        data was scraped again."""
        with open('events.pickle', 'rb') as data_file:
            events = pickle.load(data_file)
            for event in events:
                new_event = EventScraper(self.driver)
                new_event.event_data = event
                self.all_events.append(new_event)


if __name__ == '__main__':  # code to execute if called from command-line
    NE = NorthwesternEvents()
    # NE.scrape_num_weeks()
    # NE.to_pickle()
    # NE.to_krf()
    NE.from_pickle()
    print(NE)
