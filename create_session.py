"""Book tee times
To book: Booking - > Add Players -> Init Booking -> Save Booking
To delete: Calender -> Delete 

"""
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
import time
# from lxml import html


class TeeTimesSession:

    LOGIN_URL = 'https://mingolf.golf.se/Login'
    BOOK_TEETIME_URL = 'https://mingolf.golf.se/Site/Booking'
    INIT_BOOKING_URL = 'https://mingolf.golf.se/handlers/booking/InitBooking'
    CHECK_AVAILABLE_URL = 'https://mingolf.golf.se/handlers/booking/CheckAvailability'
    ADD_PLAYER_URL = 'https://mingolf.golf.se/handlers/booking/AddPlayerToBooking'
    GET_TEETIMES = 'https://mingolf.golf.se/handlers/booking/GetTeeTimesFullDay'
    SAVE_BOOKING = 'https://mingolf.golf.se/handlers/booking/SaveBooking'
    CANCEL_BOOKING = 'https://mingolf.golf.se/handlers/booking/CancelBooking'
    DELETE_BOOKED_TIME = 'https://mingolf.golf.se/handlers/Booking/DeleteBooking'
    CALENDER_URL = 'https://mingolf.golf.se/Site/Calendar/'
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
    BASE_CLUB_ID = '4fb14a3a-2135-4ae8-a302-0f7a38c93567' #Botkyrka
    BASE_COURSE_ID = '4bfc39cf-b2d2-4a32-ba81-a8db53e59bb2' #Botkyrka
    # BASE_CLUB_ID = 'c990d617-f27d-471c-be5e-a209dc2752cf'
    # BASE_COURSE_ID = '8b2b5855-323d-452d-b272-cba2cdb90c3a'


    def __init__(self, session=requests.Session()) -> None:
        self.session = session
        self.session.headers = self.HEADERS


    def get_all_times(self, date):
        url = f"{self.GET_TEETIMES}/{self.BASE_COURSE_ID}/{self.BASE_CLUB_ID}/{date}/1"
        times = self.session.get(url).json()
        return times

    def get_available_times(self, tee_times):
        taken_slots = []
        all_tee_times = tee_times
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
    
    def get_lookup_timeperiod(self, tee_times, look_from, look_to):
        available = [slot for slot in tee_times if slot['SlotTime'] >= look_from and slot['SlotTime'] <= look_to]
        return available
    
    def get_slot_closest_to_prefered(self, tee_times, prefered):
        prefered_dt = datetime.strptime(prefered, '%Y%m%dT%H%M%S')
        time = None
        diff = None
        for slot in tee_times:
            slot_time = datetime.strptime(slot["SlotTime"], '%Y%m%dT%H%M%S')
            temp_diff = abs((prefered_dt - slot_time).total_seconds())
            if diff is None:
                time = slot
                diff = temp_diff
            else:
                if temp_diff < diff:
                    time = slot
        return time
        


    
    def set_filterperiod(self, datestamp):
        dates = {}
        datestamp_obj = datetime.strptime(datestamp, '%Y%m%dT%H%M%S')
        filter_period_from = datestamp_obj - relativedelta(months=3)
        filter_period_to = datestamp_obj + relativedelta(months=3)
        dates['filterPeriodFrom'] = filter_period_from.strftime('%Y%m%dT%H%M%S')
        dates['filterPeriodTo'] = filter_period_to.strftime('%Y%m%dT%H%M%S')
        return dates


    def check_availability(self, teetime_slot):
        pdata = {"slotId":      teetime_slot['SlotID'],
                 "slotTime":    teetime_slot['SlotTime'],
                 "courseId":    teetime_slot['CourseID'],
                 "clubId":      teetime_slot['OrganizationalunitID'],
                 "bookingCode": ''}
        self.session.headers['Referer'] = 'https://mingolf.golf.se/'
        self.session.get(self.BOOK_TEETIME_URL)
        is_available = self.session.post(self.CHECK_AVAILABLE_URL, data=pdata).json()
        if is_available['Slot']['Status'] == 0:
            return is_available

    def add_player(self, golf_id):
        response = self.session.post(self.ADD_PLAYER_URL, data={'golfId': golf_id, 'countryCode': 'SE'})
        if response.status_code == 200:
            res_data = response.json()
            if res_data['HasErrors'] == True:
                print(res_data['ErrorMessage'])
            else:
                print('player added')

    def book_teetime(self, teetime_slot, players):
        self.session.get(self.BOOK_TEETIME_URL)
        pdata = {'slotId': teetime_slot['SlotID']} #15 maj
        data = {
            "slotId": teetime_slot['SlotID'],
            "slotTime": teetime_slot['SlotTime'],
            "courseId": teetime_slot['CourseID'],
            "clubId": teetime_slot['OrganizationalunitID'],
            "bookingCode": ''
        }
        is_available = self.session.post(self.CHECK_AVAILABLE_URL, data=data)
        init_booking = self.session.post(self.INIT_BOOKING_URL, data=pdata).json()
        if players:
            for player in players:
                self.add_player(player)
        book_teetime = self.session.post(self.SAVE_BOOKING).json()
        return book_teetime

    def print_booking_info(self, booked_teetime):
        booked_players = []
        time = booked_teetime['Slot']['BookingInfo']['Time']
        dt_time = datetime.strptime(time, '%Y%m%dT%H%M%S')
        for player in booked_teetime['Slot']['BookingInfo']['BookedPlayers']:
            first_name = player['FName']
            last_name = player['LName']
            booked_players.append(f"{first_name} {last_name}")
        print('BOOKING INFO')
        print('='*60)
        print('Date: ', dt_time.strftime('%Y-%m-%d'))
        print('Day: ', dt_time.strftime('%A'))
        print('Time: ', dt_time.strftime('%H:%M'))
        print('Booked players: ', "\t".join(booked_players))
        print('='*60)
        


    def delete_teetime(self, slot_id, slot_time):
        data = {'slotId': slot_id}
        dates = self.set_filterperiod(slot_time)
        pdata = {
            "slotId": slot_id,
            "handler": "Details",
            "itemTime": slot_time,
            "listType": "future",
            "maxExpand": "6",
            "filterPeriodFrom": dates['filterPeriodFrom'],
            "filterPeriodTo": dates['filterPeriodTo']
        }
        self.session.headers['Referer'] = 'https://mingolf.golf.se/'
        time = self.session.get(self.CALENDER_URL, params=pdata).json()
        deleted = self.session.post(self.DELETE_BOOKED_TIME, data=data).json()



    

    



