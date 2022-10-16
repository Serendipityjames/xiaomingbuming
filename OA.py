import time
import base64
import time,getpass,sys,os,re


try:
	from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
	from Crypto.PublicKey import RSA
	import requests
except:
	os.system('pip3 install requests')
	os.system('pip3 install pycryptodome')


url_rsa = 'https://oa.luxshare-ict.com/rsa/weaver.rsa.GetRsaInfo'
url_op = 'https://oa.luxshare-ict.com/luxshare/other/login_operation.jsp'
url_login = 'https://oa.luxshare-ict.com/login/VerifyLogin.jsp'
url_main = 'https://oa.luxshare-ict.com/wui/main.jsp'
url_get_id = 'https://oa.luxshare-ict.com/data.jsp?type=1&f_weaver_belongto_userid=&f_weaver_belongto_usertype=null&bdf_wfid=3461&bdf_fieldid=21159&bdf_viewtype=0'
url_get_info = 'https://oa.luxshare-ict.com/luxshare/workflow/rlgl/hr013/hr013_operation.jsp'
url_get_jx = 'https://oa.luxshare-ict.com/luxshare/workflow/rlgl/hr015/hr015_operation.jsp'
urlImg = 'https://oa.luxshare-ict.com/weaver/weaver.file.FileDownload'
urlPhone = 'https://oa.luxshare-ict.com/hrm/resource/simpleHrmResourceTemp.jsp'



headers = {
	'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
}
headers2 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}




def encrpt(password, public_key):
    public_key = '-----BEGIN PUBLIC KEY-----\n' + public_key + '\n-----END PUBLIC KEY-----'
    rsakey = RSA.importKey(public_key)
    cipher = Cipher_pksc1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(password.encode()))
    return cipher_text.decode()


def author(session):
	loginid = str(input("认证中......\n请输入您的工号，并确认：\n")).strip()
	pwd = str(getpass.getpass("认证中......\n请输入您的密码，并确认：\n")).strip()
	params = {'ts':str(time.time()).replace('.','')[:-4]}
	response = session.get(url=url_rsa,params=params).json()
	rsa_key =pwd + response['rsa_code']
	userpwd = encrpt(rsa_key,response['rsa_pub'])+response['rsa_flag']
	login_data = {
		'loginid': loginid,
		'userpassword': userpwd,
		'submit': '登录',
		'fontName': '微软雅黑',
		'formmethod': 'post',
		'isie': 'false',
		'logintype': 1,
	}
	response = session.post(url= url_login,data=login_data,headers=headers)
	if "登录异常，请联系管理员!" in response.text:
		return Ture, session
	else:
		return False, session


def getCookieFromLocal():
	text = ''
	try:
		with open('./cookie.txt','r') as reader:
			text = reader.read().strip()
	finally:
		return text


def wirteCookieToLocal(cookie):
	with open('./cookie.txt','w') as writer:
		writer.write(cookie)


def get_cookie(session):
	flag = True
	while flag:
		flag,session = author(session)
		if flag == False:
			ecology_JSessionId = session.cookies['ecology_JSessionId']
			wirteCookieToLocal(ecology_JSessionId)
			return ecology_JSessionId,session
		else:
			print('用户名或密码错误,请重试！')



ecology_JSessionId = getCookieFromLocal()
session = requests.session()
while True:
    cookie = {"ecology_JSessionId":ecology_JSessionId}
    query_info = input("输入你想要查询的关键字（工号，姓名，等）\n")
    if query_info == "Q":
        print("Bye, 欢迎再次使用！")
        sys.exit()
    from_data_id = {'q':query_info}

    response = session.post(url=url_get_id,data=from_data_id,cookies=cookie)
    reslut_req = response.text
    if 'Login.jsp' in reslut_req:
        print("Cookie过期! 正在重新抓取Cookie，过程中需要认证工号及密码，请稍等。。。")
        ecology_JSessionId,session = get_cookie(session)
        continue
    query_list = response.json()
    if len(query_list) == 0:
        print("查无此人！请重新输入关键词。。。 ")
        continue
    for i in query_list:
        print("姓名: "+i['name']+" 。。。。。查询ID: 》》 "+i['id']+" 《《 。。。。。部门名称: " + i['departmentname'])

    query_ID = input("输入您想查询的查询ID : \n").strip()

    formdata_info = {'operation':'getUser','xingm':query_ID}
    formdata_jx = {'operation':'getNiandkh','shenqr':query_ID}

    response_info = session.post(url=url_get_info,data=formdata_info,cookies=cookie)
    response_jx = session.post(url=url_get_jx,data=formdata_jx,cookies=cookie)
    jx_list = response_jx.json()
    info_dict = response_info.json()
    responsePhone = session.post(url=urlPhone,cookies=cookie,headers=headers,data={'userid':query_ID}).text.strip()
    #print(responsePhone)
    phonePattern = r'^1([0-9]){10}'
    imgIDPattern = r'^imageid=([0-9])*'
    phone = ''
    imageID = ''
    moreInfo = responsePhone.split('$$$')
    for info in moreInfo:
        if re.match(phonePattern,info) != None:
            phone = info
        if re.match(imgIDPattern,info) != None:
            imageID = info.split('=')[1]


    if len(info_dict) == 0:
        print("输入的ID有误，请重新查询。")
        continue
    print("========================== "+info_dict['workcode']+" =================================")
    print('工号：'+info_dict['workcode'])
    print('年龄(周岁)：'+info_dict['age'])
    print('级别：'+info_dict['zhij'])
    print('学历：'+info_dict['degree'])
    print('专业：'+info_dict['zhuany'])
    print('毕业院校：'+info_dict['cpf26'])
    if phone != '':
        print('手机号码: '+phone)
    print('直属主管：'+info_dict['managerName'])
    print('部门名称：'+info_dict['departmentName'])
    print('职位：'+info_dict['zhiw'])
    print('岗位：'+info_dict['gangwei'])
    print('入职日期：'+info_dict['shiyqj'])
    for jx in jx_list:
        print('绩效：'+jx['niand']+' >>> '+jx['shangsjpdj'])

    params={'fileid':imageID}
    responseImg = session.get(url=urlImg,headers=headers2,cookies=cookie,params=params)
    if responseImg.status_code == 200:
        if not os.path.exists('./Pic/'):
            os.mkdir('./Pic/')
        workID = info_dict['workcode']
        imgPath = './Pic/'+workID+'.jpg'
        with open(imgPath,'wb') as fp:
            fp.write(responseImg.content)
        os.popen('open '+imgPath)




