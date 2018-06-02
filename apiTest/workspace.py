#!/usr/bin/python3.6
import requests
import json
import sys

class workspace():
    def __init__(self, inventory, name):
        self.name = name
        self.inventory = inventory
        self.s = requests.session()

    def login(self, username, password):
        url = f'http://{self.inventory}:5000/login/'
        data = {'username': username, 'password': password}
        rLogin = self.s.post(url, data=data)
        if rLogin.status_code != 200:
            print('login failed')
            exit(1)
        self.s.headers['token'] = rLogin.headers['token']

    def post(self):
        url = f'http://{self.inventory}:5000/workspaces/'
        data = {'name': self.name}
        rPost = self.s.post(url, data=json.dumps(data))
        print(f'status_code={rPost.status_code}')
        print(f'response_body={rPost.status_code}')
        self.s.headers['token'] = rPost.headers['token']
        return rPost.status_code

    def get(self):
        url = f'http://{self.inventory}:5000/workspaces/{self.name}/'
        rGet = self.s.get(url=url)
        print(f'status_code={rGet.status_code}')
        if rGet.status_code == 200 or rGet.status_code == 201:
            print(f'response_body={rGet.text}')
        else:
            b = input('get request failed. show response body?(y/n)')
            if b == 'y' or b == 'yes':
                print(f'response_text={rGet.text}')
        return rGet.status_code

    def put(self, new_name):
        url = f'http://{self.inventory}:5000/workspaces/{self.name}/'
        data = {'name': new_name}
        rPut = self.s.put(url, data=json.dumps(data))
        print(f'status_code={rPut.status_code}')
        if rPut.status_code == 200 or rGet.status_code == 201:
            print(f'response_body={rPut.text}')
            self.name = new_name
        else:
            b = input('put request failed. show response body?(y/n)')
            if b == 'y' or b == 'yes':
                print(f'reponse_body={rPut.text}')
            return rPut.status_code

    def delete(self):
        url = f'http://{self.inventory}:5000/workspaces/{self.name}/'
        rDelete = self.s.delete(url)
        print(f'status_code={rDelete.status_code}')
        if rDelete.text:
            b = input('delete request failed. show response body?(y/n)')
            if b == 'y' or b == 'yes':
                print(f'response_body={rDelete.text}')
        return rDelete.status_code



def main():
    if len(sys.argv) > 1:
        inventory = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]
        name = sys.argv[4]
        new_name = sys.argv[5]
    else:
        inventory = input('Enter Inventory IP: ')
        username = input('Enter Username: ')
        password = input('Enter Password: ')
        name = input('Enter Workspace name: ')
        new_name = input('Enter Workspace new_name')

    ws = workspace(inventory, name)
    ws.login(username, password)
    print('getting workspace')
    gCode = ws.get()
    print('-------------------------------------------------------')
    print('creating workspace')
    pCode = ws.post()
    print('-------------------------------------------------------')
    print('updating workspace')
    pCode = ws.put(new_name)
    print('-------------------------------------------------------')
    print('getting updated workspace')
    guCode = ws.get()
    print('-------------------------------------------------------')
    print('deleting workspace')
    dCode = ws.delete()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        exit(1)
