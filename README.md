# SZPT_Submit
SZPT每日健康填报及临时出校脚本  
基于[IamJankin](https://github.com/IamJankin)的[SZPT_Ehall](https://github.com/IamJankin/SZPT_Ehall)及[SZPT_ATLS](https://github.com/IamJankin/SZPT_ATLS)项目进行整合修改  

##环境
运行环境：[Python3](https://www.python.org/)  
第三方库：`pip install -r requirements.txt`  

##使用方法
```
python main.py username password flag
[*] username [*]
[+] 登录成功
[*] 健康填报 [*]
[+] 填报成功
[*] 临时出校 [*]
[+] 提交成功
```
flag由两位字符串组成，第一位为1则进行健康填报，为0反之；第二位为1则进行临时出校，为0同上。  

##注意
**若行程或相关防疫信息有变更请手动填报以更新表单。请务必配合防疫工作！！！
