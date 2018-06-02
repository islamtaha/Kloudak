#!/usr/bin/python3.6
import requests
import sys


def signUp(inventory, username, email, password):
    url = f'http://{inventory}:5000/signup/'
    data = {'username': username, 'email': email, 'password': password}
    r = requests.post(url, data=data)
    print(f'status_code={r.status_code}')
    print(f'response_body={r.text}')
    return r.status_code


def login(inventory, username, password):
    url = f'http://{inventory}:5000/login/'
    data = {'username': username, 'password': password}
    r = requests.post(url, data=data)
    print(f'status_code={r.status_code}')
    print(f'response_body={r.text}')
    print(f'token header value:\n {r.headers["token"]}')
    return r.status_code


def main():
    if len(sys.argv) > 1:
        inventory = sys.argv[1]
        username = sys.argv[2]
        email = sys.argv[3]
        password = sys.argv[4]
        print(sys.argv)
    else:
        inventory = input('Enter Inventory IP: ')
        username = input('Enter Username: ')
        email = input('Enter Email: ')
        password = input('Enter Password')
    sCode = signUp(inventory, username, email, password)
    if sCode == 200 or sCode == 201:
        lCode = login(inventory, username, password)
    else:
        print('signup failed')
        exit(0)


if __name__ == '__main__':
    main()

