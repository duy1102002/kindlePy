import requests
from bs4 import BeautifulSoup


def get_out_ip(url):
    r = requests.get(url)
    txt = r.text
    ip = txt[txt.find("[") + 1: txt.find("]")]
    return str(ip)


def get_real_url(url=r'http://www.ip138.com/'):
    r = requests.get(url)
    txt = r.text
    soup = BeautifulSoup(txt,"html.parser").iframe
    return soup["src"]

def get_pub_ip():
    return get_out_ip(get_real_url())

if __name__ == '__main__':
    get_out_ip(get_real_url())

