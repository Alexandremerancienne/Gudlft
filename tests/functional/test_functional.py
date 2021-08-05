import unittest
from math import floor

from server import load_clubs, load_competitions
from server import load_purchases, dump_data

from random import choice, randrange
from selenium import webdriver


clubs = load_clubs()
competitions = load_competitions()
purchases = load_purchases()


class FunctionalTest(unittest.TestCase):

    """
    Sequence covered by FunctionalTest:

    Setup : Selenium web driver using Chrome as search engine

    1) A GET request is sent to 'http://127.0.0.1:5000/' page
    => The response includes the message
    'Welcome to the GUDLFT Registration Portal!'

    2) A POST request is sent to '/showSummary' page with a registered email
    => The response includes information relative
    to the identified club (email, remaining points)

    3) A competition is selected to book places
    => The response includes information relative
    to the selected competition (name, remaining places)

    4) Places are bought (within the limit of affordable places)
    => The information relative to the club and the competition
    are updated

    Teardown: Selenium web driver is closed and shut down
    """

    @classmethod
    def setUp(cls):
        path = "drivers/chromedriver.exe"
        cls.driver = webdriver.Chrome(executable_path=path)
        cls.driver.implicitly_wait(10)

        cls.club = choice(clubs)

        reload_competitions = load_competitions()
        cls.competition = reload_competitions[2]

        max_affordable_places = min(12, floor(int(cls.club['points'])/3),
                                    int(cls.competition['places']))
        cls.affordable_places = randrange(0, max_affordable_places + 1) \
            if max_affordable_places + 1 > 0 else 0

    def test_login_and_purchase_places(self):
        self.driver = \
            webdriver.Chrome(executable_path="drivers/chromedriver.exe")

        # 1) A GET request is sent to 'http://127.0.0.1:5000/' page

        self.driver.get("http://127.0.0.1:5000/")
        welcome_title = self.driver.find_element_by_tag_name("h1").text
        self.assertEqual(welcome_title,
                         'Welcome to the GUDLFT Registration Portal!')

        # 2) A POST request is sent to '/showSummary' page
        # with a registered email

        input_tag = self.driver.find_element_by_tag_name("input")
        input_tag.send_keys(self.club['email'])
        self.driver.find_element_by_tag_name("button").click()
        show_summary_title = self.driver.find_element_by_tag_name('h2').text
        self.assertEqual(show_summary_title, 'Welcome, ' + self.club['email'])

        # 3) A competition is selected to book places

        self.driver.find_elements_by_partial_link_text("Book")[2].click()
        reload_competitions = load_competitions()
        text = self.driver.find_element_by_tag_name("h2").text
        self.assertEqual(text, reload_competitions[2]['name'])

        # 4) Places are bought (within the limit of affordable places)

        self.driver.find_element_by_id("").send_keys(self.affordable_places)
        self.driver.find_element_by_tag_name("button").click()

        text = self.driver.find_element_by_tag_name("h2").text
        self.assertEqual(text, 'Welcome, ' + self.club['email'])
        self.assertTrue('Points available: ' +
                        str(int(self.club['points']) - 3*self.affordable_places)
                        in self.driver.page_source)
        self.assertTrue('Number of Places: ' +
                        str(int(self.competition['places'])
                            - self.affordable_places)
                        in self.driver.page_source)

    def tearDown(self):
        self.driver.close()
        self.driver.quit()
        dump_data("clubs.json", {"clubs": clubs})
        dump_data("competitions.json", {"competitions": competitions})
        dump_data("purchases.json", purchases)
