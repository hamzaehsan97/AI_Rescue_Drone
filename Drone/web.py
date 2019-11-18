import requests
import json
import datetime


def addToDatabase(position):
    url='http://192.168.64.2/test/insert.php'
    
    objectDict = {
        'time': datetime.datetime.now().time(),
        'position': position
    }
    header = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    }
    status= requests.post(url,data=objectDict, headers=header)
    print(status.text)
    

def main():
    addToDatabase(30)

if __name__ == '__main__':
    main()
