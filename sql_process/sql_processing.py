from table.data_process import GetSheet
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import psycopg2
import requests


class SQLProcessing(GetSheet):
    """
    Class to work with PostgreSQL Database using DBMS technique, content functions:
    get_currency_rate: to get the currency rate from the national bank of Russian Federation by using web scarping
    with BeautifulSoup library.
    change2ruble: function to make new column for our table, using get_currency_rate function to change all prices
    from USD to Ruble.
    data_getter: function to get all data from the table (table_order), return it as a DataFrame, that make next steps
    easier to do.
    data_input: function to put data into table (table_order) from the Google sheet.
    data_delete: function to delete all data from the table.
    check_equality: function to check if every element in both table and sheet are equal, to add unfounded elements
    or update them.
    this class has inherits from GetSheet class that gives an ability to work and use all functions and attributes
    of both classes
    """

    def __init__(self):
        super().__init__()
        # Connect to your postgres DB
        self.conn = psycopg2.connect(dbname="numbers-tz", user="postgres", password="1234", host='localhost',
                                     port='5432')
        self.cur = self.conn.cursor()  # Open a cursor to perform database operations
        self.data = self.sheet_getter()

    @staticmethod
    def get_currency_rate():
        response = requests.get('https://cbr.ru/')
        response.raise_for_status()
        site = response.text
        soup = BeautifulSoup(site, 'html.parser')
        rate = soup.find('div', class_='col-md-2 col-xs-9 _right mono-num').text
        res = float(rate.split()[0].replace(',', '.'))
        return np.array(res)

    def change2ruble(self):
        price_in_usd = map(float, self.data['стоимость, $'].tolist())
        rsl = [round(i * self.get_currency_rate(), 2) for i in price_in_usd]
        return np.array(rsl)

    def data_getter(self):
        self.cur.execute("SELECT * FROM table_order ORDER BY id")
        cols = ['№', 'заказ №', 'стоимость, $', 'стоимость_руб', 'срок поставки']
        return pd.DataFrame(self.cur.fetchall(), columns=cols)

    def data_input(self):
        cols = 'id, order_num, price_usd, price_rub, delivery_time'
        values = '%s, %s, %s, %s, %s'
        num = np.array(self.data['№'].tolist())
        order = np.array(self.data['заказ №'].tolist())
        price_usd = np.array(self.data['стоимость, $'].tolist())
        price_rub = self.change2ruble()
        time = np.array(self.data['срок поставки'].tolist())
        for i in range(num.shape[0]):
            self.cur.execute(f"INSERT INTO table_order ({cols}) VALUES ({values})",
                             (num[i], order[i], price_usd[i], price_rub[i], time[i]))
        self.conn.commit()

    def delete_all(self):
        self.cur.execute('DELETE FROM table_order')
        self.cur.execute('TRUNCATE table_order RESTART IDENTITY;')
        self.conn.commit()

    def check_equality(self):
        df_table = self.data_getter()
        df_sheet = self.sheet_getter()
        labels = ['заказ №', 'стоимость, $', 'срок поставки']
        if df_sheet.shape[0] != df_table.shape[0]:
            self.delete_all()
            self.data_input()
        else:
            check = set()
            for label in labels:
                check.add(all((df_table[label] == df_sheet[label])))
            if not all(check):
                self.delete_all()
                self.data_input()
