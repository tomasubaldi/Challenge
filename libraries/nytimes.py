from RPA.Browser.Selenium import Selenium
from config import Config
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import openpyxl

class NewYorkTimes:

    def __init__(self):
        self.browser= Selenium(auto_close=False)  
        self.url=Config().NEW_YORK_TIMES_URL

    def open_website(self):
        self.browser.open_available_browser(self.url)
        self.browser.maximize_browser_window()

    def search_phrase(self, search_phrase=Config().SEARCH_PHRASE):
        self.browser.click_button_when_visible("//button[@class='css-tkwi90 e1iflr850']")
        self.browser.input_text_when_element_is_visible("//input[@placeholder='SEARCH']",search_phrase)
        self.browser.click_button_when_visible("//button[normalize-space()='Go']")
        


    def apply_filters(self, section=Config().SECTION):
        if section!='':
            self.browser.click_button_when_visible("//div[@data-testid='section']//button[@type='button']")
            self.browser.click_button_when_visible("//input[@value='{section}'|nyt://section/70e865b6-cc70-5181-84c9-8368b3a5c34b']")
        else:
            self.browser.click_button_when_visible("//div[@data-testid='section']//button[@type='button']")
            self.browser.click_button_when_visible("//input[@value='Any']")
        #Aca va lo del show more, nose si esta bien
        #while self.browser.is_element_visible("//button[normalize-space()='Show More']"):
        #   self.browser.click_button_when_visible("//button[normalize-space()='Show More']")
        #   self.browser.wait_until_page_contains_element("//li[@class='css-1l4w6pd']")    
       
        
    def get_news_data(self):
        news_list = []
        
        try:
            news_elements = self.browser.find_elements("//li[@class='css-1l4w6pd']")
            for news_element in news_elements:
                try:
                    title_element = news_element.find_element(By.CLASS_NAME, "css-2fgx4k")
                    title = title_element.text
                except NoSuchElementException:
                    title = ""
                    
                try:
                    description_element = news_element.find_element(By.CLASS_NAME, "css-16nhkrn")
                    description = description_element.text
                except NoSuchElementException:
                    description = ""
                    
                try:
                    date_element = news_element.find_element(By.CLASS_NAME, "css-17ubb9w")
                    date = date_element.text 
                except NoSuchElementException:
                    date = ""
                    
                search_phrase_count = 0
                try:
                    search_phrase_count += title.lower().count(Config.SEARCH_PHRASE.lower())
                except AttributeError:
                    pass
                try:
                    search_phrase_count += description.lower().count(Config.SEARCH_PHRASE.lower())
                except AttributeError:
                    pass
                
                contains_money = False
                try:
                    contains_money = "$" in title or "USD" in title
                except TypeError:
                    pass
                try:
                    contains_money = contains_money or "$" in description or "USD" in description
                except TypeError:
                    pass
                
                news_list.append({
                    "title": title,
                    "description": description,
                    "date": date,
                    "search_phrase_count": search_phrase_count,
                    "contains_money": contains_money
                })
        except NoSuchElementException:
            print("No news were found")
          
          
        return news_list


    

def save_to_excel(news_list):
    wb = openpyxl.Workbook()
    ws = wb.active

    
    ws["A1"] = "Title"
    ws["B1"] = "Description"
    ws["C1"] = "Date"
    ws["D1"] = "Image Filename"
    ws["E1"] = "Search Phrase Count"
    ws["F1"] = "Contains Money"

   
    for i, news in enumerate(news_list, start=2):
        ws[f"A{i}"] = news.get("title", "")
        ws[f"B{i}"] = news.get("description", "")
        ws[f"C{i}"] = news.get("date", "")
        ws[f"D{i}"] = news.get("image_filename", "")
        ws[f"E{i}"] = news.get("search_phrase_count", "")
        ws[f"F{i}"] = news.get("contains_money", "")

    
    wb.save("news.xlsx")
