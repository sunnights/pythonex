# -*-coding:utf-8-*-
import os
import re
import sys
import time

import bs4
import requests

session = requests.session()

stuqUrl = 'http://www.stuq.org/'
courseUrl = stuqUrl + 'my/courses/study/1015'
bokeccUrl = 'http://p.bokecc.com/'
videoUrl = bokeccUrl + 'flash/player.swf'

QRImagePath = os.getcwd() + '/qrcode.jpg'

uuid = ''
state = ''
wx_code = ''
stuq_redirect_url = ''


def get_wechat_qrcode_url():
    global uuid, state

    response = session.get('https://passport.stuq.org/user/oauth/wechat')

    regx = r'&state=(\S+)#wechat_redirect'
    state = re.search(regx, response.url).group(1)

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    img_tag = soup.select('div.wrp_code img[src]')
    uuid_url = [img.attrs.get('src') for img in img_tag]
    regx = r'/connect/qrcode/(\S+)'
    uuid = re.search(regx, uuid_url[0]).group(1)


def show_qr_image():
    qrcode_url = 'https://open.weixin.qq.com/connect/qrcode/' + uuid
    response = session.get(qrcode_url)

    f = open(QRImagePath, 'wb')
    f.write(response.content)
    f.close()

    print '请使用微信扫描二维码以登录'

    if sys.platform.find('darwin') >= 0:
        os.system('open %s' % QRImagePath)
    elif sys.platform.find('linux') >= 0:
        os.system('xdg-open %s' % QRImagePath)
    else:
        os.system('call %s' % QRImagePath)

    os.remove(QRImagePath)


def authenticate():
    global wx_code, stuq_redirect_url

    login_url = 'https://long.open.weixin.qq.com/connect/l/qrconnect?uuid=%s' % uuid
    response = session.get(login_url)

    regx = r'window.wx_errcode=(\d+)'
    wx_errcode = re.search(regx, response.text).group(1)

    if wx_errcode == '405':
        print '授权成功...'
        regx = r'window.wx_code=\'(\S+)\';'
        wx_code = re.search(regx, response.text).group(1)
        stuq_redirect_url = 'https://passport.stuq.org/user/callback/wechat?code=%s&state=%s' % (wx_code, state)
    elif wx_errcode == '408':  # 超时
        pass
    else:
        return False

    return wx_errcode


def get_videos():
    session.get(stuq_redirect_url)
    response = session.get('http://www.stuq.org/my/courses/study/1015')
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    a_tag = soup.select('div.accordion a[href^=/courseware]')
    course_url_list = [a.attrs.get('href') for a in a_tag]

    video_url_list = []
    for url in course_url_list:
        video_dict = {}
        response = session.get(stuqUrl + url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        tags = soup.select('script[data-name]')
        ids = [tag.string for tag in tags]
        playerid = 'D212A3C31EC3F8CB'
        video_dict['url'] = videoUrl + "?vid=%s&siteid=%s&playerid=%s" % (ids[0], ids[1], playerid)

        tags = soup.select('h3.header')
        name = [tag.string for tag in tags]
        video_dict['name'] =  re.sub(r'\s', '', name[0])

        video_url_list.append(video_dict)

    return video_url_list


def main():
    get_wechat_qrcode_url()
    show_qr_image()
    time.sleep(1)

    status = authenticate()
    if not status:
        print '授权失败...'
        return

    video_url_list = get_videos()
    for video in video_url_list:
        print('name:%s, url:%s' % (video['name'], video['url']))


# windows下编码问题修复
# http://blog.csdn.net/heyuxuanzee/article/details/8442718
class UnicodeStreamFilter:
    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding

    def write(self, s):
        if type(s) == str:
            s = s.decode('utf-8')
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)


# if sys.stdout.encoding == 'cp936':
#     sys.stdout = UnicodeStreamFilter(sys.stdout)

if __name__ == '__main__':
    main()
