#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 3.6
# @Filename:    faculty_scraper.py
# @Author:      Samuel Hill
# @Email:       samuelhill2022@u.northwestern.edu
# @Date:        2019-03-11 12:25:27
# @Last Modified by:    Samuel Hill
# @Last Modified time:  2019-03-22 04:29:06

"""
General description of purpose.

More specific lorem ipsum dolor sit amet, consectetur adipiscing elit.
Quisque a lacus nulla. Vestibulum sodales eros ligula. Nullam euismod
libero magna.
"""

# IMPORTS
import string
import os
import pickle
from requests_html import HTMLSession
from college_scraper import CollegeScraper

# MODULE AUTHORSHIP INFO
__author__ = "Samuel Hill"
__copyright__ = "Copyright 2019, Samuel Hill."
__credits__ = ["Samuel Hill"]


# CLASSES
class FacultyScraper(object):
    """docstring for FacultyScraper"""

    # attributes to look for on faculty details page in xpath
    FACULTY_NAME = '//h1[@id="page-title"]/text()'
    ADDRESS = '//div[@id="faculty-profile-left"]/text()'
    PHONE_NUM = '//a[@class="phone_link"]/span/text()'
    # smaller strings to combine
    follow = 'following-sibling::'
    preced = 'preceding-sibling::'
    h2_dept = 'h2="Departments"'
    h2_site = 'h2[@class="sites-header"="Website"]'
    h2_affil = 'h2="Affiliations"'
    h2_edu = 'h2 = "Education"'
    h2_inter = 'h2 = "Research Interests"'
    omit_cv = 'a[@href and not(text() = "Download CV")]'
    find_cv = 'a[@href and text() = "Download CV"]'
    a_href = '/a[@href]/@href'
    a_text = '/a[@href]/text()'
    temp1 = '//p[{} and {}]'
    temp2 = '//p[{}]/'
    # remaining attributes, based on component strings above
    WEBPAGES = temp1.format(follow + h2_dept, preced + h2_site) + a_href
    WEBNAMES = temp1.format(follow + h2_dept, preced + h2_site) + a_text
    DEPARTMENT1 = temp1.format(follow + 'hr', preced + h2_dept) + a_text
    DEPARTMENT2 = temp1.format(follow + h2_affil, preced + h2_dept) + a_text
    AFFILIATIONS = (temp2 + '{}/text()').format(preced + h2_affil, omit_cv)
    CV_LINK = (temp2 + '{}/@href').format(preced + h2_affil, find_cv)
    EDUCATION = temp1.format(preced + h2_edu, follow + h2_inter) + '/text()'
    INTERESTS = temp2.format(preced + h2_inter) + '/text()'

    def __init__(self, session=None, url=''):
        super(FacultyScraper, self).__init__()
        self.session = session if session else HTMLSession()
        self.colleges = CollegeScraper()
        self.colleges.from_pickle()
        self.faculty_data = {}
        if url != '':
            self.scrape(url)

    def __str__(self):
        fac_id = self.faculty_data['id']
        mt_fn = '(SocialModelMtFn {})'.format(fac_id)
        krf = '(in-microtheory {})\n'.format(mt_fn)
        krf += '(isa {} NUPerson)\n'.format(fac_id)
        krf += '(isa {} NUFaculty)\n'.format(fac_id)
        for department in self.faculty_data['departments']:
            if department != 'Electrical Engineering and Computer Science':
                dept_id = CollegeScraper.make_unique(department)
                krf += '(department {} {})\n'.format(fac_id, dept_id)
        if self.faculty_data['education']:
            for edu in self.faculty_data['education']:
                if 'Ph.D' in edu:
                    krf += '(isa {} AcademicProfessional)\n'.format(fac_id)
                    krf += '(titleOfPerson {} Dr)\n'.format(fac_id)
                    break
            for edu in self.faculty_data['education']:
                degrees = ['M.S', 'MS', 'M.A', 'B.S', 'BS', 'B.A', 'B.E',
                           'M.E', 'M. Mus', 'B. Mus', 'Master of Fine Arts',
                           'B. Tech', 'A.B', 'S.M', 'S.B', 'B.CSci',
                           'Master of Science', 'Bachelor of Arts', 'Ph.D']
                for degree in degrees:
                    if degree in edu:
                        abbrev = self.upper_only(degree)
                        abbrev = 'PhD' if degree == 'Ph.D' else abbrev
                        krf += self.schooling(edu, abbrev, fac_id)
                        break
        if self.faculty_data['phone_number']:
            phone = self.faculty_data['phone_number']
            krf += '(phoneNumberOf {} "{}")\n'.format(fac_id, phone)
        email = self.faculty_data['email']
        krf += '(emailOf {} "{}")\n'.format(fac_id, email)
        if self.faculty_data['personal_site']:
            site = self.faculty_data['personal_site']
            krf += '(personalWebsite {} "{}")\n'.format(fac_id, site)
        room_number = self.faculty_data['room_number']
        krf += '(officeLocation {} "{}")\n'.format(fac_id, room_number)
        krf += '(in-microtheory EnglishMt)\n'
        krf += '(fullName {} "{}")\n'.format(fac_id, self.faculty_data['name'])
        last_name = self.faculty_data['name'].split(' ')[-1:][0]
        first_name = self.faculty_data['name'].split(' ')[0]
        name_temp = '(indexedProperName (TheList {}) {} {})\n'
        krf += name_temp.format('professor', last_name, fac_id)
        krf += name_temp.format('doctor', last_name, fac_id)
        krf += name_temp.format(first_name, last_name, fac_id)
        return krf

    @staticmethod
    def upper_only(abbrev):
        abbrev = CollegeScraper.make_unique(abbrev)
        return abbrev.translate(str.maketrans('', '', string.ascii_lowercase))

    def schooling(self, edu, degree, fac_id):
        krf = ''
        template = '(schooling {} {} {})\n'
        splitedu = edu.split(',')
        found = False
        options = []
        for i in range(len(self.colleges.colleges_dict)):
            # print(self.colleges.colleges_dict[i]['name'])
            college = self.colleges.colleges_dict[i]
            # for college in self.colleges.colleges_dict.items():
            if college['name'] in edu:
                krf += template.format(fac_id, college['id'], degree)
                found = True
                break  # Exact match, look no further
            if len(splitedu) > 1:
                # normal format is degree type (and field), school
                if splitedu[1] in college:  # 1 for school name, partial match
                    options.append(college['id'])  # add to list to go over...
        if not found:
            if len(options) == 1:  # only 1 option, use it
                krf += template.format(fac_id, options[0], degree)
            elif len(options) > 1:  # multiple options, check the state
                for option in options:
                    if splitedu[2] in option:  # normally split 2 is the state
                        krf += template.format(fac_id, option, degree)
                        break
            with open('extra_schools.pickle', 'rb') as data_file:
                extras = pickle.load(data_file)
                for extra in extras:
                    if extra['text'] in edu:  # not found in college scrape
                        krf += template.format(fac_id, extra['id'], degree)
                        break
        return krf

    def scrape(self, url):
        content = self.session.get(url).html
        name = content.xpath(self.FACULTY_NAME, first=True)
        full_address = content.xpath(self.ADDRESS)
        if full_address:
            address = '{} {}'.format(full_address[0], full_address[2])
            room = full_address[1]
        else:
            address, room = '', ''
        webpages = content.xpath(self.WEBPAGES)
        webnames = content.xpath(self.WEBNAMES)
        websites = list(zip(webpages, webnames))
        personal_site = ''
        for page, page_name in websites:
            if name in page_name:
                personal_site = page
        dept2 = content.xpath(self.DEPARTMENT2)
        self.faculty_data = {
            'name': name,
            'id': CollegeScraper.make_unique(name),
            'url': url,
            'address': address,
            'room_number': room,
            'phone_number': content.xpath(self.PHONE_NUM, first=True),
            'email': content.find('.mail_link', first=True).attrs['href'][7:],
            'websites': websites,
            'personal_site': personal_site,
            'departments': dept2 if dept2 else content.xpath(self.DEPARTMENT1),
            'affiliations': content.xpath(self.AFFILIATIONS),
            'cv_link': content.xpath(self.CV_LINK),
            'education': content.xpath(self.EDUCATION),
            'interests': content.xpath(self.INTERESTS)
        }


