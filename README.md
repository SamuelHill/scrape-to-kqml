# Final Project Report

## Background and Motivation

- Portion of the kiosk project, needed an update
    + 3.6.5 compatible (and use full functionality, no lazy conversion)
    + better libraries, goes with 3.6.5 compatibility and exploration of
    etk and DIG for better scraping capabilities
    + look at how a tre and ltms (in this case scaled up with fire and
    all of companions) will handle data coming in on regular intervals
        * format python code to fit this goal. Currently, long term scrape
        comparison isn't being done but the code has been remodeled so that
        can happen on either the python or lisp side easily
    + further automate a portion of the live system -> exploring what it takes
    to keep something alive with real world data
- Broader, want a better way to hook Companions up with real world data.
    + Pythonians exists, want to explore it's capabilities and see what should
    extend it... There also isn't as standard of a setup for pulling down whatever
    arbitrary information you want on the web. Previous code was all scripts with
    helper functions and this was aiming to be both more 'pythonic' and more
    accessible to anyone else that wants to scrape data.

## Approach

- Read libraries - ETK, DIG, Requests-HTML, LXML, Selenium, Spacy, more...
    + to try and find the best web scraping engines and most simple interface
    for coding (API). Also looking at determining change in a webpage's data
    automatically (ETK - regex, DIG - alerts for new data, Spacy - Machine learning
    and NLP techniques).
- Rewrite the previous scraping code only using the xpath strings to point to the
same information... XPath is necessary for at least the Northwestern pages to point
to text within a div and NOT the text within plus other internal divs (thanks to
sloppy nesting) as well as arbitrary numbers of elements without classes or ids that
simply follow eachother and have predictable headings. i.e. Scraping is still annoying
for poorly build sites but the Requests-HTML library makes even xpath easier to deal
with and can smoothly transition to searching over the text or using typical css selectors.
    + try to keep libraries, installs, and outside connections as simple as possible -
    last time was a mess
- Verify data is being scraped flexibly by throwing previous saved scrapes at it
and checking that new html parsing is more robust than previously (new xpath function
return strings cleaned up more consistently and the output is always a list which is
easier to deal with that the typical None you must deal with in other libraries).
- Test adding (inserting) data to Companions from Python
- Test asking for data from Companions

## Highlights

- Horn clauses and reference urls
    + I reformatted the college data to use horn clauses to indicate what url the
    data was obtained from (similar to homework 4) and began saving the url with all the
    associated scraper class data so that later comparisons can check against the url to
    see if two facts (or sets of facts) are the same or come from the same source.
- Classes
    + created scraper classes for each page type we want to scrape (mostly for event and
    faculty but college sort of follows this principle too) that has a simple dictionary
    which gets populated by a scrape method. The string representation of the object is
    the set of facts (and microtheories) that come from that data and with this we can both
    easily create a krf file and splice up those facts and insert them into Companions.
    + created wrapper scraper classes for the associated data_type to scrape that knows about
    the url where all sub-pages can be found, and stores a list of every scraped object for
    each page it scrapes. This list can be saved to a krf (thanks to the string rep from the
    scraper class) or pickled (python serialized file) for later reloading of the object.
- python 3 string formatting (simple but makes creating lisp style strings super easy)

## Instructions

- Download [python 3.6.5](https://www.python.org/downloads/release/python-365/) (if you don't already have it)
- Get pykqml for Pythonian, pip now works! (I asked the github to do a new release)
`pip install pykqml==1.1`
- Get requests-HTML (written by Kenneth Reitz who has done many other awesome Python libraries)
`pip install requests-html`
- When you first run html.render() from requests-html, it will download the chromium.exe
for you to use. However, none of our code currently uses that render function and as such you need
to download [chromium](https://selenium-python.readthedocs.io/installation.html#drivers) and
link it into your system path (alt - in a python REPL you can create a session, get a url, and call
render on it to download chromium 'automatically', then simply link that chromium into your system
path. I played with this previously and because it downloaded a chromium for me, I use that for selenium too)
- Get selenium (requests rendering doesn't work fully for planitpurple as it uses iframes and
async calls)
`pip install selenium`
- Copy the contents of this folder to "C://qrg/companions/v1/pythonian/"
- Start companions
- Start session, pythonian test agent
- run `python scrape_to_kqml.py`
- from the commands tab enter something like:
    + `(achieve :receiver TestAgent :content (task :action (scrape_achieve options data_types)))`
        * where options is either scrape, pickle, krf, saveScrape, or load
        * and data_types is either college, faculty, events, or all
    + to get all data (scraped, saved, and inserted):
        * `(achieve :receiver TestAgent :content (task :action (scrape_achieve saveScrape all)))`
        * this should take about 5 minutes to finish scraping and about an hour to finish inserting
    + for simple tests of inserting to Companions, just use the load option to use my old pickles.

## Conclusions

- Pythonian needs an insert microtheory function that doesn't just put one fact in the baseKB
- Requests-HTML is super close to everything you need for data-scraping, the ease of use in the API
leads me to think that there is plenty of room for exploration - especially for well formatted
and template-d pages with bits of data scattered or a regular and normal structure.
- Leaving Requests-HTML and html scraping, look at using this class model to interface with other
APIs and ways of interacting with real world data in Companions.
- ETK doesn't work for windows
    + pip install etk results in an error regarding a c++ version (14.0+) that has a dead link
    and no working installers that I could find
- DIG doesn't currently fit this need, nor is what it really does actual coreference resolution
(that work is handled by spacy and plain text matching as far as I can tell from reading the
github files a fair bit). We could use it to detect updates on a page, triggering Companions to
check for updates etc.
