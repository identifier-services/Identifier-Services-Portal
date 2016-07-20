import unittest
from selenium import webdriver

class TestViewsSelenium(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    # def test_something(self):
    #     self.driver.get('http://localhost:8000')
    #     logout = self.driver.find_element_by_partial_link_text('logout')
    #
    #     print logout
    #     print dir(logout)
    #
    #     if logout:
    #         logout.click()
