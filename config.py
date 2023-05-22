from RPA.Robocorp.WorkItems import WorkItems    

work_items = WorkItems()
work_items.get_input_work_item()
work_item = work_items.get_work_item_variables()

class Config:
    NEW_YORK_TIMES_URL = work_item["NEW_YORK_TIMES_URL"]
    SEARCH_PHRASE = work_item["SEARCH_PHRASE"]
    SECTION = work_item["SECTION"]
    MONTHS_BACK = work_item["MONTHS_BACK"]