class TeeTimes(TeeTimesSession):
    """Class to check for available tee-times as Botkyrka golfklubb
    
    HOW TO USE: 
        If no date is provided, the module will check for available
        tee-times for the current day. If date is specified then
        it will check for available tee-times for the whole day.
    """
    
    def __init__(self, username, password, datestamp, look_from, look_to, prefered_teetime=None, players=None):
        """Initiates the class
            Args:
                username (str): Golf-id for mingolf.se YYMMDD-XXX
                password (str): Password for mingolf.se
                date (str): Date to check for times: YYYYMMDDTHHMMSS or YYYYMMDD
        """
        super().__init__()
        self.username = str(username)
        self.password = str(password)
        self.datestamp = datetime.strptime(datestamp, '%Y-%m-%d').strftime('%Y%m%dT%H%M%S')
        self.look_from = datetime.strptime(f"{datestamp}_{look_from}", '%Y-%m-%d_%H:%M').strftime('%Y%m%dT%H%M%S')
        self.look_to = datetime.strptime(f"{datestamp}_{look_to}", '%Y-%m-%d_%H:%M').strftime('%Y%m%dT%H%M%S')
        self.prefered_teetime = datetime.strptime(f"{datestamp}_{prefered_teetime}", '%Y-%m-%d_%H:%M').strftime('%Y%m%dT%H%M%S')
        self.players = players
        #Login to begin session
        self.login()
        print('Logged in')

    
    def post_login_data(self):
        post_data = {
            'txtGolfID': self.username, 
            'txtPassword': self.password, 
            'target':self.LOGIN_URL, 
            'action':'submit'}
        return post_data
    
    def login(self):
        login = self.session.post(self.LOGIN_URL, data=self.post_login_data())
        # tree = html.fromstring(login.content)
        # failed = tree.xpath('//*[@id="exp-forgot-password"]/a')
        # if failed:
        #     print('Please check login-credentials to www.mingolf.se')
    
    def start_teetime_scan(self):
        not_booked = True
        while not_booked:
            all_times = self.get_all_times(self.datestamp)
            free_times = self.get_available_times(all_times)
            if not free_times:
                print('No times found')
            else:
                times_to_consider = self.get_lookup_timeperiod(free_times, self.look_from, self.look_to)
                if not times_to_consider:
                    print('No times withing lookup period')
                else:
                    if self.prefered_teetime:
                        slot = self.get_slot_closest_to_prefered(times_to_consider, self.prefered_teetime)
                        booked = self.book_teetime(slot, self.players)
                        if booked['HasErrors']:
                            print('Error yet: ', booked['ErrorMessage'])
                            continue
                        else:
                            self.print_booking_info(booked)
                            return booked
                    else:
                        booked = self.book_teetime(times_to_consider[0], self.players)
                        self.print_booking_info(booked)
                        return booked





if __name__ == '__main__':
    FELIX = "950821-011"
    SEBBE = "970424-001"
    JEPPE = "960427-020"
    MARCUS = "931209-006"
    LUKAS = "970104-015"
    players_sat = [FELIX, SEBBE, JEPPE]
    players_sun = [JEPPE, SEBBE, MARCUS]
    players_test = [JEPPE]
    user = TeeTimes('970712-024', 'adde123', '2022-07-09', '08:00', '13:00', prefered_teetime='09:00', players=None)
    user.start_teetime_scan()

    