class NorthwesternFaculty(object):
    """docstring for NorthwesternFaculty"""

    BASE_PAGE = 'http://www.mccormick.northwestern.edu'
    EECS_PEOPLE = '/eecs/computer-science/people/'
    FACULTY_PAGE = BASE_PAGE + EECS_PEOPLE
    FACULTY_CSS = '.faculty-info > h3 > a'

    def __init__(self):
        super(NorthwesternFaculty, self).__init__()
        self.session = HTMLSession()
        self.all_faculty = []

    def __str__(self):
        return '\n\n'.join([str(fac) for fac in self.all_faculty])

    def scrape_all(self):
        base = self.session.get(self.FACULTY_PAGE)
        # by using a set, everything is in a random order each run
        set_of_links = set({})
        for element in base.html.find(self.FACULTY_CSS):
            set_of_links |= element.links
        for url in set_of_links:
            self.all_faculty.append(FacultyScraper(self.session, url))

    def to_krf(self):
        """Outputs the internal faculty data (as a string) to the filename
        specified in a path relative to where this program was called from."""
        real_dir = os.path.dirname(os.path.realpath(__file__))
        with open('{0}/{1}'.format(real_dir, 'faculty.krf'), 'w+') as outfile:
            outfile.write(str(self))

    def to_pickle(self):
        """Pickles the all_faculty into a compressed binary file for easy
        reading in by other python programs."""
        with open('faculty.pickle', 'wb') as outfile:
            pickle.dump(self.all_faculty, outfile)

    def from_pickle(self):
        """Reads the previously pickled scraped faculty data back in as if the
        data was scraped again."""
        with open('faculty.pickle', 'rb') as data_file:
            self.all_faculty = pickle.load(data_file)


if __name__ == '__main__':  # code to execute if called from command-line
    NF = NorthwesternFaculty()
    # NF.scrape_all()
    # NF.to_pickle()
    # NF.to_krf()
    NF.from_pickle()
    print(NF)
