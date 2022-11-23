import re
import json
import time
import math
import base64
import random
import string
import requests
import datetime
import urllib.error
import urllib.parse
import urllib.request
import http.cookiejar
from io import BytesIO
from Crypto.Cipher import AES
from PIL import Image, ImageDraw, ImageFont
from requests_toolbelt import MultipartEncoder


class SZPT:
    # URL
    GET_INFO_POST_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsjkxxbs/mrxxbs/getSaveReportInfo.do'
    SAVE_INFO_POST_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsjkxxbs/mrxxbs/saveReportInfo.do'
    SAVE_INFO_POST_URL_1 = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/tasks/startFlow.do'
    UPDATE_COOKIE_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/itpub/MobileCommon/getMenuInfo.do'
    GET_QueryUserTasks_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/*default/index/queryUserTasks.do'
    GET_LSH = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxslscxbb/data/getSerialNumber.do'
    GET_SN = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsgrjkmjxcktb/data/getSerialNumber.do'
    POST_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/tasks/startFlow.do?_=' + \
               str(int(round(time.time() * 1000)))
    GET_SESSION_URL = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=' \
                      'https://ehall.szpt.edu.cn:443/publicappinternet/sys/szptpubxsjkxxbs' \
                      '/*default/index.do?nodeId=0&taskId=0&processInstanceId=0&instId=0&defId=0&defKey=0'
    GET_SESSION_URL_1 = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=' \
                        'https://ehall.szpt.edu.cn:443/publicappinternet/sys/szptpubxslscxbb' \
                        '/*default/index.do?nodeId=0&taskId=0&processInstanceId=0&instId=0&defId=0&defKey=0'
    GET_SESSION_URL_2 = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=' \
                        'https://ehall.szpt.edu.cn:443/publicappinternet/sys/szptpubxsgrjkmjxcktb/' \
                        '*default/index.do?nodeId=0&taskId=0&processInstanceId=0&instId=0&defId=0&defKey=0'
    GET_SESSION_URL_3 = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=' \
                        'https://ehall.szpt.edu.cn:443/publicappinternet/sys/szptpubhsjcqd/' \
                        '*default/index.do?nodeId=0&taskId=0&processInstanceId=0&instId=0&defId=0&defKey=0'

    # 请求头
    header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.116 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/'
                  'signed-exchange;v=b3;q=0.9',
        'Host': 'ehall.szpt.edu.cn'}
    header_getinfo = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.116 Mobile Safari/537.36'}

    # 初始化
    def __init__(self, xhnum, passwd, rflag='1111'):
        self.username = xhnum
        self.password = passwd
        self.flag = rflag
        self.aline = 430
        self.now_time = datetime.datetime.now()
        self.dept_name, self.dept_code = None, None
        self.AID, self.AID1, self.AID2, self.AID3 = '', '', '', ''
        self.name, self.name1, self.phone, self.phone1, self.bj, self.mktime, self.fdy_id = '', '', '', '', '', '', ''
        self.LOGIN_URL = requests.get(self.GET_SESSION_URL, allow_redirects=False).headers['Location']
        self.LOGIN_URL_1 = requests.get(self.GET_SESSION_URL_1, allow_redirects=False).headers['Location']
        self.LOGIN_URL_2 = requests.get(self.GET_SESSION_URL_2, allow_redirects=False).headers['Location']
        self.LOGIN_URL_3 = requests.get(self.GET_SESSION_URL_3, allow_redirects=False).headers['Location']
        # cookiejar
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    # 登录
    def login(self):
        # 密码AES加密
        def aes_get_key(key, pwd):
            # 生成随机字符串
            def random_string(length):
                aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
                aes_chars_len = len(aes_chars)
                restr = ''
                for i in range(0, length):
                    restr += aes_chars[math.floor(random.random() * aes_chars_len)]
                return restr
            key = key[0:16].encode('utf-8')
            iv = random_string(16).encode()
            raw = random_string(64) + pwd
            text_length = len(raw)
            amount_to_pad = AES.block_size - (text_length % AES.block_size)
            if amount_to_pad == 0:
                amount_to_pad = AES.block_size
            pad = chr(amount_to_pad)
            tmp = raw + pad * amount_to_pad
            raw = tmp.encode()
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return base64.b64encode(cipher.encrypt(raw))
        # 登录请求
        request = urllib.request.Request(url=self.LOGIN_URL, method='GET')
        response = self.opener.open(request)
        html = response.read().decode('utf-8')
        # 获取登录参数
        lt = re.search('name="lt" value="(.*?)"/>', html, re.S).group(1)
        execution = re.search('name="execution" value="(.*?)"/>', html, re.S).group(1)
        aes_key = re.search('pwdDefaultEncryptSalt = "(.*?)";', html, re.S).group(1)
        password_aes = aes_get_key(aes_key, self.password)
        params = {'username': self.username, 'password': password_aes, 'lt': lt, 'dllt': 'userNamePasswordLogin',
                  'execution': execution, '_eventId': 'submit', 'rmShown': '1'}
        # 登录提交
        request = urllib.request.Request(url=self.LOGIN_URL, method='POST',
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'))
        response = self.opener.open(request)
        html = response.read().decode('utf-8')
        request = urllib.request.Request(url=self.LOGIN_URL_1, method='POST',
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'))
        response = self.opener.open(request)
        html1 = response.read().decode('utf-8')
        request = urllib.request.Request(url=self.LOGIN_URL_2, method='POST',
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'))
        response = self.opener.open(request)
        html2 = response.read().decode('utf-8')
        request = urllib.request.Request(url=self.LOGIN_URL_3, method='POST',
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'))
        response = self.opener.open(request)
        html3 = response.read().decode('utf-8')
        # 登录判断
        if "USERID='" + self.username + "'" in html:
            self.AID = re.search("APPID='(.*?)';", html, re.S).group(1)
            self.AID1 = re.search("APPID='(.*?)';", html1, re.S).group(1)
            self.AID2 = re.search("APPID='(.*?)';", html2, re.S).group(1)
            self.AID3 = re.search("APPID='(.*?)';", html3, re.S).group(1)
            return 0
        elif "密码有误" in html:
            return 1
        elif html.count("验证码") == 11:
            return 0  # 2
        else:
            return 3

    # 设置cookies
    def set_cookies(self, aid, aname):
        params_data = {"APPID": aid, "APPNAME": aname}
        # 转换成json参数
        params = {'data': json.dumps(params_data)}
        # 更新Cookie: _WEU
        request = urllib.request.Request(url=self.UPDATE_COOKIE_URL,
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                         method='POST', headers=self.header)  # 获取Cookie: _WEU
        self.opener.open(request)

    # 获取用户信息
    def get_userinfo(self):
        url = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/*default/index/queryUserTasks.do'
        body = 'taskType=ALL_TASK&nodeId=usertask1&appName=szptpubxsgrjkmjxcktb&module=modules&page=apply&action=getA' \
               'pplyData&*order=-CREATE_TIME&pageNumber=1&pageSize=1&'
        data = json.loads(self.opener.open(urllib.request.Request(url=url, method='POST', data=body.
                          encode(encoding='UTF-8'), headers=self.header)).read().decode('utf-8'))
        # 判断第一条是否为审核中
        if data['datas']['queryUserTasks']['rows'][0]['FLOWSTATUSNAME'] == "审核中":
            recall_url = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/tasks/callback.do?_=' + \
                         str(int(round(time.time() * 1000)))
            recall_body = {'id': 'callback', 'sendMessage': 'true', 'commandType': 'callback', 'execute': 'do_callback',
                           'sendCanceledTaskMessage': 'true', 'name': '撤回', 'url': '/sys/emapflow/tasks/callback.do',
                           'taskId': data['datas']['queryUserTasks']['rows'][0]['TASKID'], 'formData': {},
                           'defKey': 'szptpubxsgrjkmjxcktb.xsgrjkmjxcktb', 'flowComment': ''}
            recall_header = {'Accept': 'application/json, text/plain, */*'}
            self.opener.open(urllib.request.Request(url=recall_url, method='POST', data=urllib.parse.
                             urlencode(recall_body).encode(encoding='UTF-8'), headers=recall_header))
            delete_url = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/tasks/deleteInstance.do?isDelete' \
                         '=true&processInstanceId=' + data['datas']['queryUserTasks']['rows'][0]['PROCESSINSTANCEID'] \
                         + '&appName=szptpubxsgrjkmjxcktb&defKey=szptpubxsgrjkmjxcktb.xsgrjkmjxcktb'
            self.opener.open(urllib.request.Request(url=delete_url, method='POST'))
            # 更新data
            data = json.loads(self.opener.open(urllib.request.Request(url=url, method='POST', data=body.
                              encode(encoding='UTF-8'), headers=self.header)).read().decode('utf-8'))
        # 判断第一条是否为已撤回
        elif data['datas']['queryUserTasks']['rows'][0]['FLOWSTATUSNAME'] == "已撤回":
            delete_url = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/tasks/deleteInstance.do?isDelete' \
                         '=true&processInstanceId=' + data['datas']['queryUserTasks']['rows'][0]['PROCESSINSTANCEID'] \
                         + '&appName=szptpubxsgrjkmjxcktb&defKey=szptpubxsgrjkmjxcktb.xsgrjkmjxcktb'
            self.opener.open(urllib.request.Request(url=delete_url, method='POST'))
            # 更新data
            data = json.loads(self.opener.open(urllib.request.Request(url=url, method='POST', data=body.
                              encode(encoding='UTF-8'), headers=self.header)).read().decode('utf-8'))
        self.bj = data['datas']['queryUserTasks']['rows'][0]['BJ']
        self.dept_code = data['datas']['queryUserTasks']['rows'][0]['DEPT_CODE']
        self.dept_name = data['datas']['queryUserTasks']['rows'][0]['DEPT_NAME']
        self.name = data['datas']['queryUserTasks']['rows'][0]['USER_NAME']
        self.phone = data['datas']['queryUserTasks']['rows'][0]['USER_MOBILE']
        self.mktime = data['datas']['queryUserTasks']['rows'][0]['CREATE_TIME']
        self.mktime = datetime.datetime.strptime(self.mktime, '%Y-%m-%d %H:%M:%S')
        if len(self.name) == 2:
            self.name1 = self.name[0] + '*'
        else:
            self.name1 = self.name[0] + '*' * (len(self.name) - 2) + self.name[-1]
            self.aline = 430 - (len(self.name) - 2) * 10
        self.phone1 = self.phone[0:3] + '****' + self.phone[7:11]
        # 获取辅导员ID
        get_next = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsgrjkmjxcktb/data/getNextAssigneesBy' \
                   'NodeFdy.do?xh=' + self.username + '&_=' + str(int(round(time.time() * 1000)))
        data_fdy = {'nodeId': 'usertask2', 'defKey': 'szptpubxsgrjkmjxcktb.xsgrjkmjxcktb', 'defId': '', 'taskId': '',
                    'oneLegKicking': 'false', 'formData': '{}'}
        self.fdy_id = json.loads(self.opener.open(urllib.request.Request(get_next, headers=self.header,
                                 data=urllib.parse.urlencode(data_fdy).encode('utf-8'))).
                                 read().decode('utf-8'))['items']['candidates'][0]['userId']

    # 提交健康填报
    def send_info(self):
        print('[*] 健康填报 [*]')
        # 获取个人信息json数据
        params = {'USER_ID': self.username}
        request = urllib.request.Request(url=self.GET_INFO_POST_URL,
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                         method='POST', headers=self.header_getinfo)
        # 保存的参数
        response = self.opener.open(request)
        data = json.loads(response.read().decode('utf-8'))
        if 'WID' in data['datas']:
            print('[-] 今日已经填报！')
        else:
            # 22-11-23表单更新
            if 'XZZXQ' not in data['datas']:
                print('[-] 表单已更新，请重新填报！')
                return
            # update 每日首次提交表单会缺失以下数据
            temp_dict = {
                "ZSDZ": "", "FSSJ": "", "SSSQ": "", "XSQBDSJ": "", "STYXZK": "",
                "JSJJGCJTSJ": "", "JSJTGCJTSJ": "", "JSJJJTGCYY": "", "STYCZK": ""}
            data['datas'].update(temp_dict)
            # 更新最后一次核酸检测时间和返校时间
            yesterday = {"ZJYCHSJCSJ": time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400)),
                         "FXSJ": "2022-08-27"}
            data['datas'].update(yesterday)
            if 'WID' not in data['datas']:  # 每日首次提交，WID为空
                data['datas']['WID'] = ""
            if 'HSJCJG' not in data['datas']:  # 如果没有核酸检测记录，则HSJCJG为空
                data['datas']['HSJCJG'] = ""
            if 'SXFS' not in data['datas']:  # 如果没有在实习，则SXFS与SFZZSXDWSS为空
                data['datas']['SXFS'] = ""
            if 'SFZZSXDWSS' not in data['datas']:
                data['datas']['SFZZSXDWSS'] = ""
            # 提交信息
            params = {'formData': data['datas']}
            request = urllib.request.Request(url=self.SAVE_INFO_POST_URL,
                                             data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                             method='POST', headers=self.header_getinfo)
            response = self.opener.open(request)
            try:
                # 判断是否提交成功
                result_json = json.loads(response.read().decode('utf-8'))
                if result_json["code"] == "0":
                    print("[+] 填报成功")
            except Exception as e:
                print('[-] 已填报或需手动更新表单（以往表单数据不可用）')
                print('错误信息：', e)

    # 提交临时出校
    def send_info_1(self):
        print('[*] 临时出校 [*]')
        # 获取个人信息json数据
        params = {
            'taskType': 'ALL_TASK', 'nodeId': 'usertask1', 'appName': 'szptpubxslscxbb', 'module': 'modules',
            'page': 'apply', 'action': 'getApplyData', '*order': '-CREATE_TIME', 'pageNumber': 1, 'pageSize': 10}
        request = urllib.request.Request(url=self.GET_QueryUserTasks_URL,
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                         method='POST', headers=self.header_getinfo)
        # 保存的参数
        response = self.opener.open(request)
        data = json.loads(response.read().decode('utf-8'))
        if not data['datas']['queryUserTasks']['rows']:
            print('[-] 请先任意提交')
            return
        data = data['datas']['queryUserTasks']['rows'][0]
        date = time.strftime("%Y-%m-%d", time.localtime())
        if date in data["CXKSSJ"]:
            print('[-] 今日已经提交！')
        elif data['SFLS_DISPLAY'] == '是':
            print('[-] 学生已申请离深')
        else:
            # 获取出校地址及交通工具
            cxlj_url = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxslscxbb/modules/apply/' \
                       'T_IT_XSLSCXBB_CXLJ_QUERY.do?INFO_WID=%s' % data['WID']
            request = urllib.request.Request(url=cxlj_url, method='POST', headers=self.header_getinfo)
            response = self.opener.open(request)
            cxlj = json.loads(response.read().decode('utf-8'))  # 出行路径
            cxlj = cxlj['datas']['T_IT_XSLSCXBB_CXLJ_QUERY']['rows'][0]
            # 获取流水号LSH
            request = urllib.request.Request(url=self.GET_LSH, method='POST', headers=self.header_getinfo)
            response = self.opener.open(request)
            lsh = response.read().decode('utf-8')
            # 删除多余字段
            temp_dict = ['WID', 'OFFICE_MOBILE', 'SFZSWTGY', 'SFQWQTXQ', 'LXCXLJ', 'ZZCL', 'PROCESSINSTANCEID', 'DEFID',
                         'DEFKEY', 'FLOWSTATUS', 'FLOWSTATUSNAME', 'FLOWSUSPENSION', 'FLOWSUSPENSIONNAME', 'TASKINFO',
                         'NODEID', 'TASKID', 'NODENAME', 'TASKSTATUS', 'TASKSTATUSNAME', 'SFZSWTGY_DISPLAY',
                         'SFQWQTXQ_DISPLAY']
            for i in temp_dict:
                data.pop(i)
            # 构造要提交的数据包
            data['cxljFormData'] = "[{\"MDDXXDZ\":\"%s\",\"CXJTFS\":\"%s\",\"SEQ\":%d}]" % (
                cxlj['MDDXXDZ'], cxlj['CXJTFS'], cxlj['SEQ'])
            if not data['SFLS_DISPLAY']:
                data['SFLS'] = '0'
                data['SFLS_DISPLAY'] = '否'
            data['ignoreSubTableModify'] = False
            data['CREATE_TIME'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 创建时间
            data['CXKSSJ'] = time.strftime("%Y-%m-%d 00:00:00", time.localtime())
            data['CXJSSJ'] = time.strftime("%Y-%m-%d 23:59:00", time.localtime())
            data['REPORT_DATE'] = time.strftime("%Y-%m-%d", time.localtime())
            data['lsh'] = lsh
            params = {'formData': data, 'sendMessage': 'true', 'id': 'start', 'commandType': 'start',
                      'execute': 'do_start', 'name': '%E6%8F%90%E4%BA%A4', 'nextNodeId': 'endevent1', 'taskId': '',
                      'url': '%2Fsys%2Femapflow%2Ftasks%2FstartFlow.do', 'content': '%E6%8F%90%E4%BA%A4',
                      'defKey': 'szptpubxslscxbb.szptpubxslscxbb'}
            request = urllib.request.Request(url=self.SAVE_INFO_POST_URL_1,
                                             data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                             method='POST', headers=self.header_getinfo)
            # 提交数据
            response = self.opener.open(request)
            # 判断是否提交成功
            if response.read().decode('utf-8') == '{\"succeed\":true}':
                print("[+] 提交成功")
            else:
                print('[-] 需手动更新表单，以往表单数据不可用')

    # 提交三码填报
    def send_info_2(self):
        # 上传图片
        def get_imgs(in_img):
            uploadimg = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapcomponent/' \
                        'file/uploadTempFileAsAttachment.do'
            # 生成scope
            random_str = ''.join(random.sample(string.ascii_letters + string.digits, 34))
            # 构造WebKitFormBoundary
            fields = {'storeId': 'image', 'scope': random_str, 'fileToken': random_str + '1',
                      'files[]': ('1.jpg', in_img, 'image/jpeg')}
            boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
            headers_img = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "content-type": "multipart/form-data; boundary=" + boundary,
                "x-requested-with": "XMLHttpRequest"}
            m = MultipartEncoder(fields=fields, boundary=boundary)
            # 提交并返回图片ID
            self.opener.open(urllib.request.Request(url=uploadimg, data=m, headers=headers_img,
                                                    method='POST')).read().decode('utf-8')
            return random_str + '1'
        print('[*] 三码填报 [*]')
        # 获取用户信息
        self.get_userinfo()
        # 判断当日是否已提交
        if self.now_time.strftime("%Y-%m-%d") == self.mktime.strftime("%Y-%m-%d"):
            print('[-] 今日已经提交！')
            return
        # 生成粤康码
        img = Image.open(BytesIO(requests.get('https://s1.ax1x.com/2022/11/21/zQ3vJU.jpg', stream=True).content))
        draw = ImageDraw.Draw(img)
        draw.text((self.aline, 195), self.name1, fill="black", font=ImageFont.truetype("simhei.ttf", 35))
        draw.text((290, 330), self.now_time.strftime('%m-%d %H:%M:10'), fill="black",
                  font=ImageFont.truetype("simhei.ttf", 70))
        draw.text((185, 1560), self.now_time.strftime('%Y-%m-%d 02:20'), fill="white",
                  font=ImageFont.truetype("simhei.ttf", 28))
        # 生成行程卡
        img1 = Image.open(BytesIO(requests.get('https://s1.ax1x.com/2022/11/20/zMkOu4.jpg', stream=True).content))
        draw = ImageDraw.Draw(img1)
        draw.text((194, 492), self.phone1, fill="black", font=ImageFont.truetype("simhei.ttf", 46))
        draw.text((130, 580), self.now_time.strftime('更新于：%Y.%m.%d %H:%M:24'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 50))
        draw.text((131, 581), self.now_time.strftime('更新于：%Y.%m.%d %H:%M:24'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 50))
        draw.text((132, 582), self.now_time.strftime('更新于：%Y.%m.%d %H:%M:24'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 50))
        # 生成核酸记录
        img2 = Image.open(BytesIO(requests.get('https://s1.ax1x.com/2022/11/20/zMkXDJ.jpg', stream=True).content))
        draw = ImageDraw.Draw(img2)
        draw.text((35, 390), self.name, fill="black", font=ImageFont.truetype("simhei.ttf", 48))
        draw.text((35, 920), self.name, fill="black", font=ImageFont.truetype("simhei.ttf", 48))
        draw.text((35, 1450), self.name, fill="black", font=ImageFont.truetype("simhei.ttf", 48))
        draw.text((360, 485), (self.now_time-datetime.timedelta(days=1)).strftime('%Y-%m-%d 20:19'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 35))
        draw.text((360, 560), self.now_time.strftime('%Y-%m-%d 02:20'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 35))
        draw.text((360, 1015), (self.now_time-datetime.timedelta(days=2)).strftime('%Y-%m-%d 21:39'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 35))
        draw.text((360, 1090), (self.now_time-datetime.timedelta(days=1)).strftime('%Y-%m-%d 01:18'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 35))
        draw.text((360, 1545), (self.now_time-datetime.timedelta(days=3)).strftime('%Y-%m-%d 18:21'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 35))
        draw.text((360, 1620), (self.now_time-datetime.timedelta(days=2)).strftime('%Y-%m-%d 00:18'), fill="gray",
                  font=ImageFont.truetype("simhei.ttf", 35))
        # 将PIL转为bytes
        bimg, bimg1, bimg2 = BytesIO(), BytesIO(), BytesIO()
        img.save(bimg, format='JPEG')
        bimg = bimg.getvalue()
        img1.save(bimg1, format='JPEG')
        bimg1 = bimg1.getvalue()
        img2.save(bimg2, format='JPEG')
        bimg2 = bimg2.getvalue()
        # 构造数据
        fromdata = {"USER_ID": self.username, "USER_NAME": self.name, "DEPT_NAME": self.dept_name,
                    "USER_MOBILE": self.phone, "DEPT_CODE": self.dept_code, "BJ": self.bj,
                    "YKM": get_imgs(bimg), "XCK": get_imgs(bimg1), "HSJCBG": get_imgs(bimg2),
                    "LSH": self.opener.open(urllib.request.Request(self.GET_SN)).read().decode('utf-8'),
                    "CREATE_TIME": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        data = {'id': 'start', 'sendMessage': 'true', 'commandType': 'start', 'execute': 'do_start', 'name': '提交',
                'url': '/sys/emapflow/tasks/startFlow.do', 'nextNodeId': 'usertask2', 'nextAssignees': self.fdy_id,
                'assigneeAdd': '', 'taskId': '', 'defKey': 'szptpubxsgrjkmjxcktb.xsgrjkmjxcktb', 'formData': fromdata}
        # 提交
        res = self.opener.open(urllib.request.Request(self.POST_URL, data=urllib.parse.urlencode(data).
                                                      encode('utf-8'))).read().decode('utf-8')
        if res == '{\"succeed\":true}':
            print('[+] 提交成功')
        else:
            print('[-] 提交失败')

    # 每日核酸签到
    def send_info_3(self):
        print('[*] 核酸签到 [*]')
        response = self.opener.open('https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubhsjcqd/hsqd/sign.do')
        data = json.loads(response.read().decode('utf-8'))
        if data['code'] == '0':
            print('[+] 签到成功')
        elif data['code'] == '-1':
            print('[-] 今日已经签到！')
        else:
            print('[-] 未知错误')

    # 主入口
    def main(self):
        print('[*] ' + self.username + ' [*]')
        login_status = self.login()
        if login_status == 0:
            print('[+] 登录成功')
            self.set_cookies(self.AID, 'szptpubxsjkxxbs')
            self.set_cookies(self.AID1, 'szptpubxslscxbb')
            self.set_cookies(self.AID3, 'szptpubxsgrjkmjxcktb')
            self.set_cookies(self.AID2, 'szptpubhsjcqd')
            if self.flag[0] == '1':
                self.send_info()
            if self.flag[1] == '1':
                self.send_info_1()
            if self.flag[2] == '1':
                self.send_info_2()
            if self.flag[3] == '1':
                self.send_info_3()
        elif login_status == 1:
            print("[-] 登录失败，您的用户名或密码有误")
        elif login_status == 2:
            print("[-] 无法登录，需要验证码，请稍后再试或手动填报。")
        else:
            print("[-] 无法登录，未知错误，请检查网站是否能访问。")
        print()


if __name__ == '__main__':
    username = ''   # 学号
    password = ''   # 一网通办密码
    flag = '1111'   # 由4位0&1组成，分别代表健康填报、临时出校、三码填报、核酸签到，每位代表一项，1代表提交，0代表不提交
    cur = SZPT(username, password, flag)
    cur.main()
