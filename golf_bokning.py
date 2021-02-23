import json
import re
import requests
import time

from bs4 import BeautifulSoup
from lxml import html

from datetime import datetime
from datetime import timedelta
from pprint import pprint

class TeeTimes:
    """Class to check for available tee-times as Botkyrka golfklubb
    
    HOW TO USE: 
        If no date is provided, the module will check for available
        tee-times for the current day. If date is specified then
        it will check for available tee-times for the whole day.
    """
    USERNAME_FORMAT = r"(^\d\d\d\d\d\d-\d\d\d$)"
    CURRENT_TIME = datetime.now().strftime('%H%M%S')
    END_OF_DAY = "19:00:00"
    if CURRENT_TIME > END_OF_DAY:
        DATE = datetime.today() + timedelta(days=1)
        TODAYS_DATE = DATE.strftime('%Y%m%dT000000')
    else:
        TODAYS_DATE = datetime.today().strftime('%Y%m%dT%H%M%S')

    def __init__(self, username, password, date=None):
        """Initiates the class
            Args:
                username (str): Golf-id for mingolf.se YYMMDD-XXX
                password (str): Password for mingolf.se
                date (str): Date to check for times: YYYYMMDDTHHMMSS or YYYYMMDD
        """
        if date:
            if re.match(r"(^20\d{2}\d{2}\d{2})([T])(\d{6}$)", date): #YYYYMMDDTHHMMSS
                self.date = date
            elif re.match(r"(^20\d{2}\d{2}\d{2}$)", date): #YYYYMMDD
                self.date = date +'T'+ self.CURRENT_TIME
            else:
                raise ValueError('Date must be formated YYYYMMDD or YYYYMMDDTHHMMSS')
        if not date:
            self.date = self.TODAYS_DATE
        if username:
            if re.match(self.USERNAME_FORMAT, username):
                self.username = str(username)
            else:
                raise ValueError('Username must be formated YYMMDD-XXX')
        if not username:
            self.username = None
        self.password = str(password)
        self.LOGINURL = 'https://mingolf.golf.se/Login?ReturnUrl=%2F'
        self.TEETIMES = f'https://mingolf.golf.se/handlers/booking/GetTeeTimesFullDay/4bfc39cf-b2d2-4a32-ba81-a8db53e59bb2/4fb14a3a-2135-4ae8-a302-0f7a38c93567/{self.date}/1'

    def post_data(self):
        post_data = {
            'txtGolfID': self.username, 
            'txtPassword': self.password, 
            'target':self.LOGINURL, 
            'action':'submit'}
        return post_data

    def login(self):
        with requests.Session() as s:
            s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
            r = s.post(self.LOGINURL, data=self.post_data())
            tree = html.fromstring(r.content)
            failed = tree.xpath('//*[@id="exp-forgot-password"]/a')
            if failed:
                print('Please check login-credentials to www.mingolf.se')
            else:
                return r

    def get_all_times(self):
        login = self.login()
        if login:
            headers = {'Referer': self.LOGINURL}
            with requests.Session() as s:
                s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
                r = s.post(self.LOGINURL, data=self.post_data())
                times = s.get(self.TEETIMES, headers=headers).json()
            return times

    
    def get_available_times(self):
        taken_slots = []
        all_tee_times = self.get_all_times()
        if all_tee_times:
            participants = all_tee_times['Participants']
            slots = all_tee_times['Slots']
            for key, value in participants.items():
                if value:
                    taken_slots.append(key)
            if taken_slots:
                for i in taken_slots:
                    slots.remove(next(d for d in slots if d['SlotID'] == i))
            res = [slot for slot in slots if slot['SlotReservations'] == None]
            return res
    
    def user_results(self):
        available_slots = self.get_available_times()
        if available_slots:
            available_times = []
            for available_slot in available_slots:
                slot = available_slot['SlotTime']
                slot_time = slot[-6:-4] + ':' + slot[-4:-2]
                available_times.append(slot_time)
            return available_times
    
    def format_results(self):
        times = self.user_results()
        if times:
            short_date = self.date[:8]
            neutral_date = datetime.today().strptime(short_date, '%Y%m%d').date()
            formated_date = neutral_date.strftime('%B %d, %Y')
            if times:
                formated_times = ('\t').join(times)
                formated_output = ('Lediga tider {}:').format(formated_date)
                return formated_output, formated_times
                #print('Boka på www.mingolf.se')
            else:
                formated_output = ('Inga lediga tider tider {}').format(formated_date)
                return formated_output
                #print(formated_output)
    

def main(username, password, date=None):
    username_format = r"(^\d\d\d\d\d\d-\d\d\d$)"
    if re.match(username_format, username):
        try: 
            tee_time = TeeTimes(username, password, date=date)
            return tee_time.format_results()
        except ValueError as e:
            print('Please check login-credentials to www.mingolf.se')
    else:
        print('GolfId is not valid, should be YYMMDD-XXX')


if __name__ == '__main__':
    print(TeeTimes('*******', '******').login())
