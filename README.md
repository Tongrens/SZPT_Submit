# SZPT_Submit
SZPT每日健康填报及临时出校脚本  
基于[IamJankin](https://github.com/IamJankin)的[SZPT_Ehall](https://github.com/IamJankin/SZPT_Ehall)及[SZPT_ATLS](https://github.com/IamJankin/SZPT_ATLS)项目进行整合修改  

## 环境
运行环境：[Python3](https://www.python.org/)  
第三方库：`pip install -r requirements.txt`  

## 使用方法
```
python run.py
[*] 21180097 [*]
[+] 登录成功
[*] 健康填报 [*]
[+] 填报成功
[*] 临时出校 [*]
[+] 提交成功
[*] 三码填报 [*]
[*] 获取用户信息 [*]
[+] 提交成功
[*] 核酸签到 [*]
[+] 签到成功
```
flag由4位0&1组成，分别代表健康填报、临时出校、三码填报、核酸签到，每位代表一项，1代表提交，0代表不提交。

## 注意
**若行程或相关防疫信息有变更请手动填报以更新表单。请务必配合防疫工作！！！**
