from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import gspread
import os


class GetSheet:
    """
    This class is to connect the Google sheet and get info from (numbers-tz) sheet.
    Using privet keys from the JSON file (keys.jso)
    """
    def __init__(self):
        self.scope = ['https://www.googleapis.com/auth/spreadsheets',
                      'https://www.googleapis.com/auth/drive.file',
                      'https://www.googleapis.com/auth/drive']
        self.keys = os.path.join(os.path.dirname(__file__), 'keys.json')
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.keys, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open('numbers-tz').sheet1

    def sheet_getter(self):
        """
        Return: DataFrame with all information from (numbers-tz) Google sheet
        """
        columns = ['№', 'заказ №', 'стоимость, $', 'срок поставки']
        df = pd.DataFrame(self.sheet.get_all_values(), columns=columns).iloc[1:, :]
        df = df.reset_index(drop=True)
        return df
