import requests
import os
from lxml import html
from pprint import pprint
from itertools import count

from common import EXPORTS_PATH, TED_USER, TED_PASSWORD

def make_ecas_session():
    session = requests.Session()
    data = {'lgid': 'en', 'action': 'gp'}
    res = session.get('http://ted.europa.eu/TED/browse/browseByBO.do')
    res = session.post('http://ted.europa.eu/TED/main/HomePage.do?pid=secured',
                       data=data, cookies={'lg': 'en'},
                       allow_redirects=True)
    a = html.fromstring(res.content).find('.//div[@id="main_domain"]/a[@title="External"]')
    res = session.get(a.get('href'))
    form = html.fromstring(res.content).find('.//form[@id="loginForm"]')
    data = dict([(i.get('name'), i.get('value')) for i in form.findall('.//input')])
    data['username'] = TED_USER
    data['password'] = TED_PASSWORD
    data['selfHost'] = 'webgate.ec.europa.eu'
    data['timeZone'] = 'GMT-04:00'
    res = session.post(form.get('action'), data=data,
                       allow_redirects=True)
    doc = html.fromstring(res.content)
    form = doc.find('.//form[@id="showAccountDetailsForm"]')
    data = dict([(i.get('name'), i.get('value')) for i in form.findall('.//input')])
    res = session.post(form.get('action'), data=data, allow_redirects=True)
    doc = html.fromstring(res.content)
    link = filter(lambda a: 'redirecting-to' in a.get('href', ''), doc.findall('.//a'))
    res = session.get(link.pop().get('href'))
    print "Session created."
    return session


def download_by_id(session, bulk_id):
    dest_path = os.path.join(EXPORTS_PATH, '%s.tgz' % bulk_id)
    print "Loading: %s" % dest_path
    if os.path.exists(dest_path):
        print "Skip: exists"
        return True
    url = "http://ted.europa.eu/TED/misc/bulkDownloadExport.do?dlTedExportojsId=%s"
    url = url % bulk_id
    data = {'action': 'dlTedExport'}
    res = session.post(url, data=data, allow_redirects=True)
    if 'html' in res.headers.get('content-type'):
        return False
    with open(dest_path, 'wb') as fh:
        fh.write(res.content)
    print "Downloaded: %s" % dest_path
    return True
    #pprint(dict(res.headers))


def download_latest(session):
    res = session.get('http://ted.europa.eu/TED/misc/bulkDownloadExport.do')
    doc = html.fromstring(res.content)
    for inp in doc.findall('.//input'):
        name = inp.get('name', '')
        if 'dlTedExportojsId' in name:
            bulk_id = inp.get('value')
            download_by_id(session, bulk_id)

def download_all(session):
    for i in count(1):
        bulk_id = '2013%03d' % i
        if not download_by_id(session, bulk_id):
            return


if __name__ == '__main__':
    session = make_ecas_session()
    #download_all(session)
    download_latest(session)
    #download_by_id(session, '2011001')
    #download_by_id(session, '2012001')
    #download_by_id(session, '2013001')

