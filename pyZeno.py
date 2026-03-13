import requests
import os
import json

class Server:
    def __init__(self,url,key,uaid,passw=''):
        self.passw = passw
        self.key = key
        self.url = url
        self.uaid = uaid

    def del_user(self,user_id):
        pak = {'admin_password': self.passw,
               'admin_key': self.key,
               'UAID':self.uaid,
               'request_data': {'command': 'del',
                                'vars': [user_id,'f']
                                }
               }
        try:
            resp = requests.post(f"{self.url}/panel/users", json=pak)
            data = resp.json()
            if data is not None:
                if data['status'] == 'ERROR COMMAND':
                    print(f'[pyZENO ADMIN] ERORR: erorr command')
                    return False
                if data['status'] == 'USER DELETED':
                    print(f'[pyZENO ADMIN] USER DELETED')
                    return True
            if data is None:
                print(f'[pyZENO ADMIN] ERORR: no data')
            else:
                return data
        except requests.exceptions.RequestException as e:
            print(f'[pyZENO ADMIN] ERORR {e}')
            return False

    def add_chat(self,user1_id,user2_id ):
        pak = {'admin_password': self.passw,
               'admin_key': self.key,
               'UAID': self.uaid,
               'request_data': {'command': 'add',
                                'vars': [user1_id, user2_id]
                                }
               }
        try:
            resp = requests.post(f"{self.url}/panel/users", json=pak)
            data = resp.json()
            if data is not None:
                if data['status'] == 'ERROR COMMAND':
                    print(f'[pyZENO ADMIN] ERORR: erorr command')
                    return False
                if data['status'] == 'CHAT WAS ADDED':
                    print(f'[pyZENO ADMIN] CHAT WAS ADDED')
                    return True
                if data['status'] == 'CHAT ADDED SUCCESSFULLY':
                    print(f'[pyZENO ADMIN] CHAT ADDED SUCCESSFULLY')
                    return True
            if data is None:
                print(f'[pyZENO ADMIN] ERORR: no data')
        except requests.exceptions.RequestException as e:
            print(f'[pyZENO ADMIN] ERORR {e}')
            return False

    def status(self):
        try:
            r = requests.get(f'{self.url}/status')
            return r.json()['status']
        except Exception as e:
            return e

    def users(self):
        try:
            r = requests.get(f'{self.url}/{self.passw}/usr/show')
            return r.json()
        except Exception as e:
            return e

class User:
    def __init__(self,user_nick, user_id,user_mail,user_password,work_url,use_backup, user_GMID='',user_PMID='', user_UDID='',):
        self.user_nick = user_nick
        self.work_url = work_url.url
        self.user_id = user_id
        self.user_mail = user_mail
        self.user_password = user_password
        self.user_GMID = user_GMID
        self.user_UDID = user_UDID
        self.user_PMID = user_PMID
        self.use_backup = use_backup
        self.backup = {}
        if use_backup == True:
            if not os.path.exists(f'pyZenoBackup_{self.user_id}.json'):
                with open(f'pyZenoBackup_{self.user_id}.json','w') as f:
                    json_data = {'user_id': self.user_id,
                                        'user_mail': self.user_mail,
                                        'user_password': self.user_password,
                                        'user_GMID': self.user_GMID,
                                        'user_UDID': self.user_UDID,
                                        'user_PMID': self.user_PMID,
                                        }
                    f.write(json.dumps(json_data))
                    self.backup = json_data
                    print('[pyZENO] Backup created')
            else:
                with open(f'pyZenoBackup_{self.user_id}.json','r') as f:
                    backup = json.load(f)
                    self.user_id = backup['user_id']
                    self.user_mail = backup['user_mail']
                    self.user_password = backup['user_password']
                    self.user_GMID = backup['user_GMID']
                    self.user_UDID = backup['user_UDID']
                    self.user_PMID = backup['user_PMID']
                    self.backup = backup
                    print('[pyZENO] Backup loaded')

    def save_backup(self):
        with open(f'pyZenoBackup_{self.user_id}.json', 'w') as f:
            f.write(json.dumps(self.backup))
            print('[pyZENO] Backup saved')
    def register(self):
        try:
            resp = requests.post(f"{self.work_url}/reg/",
                                 json={'nick': self.user_nick,'id': self.user_id, 'password': self.user_password, 'mail': self.user_mail, 'reg_type': 'fast'})
            data = resp.json()
            if data is not None:
                self.user_UDID = data['UDID']
                self.user_GMID = data['GMID']
                self.user_PMID = data['PMID']
                self.user_nick = data['nick']
                self.user_mail = data['mail']
                self.backup['nick'] = data['nick']
                self.backup['chats'] = data['chats']
                self.backup['mail'] = data['mail']
                self.backup['user_UDID'] = data['UDID']
                self.backup['user_PMID'] = data['PMID']
                self.backup['user_GMID'] = data['GMID']
                self.save_backup()
                return data
            else:
                print('[pyZENO] answer is empty')
        except Exception as e:
            print(f'[pyZENO] Failed register: {e}')
    def login(self):
        try:
            resp = requests.post(f"{self.work_url}/login/",json={'id': self.user_id, 'password': self.user_password, 'mail': self.user_mail})
            data = resp.json()
            if data is not None and 'UDID' in data:
                self.user_UDID = data['UDID']
                if self.use_backup == True:
                        self.backup['user_UDID'] = self.user_UDID
                        self.save_backup()
                print('[pyZENO] UDID updated')
                return data
            else:
                print('[pyZENO] Login failed:', data.get('status') if isinstance(data, dict) else 'Unknown error')
                if data.get('status') == 'Device already registered':
                    return True
                else:
                    return False
        except Exception as e:
            print(f'[pyZENO] Failed login: {e}')
            return False

    def send_message(self,recipient_id, message: str):
        resp = requests.post(f"{self.work_url}/mes/post/", json={'sender_id': self.user_id,
                                                                'sender_PMID': self.user_PMID ,
                                                                'sender_UDID': self.user_UDID,
                                                                'recipient_id': recipient_id,
                                                                'message': message})
        data = resp.json()
        if resp.status_code != 200:
            print('[pyZENO] Post Messages failed:',
                    data.get('status') if isinstance(data, dict) else resp.status_code)
            return False
        if data is not None and 'newPMID' in data:
            self.user_PMID = resp.json()['newPMID']
            if self.use_backup == True:
                self.backup['user_PMID'] = self.user_PMID
                self.save_backup()
            return resp.json()
        if data is not None:
            return data
        else:
            print('[pyZENO] Post Message failed:', data.get('status') if isinstance(data, dict) else 'Unknown error')

    def get_messages(self):
        resp = requests.get(f"{self.work_url}/mes/get/",json={'user_id': self.user_id, 'user_GMID': self.user_GMID, 'user_UDID': self.user_UDID})
        data = resp.json()
        if resp.status_code != 200:
            print('[pyZENO] Get Messages failed:', data.get('status') if isinstance(data, dict) else resp.status_code)
            return False
        if data is not None and 'GMID' in data:
            self.user_GMID = resp.json()['GMID']
            if self.use_backup == True:
                self.backup['user_GMID'] = self.user_GMID
                self.save_backup()
            return resp.json()
        if data is not None:
            return data
        else:
            print('[pyZENO] Get Message failed:', data.get('status') if isinstance(data, dict) else 'Unknown error')
