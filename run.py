import re
import json
import base64
import random
import requests
import urllib.parse
import urllib.request
import http.cookiejar
from Cryptodome.Cipher import AES


class SZPT:
    # URL
    UPDATE_COOKIE_URL = 'https://ehall.szpt.edu.cn/publicappinternet/sys/itpub/MobileCommon/getMenuInfo.do'
    GET_SESSION_URL = 'https://ehall.szpt.edu.cn:443/amp-auth-adapter/login?service=' \
                      'https://ehall.szpt.edu.cn:443/publicappinternet/sys/szptpubxsjkxxbs' \
                      '/*default/index.do?nodeId=0&taskId=0&processInstanceId=0&instId=0&defId=0&defKey=0'
    # 请求头
    header = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like '
                            'Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,appl'
                        'ication/signed-exchange;v=b3;q=0.9',
              'Host': 'ehall.szpt.edu.cn'}
    header_getinfo = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36'}

    # 初始化
    def __init__(self, xhnum, passwd):
        self.username, self.password, self.AID = xhnum, passwd, ''
        # cookiejar
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    # 登录
    def login(self):
        # 获取登录URL
        login_url = requests.get(self.GET_SESSION_URL, allow_redirects=False).headers['Location']
        # 登录请求
        request = urllib.request.Request(url=login_url, method='GET')
        html = self.opener.open(request).read().decode('utf-8')
        # 生成登录参数
        lt = re.search('name="lt" value="(.*?)"/>', html, re.S).group(1)
        execution = re.search('name="execution" value="(.*?)"/>', html, re.S).group(1)
        aes_key = re.search('pwdDefaultEncryptSalt = "(.*?)";', html, re.S).group(1)[:16].encode('utf-8')
        aes_chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
        iv = ''.join([random.choice(aes_chars) for _ in range(16)]).encode()
        raw = ''.join([random.choice(aes_chars) for _ in range(64)]) + self.password
        amount_to_pad = AES.block_size - (len(raw) % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        raw = (raw + chr(amount_to_pad) * amount_to_pad).encode()
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        password_aes = base64.b64encode(cipher.encrypt(raw))
        params = {'username': self.username, 'password': password_aes, 'lt': lt,
                  'dllt': 'userNamePasswordLogin',
                  'execution': execution, '_eventId': 'submit', 'rmShown': '1'}
        # 登录提交
        request = urllib.request.Request(url=login_url, method='POST',
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'))
        html = self.opener.open(request).read().decode('utf-8')
        self.AID = re.search("APPID='(.*?)';", html, re.S).group(1)
        # 登录判断
        if "USERID='" + self.username + "'" in html:
            print('[+] 登录成功')
            cookies_params = {'data': json.dumps({"APPID": self.AID, "APPNAME": 'szptpubxsjkxxbs'})}
            # 更新Cookie: _WEU
            cookies_request = urllib.request.Request(url=self.UPDATE_COOKIE_URL, data=urllib.parse.
                                                     urlencode(cookies_params).encode(encoding='UTF-8'),
                                                     method='POST', headers=self.header)  # 获取Cookie: _WEU
            self.opener.open(cookies_request)
            return 1
        elif not html:
            print('[-] 未登录，没有选择任何填报')
        elif "密码有误" in html:
            print("[-] 登录失败，您的用户名或密码有误")
        elif html.count("验证码") == 11:
            print("[-] 无法登录，需要验证码，请稍后再试或手动填报。")
        else:
            print("[-] 无法登录，未知错误，请检查网站是否能访问。")

    # 提交健康填报
    def send_info(self):
        print('[*] 健康填报 [*]')
        # URL
        get_user_info = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsjkxxbs/mrxxbs/getSaveReportInfo.do'
        send_user_info = 'https://ehall.szpt.edu.cn/publicappinternet/sys/szptpubxsjkxxbs/mrxxbs/saveReportInfo.do'
        # 获取个人信息json数据
        params = {'USER_ID': self.username}
        request = urllib.request.Request(url=get_user_info,
                                         data=urllib.parse.urlencode(params).encode(encoding='UTF-8'),
                                         method='POST', headers=self.header_getinfo)
        # 保存的参数
        response = self.opener.open(request)
        data = json.loads(response.read().decode('utf-8'))
        if 'WID' in data['datas']:
            print('[-] 今日已经填报！')
        else:
            if not data['datas'].get('SFYFS'):
                print('[-] 表单已更新，请重新填报！')
                return
            if 'WID' not in data['datas']:  # 每日首次提交，WID为空
                data['datas']['WID'] = ""
            # 需要填充的参数
            update_list = ['ZSDZ', 'SFZLKYJCHHSJCJGS', 'XGYMJZJJ', 'SFYYYXGYMJZ', 'WJZXGYMYY', 'YJZXGYMZJS']
            for i in update_list:
                data['datas'][i] = ''
            # 提交信息
            params = {'formData': data['datas']}
            request = urllib.request.Request(url=send_user_info,
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

    # 主入口
    def main(self):
        print('[*] ' + self.username + ' [*]')
        if self.login():
            self.send_info()


if __name__ == '__main__':
    username = ''  # 学号
    password = ''  # 一网通办密码
    cur = SZPT(username, password)
    cur.main()
