import random
import requests
import json
import names
import time
import urllib3
import os
import sys
import threading
from faker import Faker
os.system('cls' if os.name == 'nt' else 'clear')
urllib3.disable_warnings()

class shell:
    def __init__(self, proxy, task) -> None:
        a = proxy.split(':')
        proxy = '{}:{}@{}:{}'.format(a[2],a[3],a[0],a[1])
        self.session = requests.Session()
        # self.session.verify = False
        self.session.proxies = {
            "http": "http://" + proxy,
            "https": "http://" + proxy
        }
        self.task = task
        self.userAgent = Faker().user_agent()
        self.fetchSite()

    def fetchSite(self):
        headers = {
            'User-Agent': self.userAgent,
            'origin': 'https://shell-10year.promo.eprize.com',
            'referer': 'https://shell-10year.promo.eprize.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }
        self.session.get('https://shell-10year.promo.eprize.com/#/register', headers=headers)
        self.makeTask()

    def log(self, message, error=None):
        if (error):
            print("[{}] {}".format(self.__class__.__name__, error))
        print("[{}] {}".format(self.__class__.__name__, message))
        sys.stdout.flush()

    def makeTask(self):
        self.log(f'Thread: {self.task} | Making Account')
        self.solveCaptcha()

    def solveCaptcha(self):
        config = {
            "clientKey":"###",
            "task":
            {
                "type":"NoCaptchaTaskProxyless",
                "websiteURL":"https://shell-10year.promo.eprize.com/#/register",
                "websiteKey":"6LfFX0UhAAAAADz0yc6rc18_9kCy0JEvhvn8MW-0"
            }
        }
        r = self.session.post('https://api.capmonster.cloud/createTask', data=json.dumps(config)).json()
        id = r['taskId']
        self.log(f'Thread {self.task} | ID: {id}')
        self.getSolution(id)
    
    def getSolution(self, id):
        config = {
            "clientKey":"###",
            "taskId": id
        }
        while True:
            try:
                r = self.session.post('https://api.capmonster.cloud/getTaskResult', data=json.dumps(config)).json()
                self.log(f"Thread {self.task} | Captcha status: {r['status']}")
                solution = r['solution']['gRecaptchaResponse']
                if solution:
                    break
            except:
                time.sleep(5)
                self.log(f'Thread {self.task} | No Solution, waiting')
        self.log(f'Thread {self.task} | Captcha resp : {solution[0:10]}...')
        self.createProfile(solution)
    
    def createProfile(self, solution):
        email = names.get_first_name() + names.get_last_name() + str(''.join([str(random.randint(0,9)) for x in range(4)]))
        domain = 'gmail.com'
        config = {
            "is_limited":'true',
            "plays_remaining":0,
            "age":"",
            "primary_opt_in":'true',
            "rules":'true',
            "first_name":f"{names.get_first_name()}",
            "last_name":f"{names.get_last_name()}",
            "email":f"{email}@{domain}",
            "country":"US",
            "x_channel":"def",
            "locale":"en-US",
            "isAutomatedTest":'false',
            "g-recaptcha-response": f"{solution}"
            }
            
        headers = {
            'User-Agent': self.userAgent,
            'origin': 'https://shell-10year.promo.eprize.com',
            'referer': 'https://shell-10year.promo.eprize.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'Content-Type': 'application/json',
            'accept': 'application/json, text/plain, */*'
        }

        r = self.session.post('https://shell-10year.promo.eprize.com/api/profiles', data=json.dumps(config), headers=headers).json()

        try:
            userID = r['result']['profile']['id']
            token = r['result']['profile']['token']
            with open("./accounts.txt", "a", encoding='utf-8') as f:
                f.write(f'{config["email"]}\n')
        except:
            self.log(r)

        self.entry(userID, token, config["email"])
    
    def entry(self, id, token, email):
        config = {"id":f"{id}"}
        headers = {
            'origin': 'https://shell-10year.promo.eprize.com',
            'referer': 'https://shell-10year.promo.eprize.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.userAgent,
            'x-hw-profile-token': f'{token}'
        }
        r = self.session.post('https://shell-10year.promo.eprize.com/api/game/play', data=json.dumps(config), headers=headers).json()
        try:
            won = r['prizeWon']
            if won: 
                with open("./won.txt", "a", encoding='utf-8') as f:
                    f.write(f'{won} | {email}\n')
        except:
            pass
        self.log(r)

with open('./proxy.txt','r') as f:
    proxies = f.read().split('\n')

threads = []
for x in proxies:
    threads.append(threading.Thread(target=shell, args=[x, 1]))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
 
