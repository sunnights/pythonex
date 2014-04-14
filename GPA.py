# -*- coding: GBK -*-

import sys
import urllib  
import urllib2
import cookielib
import re
import string
import types

class SDU_Spider:

    def login(self):
        self.zjh = raw_input("学号：")
        self.mm = raw_input("密码：")
    
    # 申明相关的属性  
    def __init__(self):
        self.zjh = ''
        self.mm = ''
        self.login();
        self.loginUrl = 'http://202.207.247.44:8063/loginAction.do'         # 登录的url
        self.resultUrl = 'http://202.207.247.44:8063/gradeLnAllAction.do?type=ln&oper=fainfo&fajhh=1374'       # 显示成绩的url
        self.cookieJar = cookielib.CookieJar()                              # 初始化一个CookieJar来处理Cookie的信息
        self.postdata=urllib.urlencode({'zjh':self.zjh,'mm':self.mm})  # POST的数据
        print self.postdata
        print '\n'
        f.write(self.postdata + '\n\n')
        self.cno = []
        self.cseq = []
        self.cname = []
        self.cename = []
        self.credit = []
        self.cprop = []
        self.grade = []
        self.reason = []
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
        self.gp = []
        self.GPA = 0.0

    def sdu_init(self):
        # 初始化链接并且获取cookie
        myRequest = urllib2.Request(url = self.loginUrl,data = self.postdata)   # 自定义一个请求
        response = self.opener.open(myRequest)            # 访问登录页面，获取到必须的cookie的值
        response = self.opener.open(self.resultUrl)       # 访问成绩页面，获得成绩的数据
        # 打印返回的内容
        #print response.read()
        self.deal_data(response.read())
        #self.print_data()
        self.print_datatofile()

        self.cal_GP()
        
        self.cal_GPA()
        print u'各门成绩绩点:'
        print self.gp
        print u'GPA:'
        print self.GPA
        f.write(u'GPA:' + str(self.GPA) + '\n')
        

    # 将内容从页面代码中抠出来
    def deal_data(self,myPage):
        myItems = re.findall('<tr class="odd.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<td[^>]*>([^<]*)</td>.*?<p[^>]*>([^<]*)&nbsp;</P>.*?<p[^>]*>([^<]*)&nbsp;</P>',myPage,re.S)     #获取到学分
        #print myItems
        for item in myItems:
            self.cno.append(item[0].strip())
            self.cseq.append(item[1].strip())
            self.cname.append(item[2].strip())
            self.cename.append(item[3].strip())
            self.credit.append(item[4].strip())
            self.cprop.append(item[5].strip())
            self.grade.append(item[6].strip())
            self.reason.append(item[7].strip())
            
    # 输出各门成绩
    def print_data(self):
        for i in range(len(self.cno)):
            print self.cno[i]
            print self.cseq[i]
            print self.cname[i]
            print self.cename[i]
            print self.credit[i]
            print self.cprop[i]
            print self.grade[i]
            print self.reason[i]

    def print_datatofile(self):
        for i in range(len(self.cno)):
            f.write(self.cno[i] + '\n')
            f.write(self.cseq[i] + '\n')
            f.write(self.cname[i] + '\n')
            f.write(self.cename[i] + '\n')
            f.write(self.credit[i] + '\n')
            f.write(self.cprop[i] + '\n')
            f.write(self.grade[i] + '\n')
            f.write(self.reason[i] + '\n')

    def cal_GPA(self):
        # 学分绩点 = 绩点 × 学分
        # 平均学分绩点 = Σ学分绩点 / Σ学分
        self.cal_GP()
        sum_xfjd = 0.0
        sum_credit = 0.0
        for i in range(len(self.cno)):
            sum_xfjd += string.atof(self.gp[i]) * string.atof(self.credit[i])
            sum_credit += string.atof(self.credit[i])
        self.GPA = sum_xfjd / sum_credit

    def cal_GP(self):
        for i in range(len(self.cno)):
            #print self.grade[i]
            try:
                if unicode(self.grade[i]).isdecimal:
                    #print u'-----'
                    grade = string.atof(self.grade[i])
                    if (grade >= 95) & (grade <= 100):
                        self.gp.append(5)
                    elif (grade >= 90) & (grade < 95):
                        self.gp.append(4.5)
                    elif (grade >= 85) & (grade < 90):
                        self.gp.append(4)
                    elif (grade >= 80) & (grade < 85):
                        self.gp.append(3.5)
                    elif (grade >= 75) & (grade < 80):
                        self.gp.append(3)
                    elif (grade >= 70) & (grade < 75):
                        self.gp.append(2.5)
                    elif (grade >= 65) & (grade < 70):
                        self.gp.append(2)
                    elif (grade >= 60) & (grade < 65):
                        self.gp.append(1.5)
                    elif (grade < 60):
                        self.gp.append(0)
            except:
                #print u'--'
                grade = self.grade[i]
                if grade == '优秀':
                    self.gp.append(4.5)
                elif grade == '良好':
                    self.gp.append(3.5)
                elif grade == '中等':
                    self.gp.append(2.5)
                elif grade == '及格':
                    self.gp.append(1.5)
                elif grade == '不及格':
                    self.gp.append(0)
    
#调用
f = file('GPA.txt','w')
mySpider = SDU_Spider()
mySpider.sdu_init()
f.close()
raw_input("\n详细信息已输出至GPA.txt\n按任意键退出")
