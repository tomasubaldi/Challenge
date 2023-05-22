import time
import datetime
import re
import urllib.request
import os
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.keys import Keys
from RPA.Excel.Files import Files
from RPA.Browser.Selenium import Selenium
from config import Config
from info import Info


class NewYorkTimes:
    def __init__(self):
        self.browser = Selenium(auto_close=False)
        self.url = Config().NEW_YORK_TIMES_URL
        self.cwd = os.getcwd()

    def open_website(self):
        """Method to Open Website and check the cookies banner"""
        self.browser.open_available_browser(self.url)
        self.browser.maximize_browser_window()
        # If the Cookies Banner Appears
        if self.browser.is_element_visible("//button[@data-testid='GDPR-accept']"):
            self.browser.click_element_when_visible(
                "//button[@data-testid='GDPR-accept']")

    def search_phrase(self, search_phrase=Config().SEARCH_PHRASE):
        """Search Phrase Method"""
        print("Searching phrase...")
        self.browser.click_button_when_visible(
            "//button[@data-test-id='search-button']")
        self.browser.input_text_when_element_is_visible(
            "//input[@placeholder='SEARCH']", search_phrase)
        self.browser.click_button_when_visible(
            "//button[@data-test-id='search-submit']")
       
    def output_folder(self):
        """Method to create and clean all the files in the output folder"""
        if not os.path.exists("output"):
            os.makedirs("output")
        else:
            for f in os.listdir("output"):
                os.remove(os.path.join("output", f))

    def _date_filter(self, months_back):
        """Date Range Filter Method"""
        self.browser.click_button_when_visible(
            "//button[@data-testid='search-date-dropdown-a']")
        self.browser.wait_until_element_is_visible(
            "//button[@value='Specific Dates']")
        self.browser.click_button_when_visible(
            "//button[@value='Specific Dates']")
        # Find the input fields for start and end date|
        start_date_field = "//input[@aria-label='start date']"
        end_date_field = "//input[@aria-label='end date']"
        # Calculate the date range
        end_date = datetime.date.today()
        start_date = end_date - relativedelta(months=months_back)
        # Fill in the start and end date fields
        self.browser.input_text_when_element_is_visible(
            start_date_field, start_date.strftime("%m/%d/%Y"))
        self.browser.input_text_when_element_is_visible(
            end_date_field, end_date.strftime("%m/%d/%Y"))
        self.browser.find_element(end_date_field).send_keys(Keys.ENTER)
        print(f"Chosen Date Range: from {start_date} to {end_date}")

    def _press_show_more(self):
        """Method to show all the news pressing show more button"""
        try:
            while self.browser.is_element_visible(
                "//button[@data-testid='search-show-more-button']"):
                self.browser.wait_until_element_is_visible(
                    "//button[@data-testid='search-show-more-button']", timeout=10)
                self.browser.click_button_when_visible(
                    "//button[@data-testid='search-show-more-button']")
                time.sleep(2)
        except Exception as ex:
            raise Exception(f"Failed pressing show more button. {ex}") from ex

    def _section_filter(self, sections: list):
        """Method to filter with section/category"""
        self.browser.click_button_when_visible(
            "//button[@data-testid='search-multiselect-button']")
        self.browser.wait_until_element_is_visible(
            "//ul[@data-testid='multi-select-dropdown-list']")
        section_elements = self.browser.find_elements(
            "//label[input[@type='checkbox']]")
        time.sleep(2)
        for section_element in section_elements:
            for section in sections:
                if section in section_element.text:
                    section_element.click()
        self.browser.click_button_when_visible(
            "//button[@data-testid='search-multiselect-button']")

    def apply_filters(self):
        """Applying All the Filters"""
        print("Applying all the filters...")
        # Sort by newest
        self.browser.select_from_list_by_value(
            "//select[@data-testid='SearchForm-sortBy']", "newest")
        # Section Filter
        self._section_filter(Config().SECTION)
        # Data Filter
        self._date_filter(Config().MONTHS_BACK)
        # After manually entering the date range,
        # the page loaded an incorrect combination of dates which was resolved after refreshing
        self.browser.reload_page()
        time.sleep(3)

        # Show all the news pressing "Show More" button
        self._press_show_more()

    def _get_title(self, i: int):
        """Method to return the news' title"""
        try:
            title_element = self.browser.find_element(
                f"(//li[@data-testid='search-bodega-result'][{i}]//h4)")
            return title_element.text
        except Exception:
            return "No title found"

    def _get_description(self, i: int):
        """Method to return the news' description"""
        try:
            description_element = self.browser.find_element(
                f"//li[@data-testid='search-bodega-result'][{i}]//a/p[1]")
            return description_element.text
        except Exception:
            return "No description found"

    def _get_date(self, i: int):
        """ Method to return the news' date"""
        try:
            date_element = self.browser.find_element(
               f"(//li[@data-testid='search-bodega-result'][{i}]//span[@data-testid='todays-date'])"
            )
            return date_element.text
        except Exception:
            return "No date found"
        
    def _phrase_count(self, title: str , description: str, search_phrase=Config().SEARCH_PHRASE):
        """Method to count of search phrases in the title and description"""
        words = search_phrase.lower().split()
        title_count = sum(title.lower().count(word) for word in words)
        description_count = sum(description.lower().count(word) for word in words)
        phrase_count = title_count + description_count
        return phrase_count

    def _get_picture_link(self, i: int):
        """Method to return the news' picture link"""
        try:
            picture_element = self.browser.find_element(
                f"//li[@data-testid='search-bodega-result'][{i}]//img")
            return picture_element.get_attribute("src")
        except Exception:
            return "No date found"

    def _download_picture(self, picture_link, i: int):
        """Method to  download the news' picture"""
        picture = urllib.request.urlopen(picture_link).read()
        picture_filename = f"news_picture_{i}"
        with open(os.path.join(self.cwd, "output", f"{picture_filename}.jpg"), "wb") as f:
            f.write(picture)
        return picture_filename

    def _contains_money(self, str1, str2):
        """Method to evaluate if the title/description has any ammount of money"""
        # Pattern $11.1 | $111,111.11
        pattern1 = r"\$[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?"
        # Pattern 11 dollars | 11 USD
        pattern2 = r"[0-9]+ (?:dollars|USD)"

        match1 = re.search(pattern1, str1)
        match2 = re.search(pattern2, str1)
        match3 = re.search(pattern1, str2)
        match4 = re.search(pattern2, str2)

        return match1 is not None or match2 is not None or match3 is not None or match4 is not None

    def get_news_data(self):
        """Method to get the news' data"""
        self.browser.wait_until_element_is_visible("//ol[@data-testid='search-results']")
        news_list = []
        print("Getting data from all the news...")
        news_elements = self.browser.find_elements("//li[@data-testid='search-bodega-result']")
        for i, _ in enumerate(news_elements, start=1):
            try:
                new_info = Info()
                new_info.title = self._get_title(i)
                new_info.date = self._get_date(i)
                new_info.description = self._get_description(i)
                new_info.phrase_count = self._phrase_count(new_info.title, new_info.description)
                new_info.contains_money = self._contains_money(new_info.title, new_info.description)
                new_info.picture_link = self._get_picture_link(i)
                new_info.picture_filename = self._download_picture(
                    new_info.picture_link, i)
                news_list.append(new_info)
            except ValueError:
                print(f"Error in news number {i}")
                continue
        return news_list

    def save_to_excel(self, news_list):
        """Method to save the data in an excel file"""
        print("Saving to excel in output ...")
        excel_file = Files()
        excel_file.create_workbook()
        excel_file.create_worksheet(name="News")
        headers = [
            "Title",
            "Date",
            "Description",
            "Picture Link",
            "Picture Filename",
            "Phrase Count",
            "Contains Money?",
        ]
        excel_file.append_rows_to_worksheet([headers])
        for news in news_list:
            row = [
                news.title,
                news.date,
                news.description,
                news.picture_link,
                news.picture_filename,
                news.phrase_count,
                news.contains_money,
            ]
            excel_file.append_rows_to_worksheet([row])

        excel_file.save_workbook(os.path.join(self.cwd, "output", "News.xlsx"))
