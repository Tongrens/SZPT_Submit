import re
import sys
import json
import time
import math
import base64
import random
import requests
import urllib.error
import urllib.parse
import urllib.request
import http.cookiejar
from Crypto.Cipher import AES


class SZPT:
    # URL
    GET_INFO_POST_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsjkxxbs/mrxxbs/getSaveReportInfo.do'
    SAVE_INFO_POST_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsjkxxbs/mrxxbs/saveReportInfo.do'
    SAVE_INFO_POST_URL_1 = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/tasks/startFlow.do'
    UPDATE_COOKIE_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/itpub/MobileCommon/getMenuInfo.do'
    GET_QueryUserTasks_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/emapflow/*default/index/queryUserTasks.do'
    GET_LSH = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxslscxbb/data/getSerialNumber.do'
    GET_SESSION_URL = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=' \
                      'https://ehall.szpt.edu.cn:443/publicappinternet/sys/szptpubxsjkxxbs' \
                      '/*default/index.do?nodeId=0&taskId=0&processInstanceId=0&instId=0&defId=0&defKey=0'
    GET_SESSION_URL_1 = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=' \
                        'https://ehall.szpt.edu.cn:443/publicappinternet/sys/szptpubxslscxbb' \
                        '/*default/index.do?nodeId=0&taskId=0&processInstanceId=0&instId=0&defId=0&defKey=0'
    """
    GET_SESSION_URL_2 = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=' \
                        'https://ehall.szpt.edu.cn:443/publicappinternet/sys/szptpubhsjcqd/' \
                        '*default/index.do?nodeId=0&taskId=0&processInstanceId=0&instId=0&defId=0&defKey=0'
    """
    # 请求头
    header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.116 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/'
                  'signed-exchange;v=b3;q=0.9',
        'Host': 'ehall.szpt.edu.cn'}
    header_getinfo = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.116 Mobile Safari/537.36',
    }

    # 初始化
    def __init__(self, username, password, flag='11'):
        self.username = username
        self.password = password
        self.flag = flag
        self.AID, self.AID1, self.AID2 = '', '', ''
        self.LOGIN_URL = requests.get(self.GET_SESSION_URL, allow_redirects=False).headers['Location']
        self.LOGIN_URL_1 = requests.get(self.GET_SESSION_URL_1, allow_redirects=False).headers['Location']
        # self.LOGIN_URL_2 = requests.get(self.GET_SESSION_URL_2, allow_redirects=False).headers['Location']
        # cookiejar
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    # 生成随机字符串
    def random_string(self, length):
        aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
        aes_chars_len = len(aes_chars)
        restr = ''
        for i in range(0, length):
            restr += aes_chars[math.floor(random.random() * aes_chars_len)]
        return restr

    # 密码AES加密
    def aes_get_key(self, key, pwd):
        key = key[0:16].encode('utf-8')
        iv = self.random_string(16).encode()
        raw = self.random_string(64) + pwd
        text_length = len(raw)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        tmp = raw + pad * amount_to_pad
        raw = tmp.encode()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(cipher.encrypt(raw))

    # 登录
    def login(self):
        # 登录请求
        request = urllib.request.Request(url=self.LOGIN_URL, method='GET')
        response = self.opener.open(request)
        html = response.read().decode('utf-8')
        # 获取登录参数
        lt = re.search('name="lt" value="(.*?)"/>', html, re.S).group(1)
        execution = re.search('name="execution" value="(.*?)"/>', html, re.S).group(1)
        aes_key = re.search('pwdDefaultEncryptSalt = "(.*?)";', html, re.S).group(1)
        password_aes = self.aes_get_key(aes_key, self.password)
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
        """
        request = urllib.request.Request(url=self.LOGIN_URL_2, method='POST',
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'))
        response = self.opener.open(request)
        html2 = response.read().decode('utf-8')
        """
        # 登录判断
        if "USERID='" + self.username + "'" in html:
            self.AID = re.search("APPID='(.*?)';", html, re.S).group(1)
            self.AID1 = re.search("APPID='(.*?)';", html1, re.S).group(1)
            # self.AID2 = re.search("APPID='(.*?)';", html2, re.S).group(1)
            return 0
        elif "密码有误" in html:
            return 1
        elif html.count("验证码") == 11:
            return 0   # 2
        else:
            return 3

    # 设置cookies
    def set_cookies(self, aid, name):
        params_data = {"APPID": aid, "APPNAME": name}
        # 转换成json参数
        params = {'data': json.dumps(params_data)}
        # 更新Cookie: _WEU
        request = urllib.request.Request(url=self.UPDATE_COOKIE_URL,
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                         method='POST', headers=self.header)  # 获取Cookie: _WEU
        self.opener.open(request)

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
            except:
                print('[-] 已填报或需手动更新表单（以往表单数据不可用）')

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
        else:
            # 获取出校地址及交通工具
            CXLJ_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxslscxbb/modules/apply/' \
                       'T_IT_XSLSCXBB_CXLJ_QUERY.do?INFO_WID=%s' % data['WID']
            request = urllib.request.Request(url=CXLJ_URL, method='POST', headers=self.header_getinfo)
            response = self.opener.open(request)
            CXLJ = json.loads(response.read().decode('utf-8'))  # 出行路径
            CXLJ = CXLJ['datas']['T_IT_XSLSCXBB_CXLJ_QUERY']['rows'][0]
            # 获取流水号LSH
            request = urllib.request.Request(url=self.GET_LSH, method='POST', headers=self.header_getinfo)
            response = self.opener.open(request)
            LSH = response.read().decode('utf-8')
            # 删除多余字段
            temp_dict = ['WID', 'OFFICE_MOBILE', 'SFZSWTGY', 'SFQWQTXQ', 'LXCXLJ', 'ZZCL', 'PROCESSINSTANCEID', 'DEFID',
                         'DEFKEY', 'FLOWSTATUS', 'FLOWSTATUSNAME', 'FLOWSUSPENSION', 'FLOWSUSPENSIONNAME', 'TASKINFO',
                         'NODEID', 'TASKID', 'NODENAME', 'TASKSTATUS', 'TASKSTATUSNAME', 'SFZSWTGY_DISPLAY',
                         'SFQWQTXQ_DISPLAY']
            for i in temp_dict:
                data.pop(i)
            # 构造要提交的数据包
            data['cxljFormData'] = "[{\"MDDXXDZ\":\"%s\",\"CXJTFS\":\"%s\",\"SEQ\":%d}]" % (
                CXLJ['MDDXXDZ'], CXLJ['CXJTFS'], CXLJ['SEQ'])
            data['ignoreSubTableModify'] = False
            data['CREATE_TIME'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 创建时间
            data['CXKSSJ'] = time.strftime("%Y-%m-%d 00:00:00", time.localtime())
            data['CXJSSJ'] = time.strftime("%Y-%m-%d 23:59:00", time.localtime())
            data['REPORT_DATE'] = time.strftime("%Y-%m-%d", time.localtime())
            data['LSH'] = LSH
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

    """
    # 每日核酸签到
    def send_info_2(self):
        print('[*] 核酸签到 [*]')
        response = self.opener.open('https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubhsjcqd/hsqd/sign.do')
        data = json.loads(response.read().decode('utf-8'))
        if data['code'] == '0':
            print('[+] 签到成功')
        elif data['code'] == '-1':
            print('[-] 今日已经签到！')
        else:
            print('[-] 未知错误')
    """

    # 主入口
    def main(self):
        print('[*] ' + self.username + ' [*]')
        login_status = self.login()
        if login_status == 0:
            print('[+] 登录成功')
            self.set_cookies(self.AID, 'szptpubxsjkxxbs')
            self.set_cookies(self.AID1, 'szptpubxslscxbb')
            # self.set_cookies(self.AID2, 'szptpubhsjcqd')
            if self.flag[0] == '1':
                self.send_info()
            if self.flag[1] == '1':
                self.send_info_1()
            """
            if self.flag[2] == '1':
                self.send_info_2()
            """
        elif login_status == 1:
            print("[-] 登录失败，您的用户名或密码有误")
        elif login_status == 2:
            print("[-] 无法登录，需要验证码，请稍后再试或手动填报。")
        else:
            print("[-] 无法登录，未知错误，请检查网站是否能访问。")
        print()


if __name__ == '__main__':
    arg = sys.argv
    if len(arg) != 4:
        print('[-] 请输入参数')
        sys.exit()
    u = arg[1]
    p = arg[2]
    f = arg[3]
    cur = SZPT(u, p, f)
    cur.main()
