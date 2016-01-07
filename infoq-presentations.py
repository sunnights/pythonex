# -*-coding:utf-8-*-

import re

import bs4
import requests

session = requests.session()

base_url = 'http://www.infoq.com/cn/presentations/'
page_url = 'application-of-lua-in-nginx'
presentation_url = base_url + page_url

response = session.get(presentation_url)
soup = bs4.BeautifulSoup(response.text, 'html.parser')

title_tag = soup.select('div.presentation_full div')
title = title_tag[0].string
title = re.sub(r'\s', '', title)

en_title = re.sub(r'-', ' ', page_url)

author_tag = soup.select('div.presentation_full a.editorlink')
author = author_tag[0].string
author = re.sub(r'\s', '', author)

url_tag = soup.select('div.video div#player script[src]')
url = url_tag[-1].attrs.get('src')

print('title: %s\nen_title: %s\nauthor: %s\nurl: %s' % (title, en_title, author, url))
