# -*- coding=utf-8 -*-
import time,configparser,os,log,sys,re,random,pymysql,simplejson,json
import smtplib,traceback,requests,hashlib,json,base64
from selenium import webdriver
from progressbar import *
from email.mime.text import MIMEText
obj_log = log.get_logger()
configfile = 'config.ini'


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                            cls, *args, **kwargs)
        return cls._instance
class Tools(Singleton):
	def __init__(self):
		self.hallCode = "YTSG"
		self.customerId = 0
		# self.hallCode = raw_input("请输入客户代码：")
		# self.second_hallCode = sys.argv[2]
		self.all_config = self.init_allconfig(configfile)
		self.userName = self.all_config['username']
		self.password = self.all_config['pwd']
		self.ip = self.all_config['ip']
		self.port = self.all_config['port']
		self.my_user1 = self.all_config['my_user1']
		self.my_pwd1 = self.all_config['my_pwd1']
		# self.add = "39.108.170.48:8081"
		self.add = "47.106.254.243"
		self.app_add = "47.106.164.212:18081"
		# self.add = "192.168.28.10:8096"
		# self.app_add = "192.168.28.10:18081"


	def call_rest_api(self, API_URL, req_type,files=None,data_rtn=None, header=True,
					  		get_err_msg=True, token=None, timeout=None):
		retry_num = 5
		retry_interval_time = 10
		cnt = 0
		while cnt < retry_num:
			if token == None:
				'''此接口不需要token'''
				pass
			else:
				token = self.login_readerapp()
			headers = {
				'token': token,
				'Content-Type': 'application/json;charset=UTF-8'
			}
			try:
				if data_rtn != None:
					if req_type == "POST":
						values = json.dumps(data_rtn)
						# obj_log.info values

						req = requests.post(API_URL, data=values, headers=headers)
					elif req_type == "PUT":
						# obj_log.info API_URL
						values = json.dumps(data_rtn)
						req = requests.put(API_URL, data=values, headers=headers,timeout=timeout)

					elif req_type == "GET":
						# obj_log.info API_URL
						req = requests.get(API_URL, params=data_rtn, headers=headers,timeout=timeout)
					elif req_type == "DELETE":
						# obj_log.info API_URL
						req = requests.delete(API_URL, params=data_rtn, headers=headers,timeout=timeout)
				else:
					if req_type == "POST":
						values = json.dumps(data_rtn)
						req = requests.post(API_URL, headers=headers)

					elif req_type == "PUT":
						# obj_log.info API_URL
						req = requests.put(API_URL, headers=headers,timeout=timeout)

					elif req_type == "GET":
						obj_log.info(API_URL)
						req = requests.get(API_URL, headers=headers, timeout=timeout)
					elif req_type == "DELETE":
						obj_log.info(API_URL)
						req = requests.delete(API_URL, headers=headers, timeout=timeout)
			except Exception as e:
				if get_err_msg == True:
					try:
						return e.read()
					except Exception:
						return e
				continue
			if str(req.status_code) == "200":
				rtn_temp = req.text
				# rtn_temp = str(rtn_temp)
				# obj_log.info type(rtn_temp)
				rtn = json.loads(rtn_temp)
				req.close()
				return rtn
			else:
				obj_log.error("ERROR : Failed to requests API!")
				time.sleep(retry_interval_time)
				cnt += 1
				obj_log.error('retry: %d' % cnt)
				req.close()

		return False

	def login_readerapp(self,idCard='510722199003150950',idPassword='e10adc3949ba59abbe56e057f20f883e'):
		'''读者APP登陆'''
		temp_dict = {}
		temp_dict['idCard'] = idCard
		temp_dict['idPassword'] = idPassword
		values = json.dumps(temp_dict)
		API_URL = "http://" + self.app_add + "/userApp/reader/login"
		headers = {
			'Content-Type': 'application/json;charset=UTF-8'
		}
		req = requests.post(API_URL, data=values, headers=headers)
		if str(req.status_code) == "200":
			obj_log.info('登陆读者APP成功.......')
			rtn_temp = req.text
			rtn = json.loads(str(rtn_temp))
			rtn = rtn['data']['token']
			print(rtn)
			req.close()
			return rtn
		else:
			obj_log.info('读者APP登陆失败.......')
			return False


	def progressbar_k(self, sleep_time):
		widgets = ['Progress: ', Percentage(), ' ', Bar(marker=RotatingMarker('>-=')),' ', ETA()]
		pbar = ProgressBar(widgets=widgets, maxval=sleep_time).start()
		for i in range(sleep_time):
			pbar.update(1*i+1)
			time.sleep(1)
			pbar.finish()

	def get_md5(self, str):
		m = hashlib.md5()
		m.update(str.encode("utf8"))
		md5 = m.hexdigest()
		return md5
	def get_imgbas64(self, path):
		img = open(path, 'rb')
		img_bas64 = base64.b64encode(img.read())
		img.close()
		'''b 表示 byte的意思，将byte转换回去'''
		return str(img_bas64,'utf-8')

	def get_files_path(self):
		path = (os.path.split(os.path.realpath(__file__)))[0] + '\\' + "img"
		return path

	def listdir(self):  # 传入存储的list
		list_name = []
		path = self.get_files_path()
		for file in os.listdir(path):
			file_path = os.path.join(path, file)
			if os.path.isdir(file_path):
				listdir(file_path, list_name)
			else:
				list_name.append(file_path)
		return list_name

	def init_allconfig(self, configfile):
		ip = self.get_config(self.hallCode, 'ip', configfile)
		username = self.get_config(self.hallCode, 'username', configfile)
		port = self.get_config(self.hallCode, 'port', configfile)
		pwd = self.get_config(self.hallCode, 'pwd', configfile)
		my_user1 = self.get_config('user1', 'idCard', configfile)
		my_pwd1 = self.get_config('user1', 'pwd', configfile)
		all_config = {}
		all_config['hallCode'] = self.hallCode
		all_config['username'] = username
		all_config['port'] = port
		all_config['pwd'] = pwd
		all_config['ip'] = ip
		all_config['my_user1'] = my_user1
		all_config['my_pwd1'] = my_pwd1
		return all_config

	def get_config(self, section, key, configfile):
		config = configparser.ConfigParser()
		path = (os.path.split(os.path.realpath(__file__)))[0] + '/' + configfile
		config.read(path)
		# section = config.sections()
		# options = config.options(self.hallCode)
		# item = config.items(self.hallCode)
		rtn = config.get(section, key)
		return rtn

	def sql_event(self, statement):
		sql_type = statement.split(" ")[0]
		# conn = MySQLdb.connect(
		# 	host='rm-wz91b2j3ypnw1fbr6o.mysql.rds.aliyuncs.com',
		# 	port=3306,
		# 	user='chensq',
		# 	passwd='shi1!2@chen3com',
		# 	charset='utf8',
		# 	db='bookplatform',
		# )

		# conn = MySQLdb.connect(
		# 	host='192.168.28.10',
		# 	port=3306,
		# 	user='root',
		# 	passwd='123456',
		# 	charset='utf8',
		# 	db='bookplatform_back',
		# )

		conn = pymysql.connect(
			host='120.77.80.162',
			port=3306,
			user='test',
			passwd='123456',
			charset='utf8',
			db='bookplatform_test',
			cursorclass=pymysql.cursors.DictCursor
		)
		try:
			obj_log.info("Get or change the data into MySql............")
			obj_log.info(statement)
			cur = conn.cursor()
			a = cur.execute(statement)
		except Exception as e:
			obj_log.info(e)
		if sql_type in ("SELECT","select"):
			info = cur.fetchmany(a)
			rtn = list(info)
			cur.close()
			conn.close()
			return rtn
		else:
			conn.commit()
			cur.close()
			conn.close()
			return True

	def sql_event_no_dic(self, statement):
		sql_type = statement.split(" ")[0]
		# conn = MySQLdb.connect(
		# 	host='rm-wz91b2j3ypnw1fbr6o.mysql.rds.aliyuncs.com',
		# 	port=3306,
		# 	user='chensq',
		# 	passwd='shi1!2@chen3com',
		# 	charset='utf8',
		# 	db='bookplatform',
		# )

		# conn = MySQLdb.connect(
		# 	host='192.168.28.10',
		# 	port=3306,
		# 	user='root',
		# 	passwd='123456',
		# 	charset='utf8',
		# 	db='bookplatform_back',
		# )

		# conn = MySQLdb.connect(
		# 	host='rm-wz91b2j3ypnw1fbr6o.mysql.rds.aliyuncs.com',
		# 	port=3306,
		# 	user='yuntutest',
		# 	passwd='y!unTu@123',
		# 	charset='utf8',
		# 	db='bookplatform_test',
		# )

		conn = pymysql.connect(
			host='120.77.80.162',
			port=3306,
			user='test',
			passwd='123456',
			charset='utf8',
			db='bookplatform_test',
		)

		try:
			obj_log.info("Get or change the data into MySql............")
			cur = conn.cursor()
			a = cur.execute(statement)
		except Exception as e:
			obj_log.info(e)
		if sql_type in ("SELECT","select"):
			info = cur.fetchmany(a)
			rtn = list(info)
			cur.close()
			conn.close()
			return rtn
		else:
			conn.commit()
			cur.close()
			conn.close()
			return True

	def send_mail(self,to_list,bodyFile="" ,sub='QA Report',MAIL_HOST="smtp.163.com",MAIL_USER="18782019436@163.com",MAIL_PWD="lyp594797433",MAILTO_FROM='18782019436@163.com'):
		if bodyFile != "":
			f = open(bodyFile, 'r')
			msg = MIMEText(f.read(), 'html', 'utf8')
			f.close()
		else:
			print('File is empty!')
		msg['Subject'] = sub
		msg['From'] = MAILTO_FROM
		msg['To'] = ";".join(to_list)
		try:
			server = smtplib.SMTP(MAIL_HOST)
			#server.connect(MAIL_HOST,MAIL_PORT)
			server.starttls()
			server.login(MAIL_USER, MAIL_PWD)
			server.sendmail(MAILTO_FROM, to_list, msg.as_string())
			server.close()
			return True
		except Exception as e:
			print(str(e))
			return False

	'''Excel文件操作 '''
	'''**************************************************************************************************************'''
	'''Excel 文件读取'''
	def dict_data(self, excelPath, indexOrName=0):
		self.data = xlrd.open_workbook(excelPath)
		try:
			self.table = self.data.sheet_by_name(indexOrName)
		except Exception as e:
			if type(indexOrName) is not int:
				indexOrName = int(indexOrName)
			self.table = self.data.sheet_by_index(indexOrName)

		# 获取第一行作为key值
		self.keys = self.table.row_values(0)
		# 获取总行数
		self.rowNum = self.table.nrows
		# 获取总列数
		self.colNum = self.table.ncols
		if self.rowNum <= 1:
			print("总行数小于1")
		else:
			res_list = []
			j = 1
		for i in range(self.rowNum - 1):
			s = {}
			# 从第二行取对应values值
			values = self.table.row_values(j)
			for x in range(self.colNum):
				s[self.keys[x]] = values[x]
			res_list.append(s)
			j += 1
		return res_list

	def export_ToExcle(self, statement, outputpath):
		# conn = MySQLdb.connect(
		# 	host='192.168.28.10',
		# 	port=3306,
		# 	user='root',
		# 	passwd='123456',
		# 	charset='utf8',
		# 	db='bookplatform',
		# )

		conn = MySQLdb.connect(
			host='rm-wz91b2j3ypnw1fbr6o.mysql.rds.aliyuncs.com',
			port=3306,
			user='yuntutest',
			passwd='y!unTu@123',
			charset='utf8',
			db='bookplatform_back',
		)
		conn = MySQLdb.connect(
			host='rm-wz91b2j3ypnw1fbr6o.mysql.rds.aliyuncs.com',
			port=3306,
			user='ceshiuser',
			passwd='U%#Ceshi47io45',
			charset='utf8',
			db='bookplatform',
		)
		cursor = conn.cursor()
		try:
			print("Get or change the data into MySql............")
			count = cursor.execute(statement)
		except Exception as e:
			print(e)
		if count == 0:
			print(statement)
			return False
		# 重置游标的位置
		cursor.scroll(0, mode='absolute')

		# 搜取所有结果
		results = cursor.fetchall()
		# 获取MYSQL里面的数据字段名称
		fields = cursor.description
		workbook = xlwt.Workbook()
		sheet = workbook.add_sheet('table_message', cell_overwrite_ok=True)
		# 写上字段信息
		for field in range(0, len(fields)):
			sheet.write(0, field, fields[field][0])
		# 获取并写入数据段信息
		row = 1
		col = 0
		print (str(len(results)) + "  " + outputpath)
		for row in range(1, len(results) + 1):
			for col in range(0, len(fields)):
				sheet.write(row, col, u'%s' % results[row - 1][col])
		workbook.save(outputpath)

	# r'datetest.xls'
	def combineExcel(self, indexOrName=0):
		filelocation = (os.path.split(os.path.realpath(__file__)))[0] + "\\"
		biaotou = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
		fileform = "xls"
		filedestination = filelocation
		file = "combine_file"
		filearray = []
		for filename in glob.glob(filelocation + "*." + fileform):
			filearray.append(filename)

		ge = len(filearray)
		matrix = [None] * ge
		for i in range(ge):
			fname = filearray[i]
			workbook_open = xlrd.open_workbook(fname)

			try:
				sh = workbook_open.sheet_by_name(indexOrName)
			except Exception as e:
				if type(indexOrName) is not int:
					indexOrName = int(indexOrName)
				sh = workbook_open.sheet_by_index(indexOrName)

			nrows = sh.nrows
			# if nrows - 1 != 60:
			# 	print('................{0}...{1}'.format(nrows - 1, fname))
			matrix[i] = [0] * (nrows - 1)
			ncols = sh.ncols
			for m in range(nrows - 1):
				matrix[i][m] = ["0"] * ncols

			for j in range(1, nrows):
				for k in range(0, ncols):
					matrix[i][j - 1][k] = sh.cell(j, k).value
		filename = xlwt.Workbook()
		sheet = filename.add_sheet("test")

		for i in range(0, len(biaotou)):
			sheet.write(0, i, biaotou[i])

		zh = 1
		for i in range(ge):
			for j in range(len(matrix[i])):
				for k in range(len(matrix[i][j])):
					sheet.write(zh, k, matrix[i][j][k])
				zh = zh + 1

		filename.save(filedestination + file + ".xls")