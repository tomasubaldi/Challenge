from libraries.nytimes import NewYorkTimes

class Process:

    def __init__(self) -> None:
        self.nytimes = NewYorkTimes()
    
    def start(self):
        self.nytimes.open_website()
        self.nytimes.search_phrase()
        self.nytimes.apply_filters()
        self.nytimes.get_news_data()



            
    def finish(self):
        print("The process has finished")

        