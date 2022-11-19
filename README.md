# SZPT_Submit
SZPT自动填报信息脚本
基于[IamJankin](https://github.com/IamJankin)的[SZPT_Ehall](https://github.com/IamJankin/SZPT_Ehall)及[SZPT_ATLS](https://github.com/IamJankin/SZPT_ATLS)项目进行整合修改  

## 环境
运行环境：[Python3](https://www.python.org/)  
第三方库：`pip install -r requirements.txt`  

## 使用方法
```
# run.py
if __name__ == '__main__':
    username = ''   # 学号
    password = ''   # 一网通办密码
    flag = '1111'   # 由4位0&1组成，分别代表健康填报、临时出校、三码填报、核酸签到，每位代表一项，1代表提交，0代表不提交
    cur = SZPT(username, password, flag)
    cur.main()
```

```
python run.py
[*] 2118000 [*]
[+] 登录成功
[*] 健康填报 [*]
[+] 填报成功
[*] 临时出校 [*]
[+] 提交成功
[*] 三码填报 [*]
[+] 提交成功
[*] 核酸签到 [*]
[+] 签到成功
```

## 注意
**若行程或相关防疫信息有变更请手动填报以更新表单。**

## 免责声明
**此脚本仅供学习，禁止将脚本用于违法用途，任何因使用本脚本造成的违法行为均与开发者无关！**

**请务必配合防疫工作！！！**
