from datetime import date
from bs4 import BeautifulSoup
import requests
import datetime

class Schedule():

    def get_padge(self):
        url = 'https://www.fitnesshouse.ru/schedule-club.html?club=vet&scheduleFilterType=00&scheduleFilterTime=00#schedule'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup
    
    @staticmethod
    def chek_time(lesson_time):
        lesson_time = lesson_time.split(':')
        t = datetime.time(hour=int(lesson_time[0]), minute=int(lesson_time[1]), second=0)
        current_time = datetime.datetime.now()
        current_time = datetime.time(hour=current_time.hour, minute =current_time.minute, second=0)
        if t >= current_time:
            return True
        else:
            return False
        
        print(t)

    def get_schedule(self, soup):
        schedule = soup.findAll('td', class_='table-schedule__td active')
        schedule_today = [] 

        for i in schedule:
            schedule_today.append({'time':i.get('data-time'),
                                   'name':i.find('div', class_='lesson__name').text.strip(),
                                 'deckription':i.get('onclick'),
                                  'place':i.find('div', class_='lesson__place').text.strip(),
                                  'couch':i.find('div', class_='lesson__trainer').text.strip()})

        text = str(date.today())
        schedule_today = tuple(filter(lambda a: self.chek_time(a['time']) and
                                      not('Бассейн' in a['place'] or
                                          '(250р.)' in a['name']), schedule_today ))

        if len(tuple(schedule_today)) == 0:
            text = 'Today is no lessons'
        else:
            for lesson in schedule_today:
                self.chek_time(lesson['time'])
                text = f'''{text}
Время:{lesson['time']}
Название: {lesson['name']}
Место: {lesson['place']}
Тренер: {lesson['couch']}\n'''
            print(2)
        return text


s = Schedule()
soup = s.get_padge()
print(s.get_schedule(soup))
