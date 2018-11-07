# -*- coding=utf-8 -*-
import utils,time,log,re,sys,json,simplejson,random,requests,threading
obj_log = log.get_logger()

class Runner:
	def __init__(self, all_config):
		self.obj_tools = utils.Tools()
		# self.hallCode =  self.obj_utils.hallCode
		self.user = all_config['username']
		self.pwd = all_config['pwd']
		self.port = all_config['port']
		self.ip = all_config['ip']
		self.my_user1 = all_config['my_user1']
		self.my_pwd1 = all_config['my_pwd1']
		self.add = self.obj_tools.add
		self.customerId = self.obj_tools.customerId
	'''客户角色新增操作'''

	def _role_add(self, hallcode, menu_id):
		req_type = 'POST'
		default_menu_id = ["37"]
		'''资讯'''
		if menu_id == "15":
			default_menu_id.append("16")
		if menu_id == "17":
			default_menu_id.append("16")
		'''读友会'''
		if menu_id == "18":
			default_menu_id.append("19")
		if menu_id == "20":
			default_menu_id.append("19")
		'''消息'''
		if menu_id == "33":
			default_menu_id.append("34")
		if menu_id == "35":
			default_menu_id.append("34")
		temp_dict = {}
		user_menuId_list = []
		now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
		sql_statement = "SELECT id,userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
		login_info = self.obj_tools.sql_event(sql_statement)
		admin_customer_password = login_info[0]['password']
		admin_customer_username = login_info[0]['userName']
		currentUserId = login_info[0]['id']
		token = self.obj_tools.loginYunyun(hallcode, admin_customer_username, admin_customer_password)
		temp_dict['currentUserId'] = currentUserId
		temp_dict['name'] = hallcode + '-name-' + now_time
		temp_dict['description'] = hallcode + '-desc-' + now_time
		default_menu_id.append(menu_id)
		temp_dict['menuIds'] = default_menu_id
		API_URL = "http://" + self.add + "/api/roleMenu/saveRoleMenu"
		req = self.obj_tools.call_rest_api(API_URL,req_type,data_rtn=temp_dict,token=token)
		if req['status'] == 200:
			obj_log.info('Add role {} successfully........'.format(temp_dict['name']))
		else:
			obj_log.info('Add role {} failed.......'.format(temp_dict['name']))
			return False

		return temp_dict['name']

	def _user_add(self, hallcode, role_id):
		req_type = 'POST'
		now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time()))
		sql_statement = "SELECT userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"

		login_info = self.obj_tools.sql_event(sql_statement)
		admin_customer_password = login_info[0]['password']
		admin_customer_username = login_info[0]['userName']
		token = self.obj_tools.loginYunyun(hallcode, admin_customer_username, admin_customer_password)
		temp_dict = {}
		temp_dict['hallCode'] = hallcode
		temp_dict['departmentDto'] = {}
		temp_dict['departmentDto']['deptName'] = '部门1'
		if hallcode != "YTSG":
			customer_id_statement = "SELECT id from system_customer WHERE hallCode = " + "'" + hallcode + "'"
			customer_id = self.obj_tools.sql_event(customer_id_statement)
			customer_id = customer_id[0]['id']
			dept_id_statement = "SELECT id FROM system_user_department WHERE customerId = " + str(customer_id) + " AND deptName = " + \
								"'" + temp_dict['departmentDto']['deptName'] + "'"
		else:
			dept_id_statement = "SELECT id FROM system_user_department WHERE customerId = " + str(self.customerId) + " AND deptName = " + \
								"'" + temp_dict['departmentDto']['deptName'] + "'"
		dept_id = self.obj_tools.sql_event(dept_id_statement)
		dept_id = dept_id[0]['id']
		temp_dict['departmentDto']['id'] = dept_id
		temp_dict['dutyDto'] = {}
		temp_dict['dutyDto']['dutyName'] = '职务1'
		duty_id_statement = "SELECT id FROM system_user_duty WHERE deptId = " + str(dept_id) + " AND dutyName = " + \
							"'" + temp_dict['dutyDto']['dutyName'] + "'"
		dept_id = self.obj_tools.sql_event(duty_id_statement)
		dept_id = dept_id[0]['id']
		temp_dict['dutyDto']['id'] = dept_id
		temp_dict['roleId'] = role_id
		temp_dict['sex'] = "1"
		temp_dict['userName'] = hallcode + '-new-' + now_time
		temp_dict['phone'] = '13980004762'
		temp_dict['tel'] = '13980004762'
		temp_dict['chat'] = '13980004762@163.com'
		API_URL = "http://" + self.add + "/api/user/saveSystemUser"
		req = self.obj_tools.call_rest_api(API_URL,req_type,data_rtn=temp_dict,token=token)
		if req['status'] == 200:
			obj_log.info('Add user %s successfully........' % (temp_dict['userName']))
			update_user_statement = "UPDATE system_user set is_first_login = 1 WHERE hallCode = '" + hallcode + "' and userName = '" + \
									temp_dict['userName'] + "'"
			update_user_status = self.obj_tools.sql_event(update_user_statement)

		else:
			obj_log.info('Add user %s failed.......'% (temp_dict['userName']))
			return False

		return temp_dict['userName']

	def _upload_image(self):
		API_URL = "http://" + self.add + "/api/image/uploadImageSaveOrUpdate"
		image_list = self.obj_tools.listdir()
		image_path = random.choice(image_list)
		print(image_path)
		files = {'fileImage': ("11.png", open(image_path, 'rb'), 'image/png')}
		obj_log.info('Upload image start.......')
		req = requests.post(API_URL, files=files)
		if req.status_code == 200:
			obj_log.info('Upload image successfully.......')
		else:
			obj_log.info('Upload image failed.......')
			return False
		rtn_temp = req.text
		rtn = json.loads(rtn_temp)
		return rtn['data']

	def _new_audited(self, new_id):
		req_type = 'PUT'
		new_status_statement = "SELECT status from system_news WHERE id = " + str(new_id)
		get_new_status = self.obj_tools.sql_event(new_status_statement)
		new_status = get_new_status[0]['status']
		if new_status == 3:
			obj_log.info("The news need audit by second_level customer user........")
			hallcode_statement = "SELECT hallCode from system_customer WHERE id = (SELECT sourceId FROM system_news WHERE id = " + str(new_id) + ")"
			hallcode_name =  self.obj_tools.sql_event(hallcode_statement)

			# 根据new_id判断是不是客户代码 0：图书馆 其他：客户代码
			if len(hallcode_name) == 0:
				library_id_statement = "SELECT sourceId FROM system_news WHERE id = " + str(new_id)
				hallcode_id = self.obj_tools.sql_event(library_id_statement)
				library_id = hallcode_id[0]['sourceId']
				get_customer_statement = "SELECT hallCode from system_customer WHERE id = (SELECT customerId from librarys WHERE id = " + str(library_id) + ")"
				hallcode_temp = self.obj_tools.sql_event(get_customer_statement)
				hallcode = hallcode_temp[0]['hallCode']
			else:
				hallcode = hallcode_name[0]['hallCode']

			sql_statement = "SELECT id,userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
			login_info = self.obj_tools.sql_event(sql_statement)
			audited_user_password = login_info[0]['password']
			audited_user_username = login_info[0]['userName']
			audited_user_id = login_info[0]['id']
			token = self.obj_tools.loginYunyun(hallcode, audited_user_username, audited_user_password)
			API_URL = "http://" + self.add + "/api/news/" + str(new_id) + "/newAudited?currentUserId=" +  str(audited_user_id)
			req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
			if req['status'] == 200:
				obj_log.info('Audited second_level the new {} successfully........'.format(new_id))

			else:
				obj_log.info('Audited second_level the new {} failed........'.format(new_id))
				return False
		self.obj_tools.progressbar_k(2)
		get_new_status = self.obj_tools.sql_event(new_status_statement)
		new_status = get_new_status[0]['status']
		if new_status == 2:
			obj_log.info("The news need audit by primary_level customer user........")
			hallcode = "YTSG"
			sql_statement = "SELECT id,userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
			login_info = self.obj_tools.sql_event(sql_statement)
			audited_user_password = login_info[0]['password']
			audited_user_username = login_info[0]['userName']
			audited_user_id = login_info[0]['id']
			token = self.obj_tools.loginYunyun(hallcode, audited_user_username, audited_user_password)
			API_URL = "http://" + self.add + "/api/news/" + str(new_id) + "/newAudited?currentUserId=" + str(audited_user_id)
			req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
			print(req)
			if req['status'] == 200:
				obj_log.info('Audited primary_level the new {} successfully........'.format(new_id))
			else:
				obj_log.info('Audited primary_level the new {} failed........'.format(new_id))
				return False

		return True

	def _get_customer_user_info(self, hallcode, menu_id=""):
		power_list = []
		all_customer_statement = "SELECT id from system_user WHERE hallCode = " + "'" + hallcode + "'" + " AND isEffective = 1"
		all_customer_user = self.obj_tools.sql_event(all_customer_statement)
		user_info = []
		if menu_id == "":
			sql_statement = "SELECT id,userName,password from system_user WHERE hallCode = '" + hallcode + "' and remark = 1"
			user_info = self.obj_tools.sql_event(sql_statement)

		else:
			for i in range(len(all_customer_user)):
				for user in all_customer_user[i]:
					user_id = all_customer_user[i]['id']
					user_power_statement = "SELECT id FROM system_menu WHERE id in (\
											SELECT menuId FROM system_role_menu WHERE roleId = (\
											SELECT roleId from system_user_role WHERE userId = " + str(user_id) + "))"
					user_power_info = self.obj_tools.sql_event(user_power_statement)
					for i in user_power_info:
						power_list.append(i['id'])
					# 查看新增权限是否存在： 15 资讯新增权限
					if int(menu_id) in power_list:
						right_username_statement =  "SELECT id, userName, password from system_user WHERE hallCode = " + "'"\
													+ hallcode + "'" + " and id = " + str(user_id)
						user_info = self.obj_tools.sql_event(right_username_statement)
						break
		if len(user_info) == 0:
			obj_log.info("The customer {} have no user possess the power of add the news".format(hallcode))
			obj_log.info("Add the user with the power of add the news on customer {}. ".format(hallcode))
			# 新增有资讯新增权限的用户
			time.sleep(3)
			role_add_rtn = self._role_add(hallcode, menu_id)


			# 获取角色ID
			role_id_statement = "SELECT id FROM  system_role WHERE name = " + "'" + role_add_rtn + "'"
			role_id = self.obj_tools.sql_event(role_id_statement)
			role_id = role_id[0]['id']
			add_user_rtn = self._user_add(hallcode, role_id)
			right_add_username = "SELECT id, userName, password from system_user WHERE hallCode = " + "'" \
									   + hallcode + "'" + " and userName = " + "'" + add_user_rtn + "'"
			user_info = self.obj_tools.sql_event(right_add_username)
		else:
			name = user_info[0]['userName']
			obj_log.info("The customer user %s can add the news...." %(name))
		return user_info[0]
	def _get_firstcategory(self):
		req_type = 'GET'
		hallCode = "YTSG"
		first_category_rtn = {}
		first_category_list = []
		API_URL = "http://" + self.add + "/api/videosCategory/getFirstCategory"
		get_user_info = self._get_customer_user_info(hallCode)
		get_user = get_user_info['userName']
		get_pwd = get_user_info['password']
		token = self.obj_tools.loginYunyun(hallCode, get_user, get_pwd)
		req = self.obj_tools.call_rest_api(API_URL, req_type, token=token)
		if req['status'] == 200:
			obj_log.info('Get first category successfully........')
			first_category = req['data']
			for i in range(len(first_category)):
				first_category_id = first_category[i]['id']
				first_category_rtn[first_category_id] =first_category[i]['name']
		else:
			obj_log.info('Get first category failed.......')
			return False

		return first_category_rtn
	def _get_secondcategory(self):
		req_type = 'GET'
		hallCode = "YTSG"
		temp_dict = {}
		second_category_rtn = {}
		second_category_temp = []
		second_category_list = []
		first_category_list = self._get_firstcategory()
		API_URL = "http://" + self.add + "/api/videosCategory/getSecondCategory"
		get_user_info = self._get_customer_user_info(hallCode)
		get_user = get_user_info['userName']
		get_pwd = get_user_info['password']
		token = self.obj_tools.loginYunyun(hallCode, get_user, get_pwd)
		for id in first_category_list.keys():
			second_category_list = []
			temp_dict['id'] = id
			req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
			if req['status'] == 200:
				obj_log.info('Get second category successfully........')
				second_category_temp = req['data']
				for i in range(len(second_category_temp)):
					second_category_id = second_category_temp[i]['id']
					second_category_list.append(second_category_id)
			else:
				obj_log.info('Get second category failed.......')
				return False
			second_category_rtn[id] = second_category_list

		return second_category_rtn
	def _get_newfromdb(self,hallCode=None,areaCode=None):
		# 此方法返回所有和传入hallCode在同一省市区的所有资讯，按照平台，省级，市级，区县级，图书馆分类
		all_news_rtn = {}
		if hallCode:
			library_areacode = self._get_library_areacode(hallCode=hallCode)
		if areaCode:
			library_areacode = self._get_library_areacode(areaCode=areaCode)
		if library_areacode['areaCode'] == None or library_areacode['areaCode'] == "":
			platfrom_news_statement = '''SELECT '''+ ''' ''' +\
									  			'''sn.id,sn.sourceId,
												sn.title,
												sra.province_code,
												sra.city_code,
												sra.area_code,
												DATE_FORMAT(
													sn.create_time,
													'%Y%m%d%H%i%S'
												) AS c_time
											FROM
												system_news sn
											LEFT JOIN system_customer sc ON sn.sourceId = sc.id
											LEFT JOIN system_customer_level scl ON scl.id = sc.levelId
											LEFT JOIN system_relative_area sra ON sn.id = sra.relative_id
											LEFT JOIN system_province sp ON sra.province_code = sp. CODE
											LEFT JOIN system_city sci ON sra.city_code = sci. CODE
											LEFT JOIN system_area sa ON sra.area_code = sa. CODE
											WHERE
												sn. STATUS = 0
											AND sn.type = 1
											AND sra.relative_type = 0
											AND ((sra.city_code = ''' + library_areacode['cityCode'] +  \
												''' AND sra.area_code = 'all')
												OR (sra.province_code = ''' + library_areacode['provinceCode'] +  ''' AND sra.city_code = 'all')
												OR (sra.province_code = 'all')
											)
											ORDER BY c_time DESC'''
			area_news_statement = '''SELECT sn.id,
											sn.sourceId,
											sn.title,
											sra.province_code,
											sra.city_code,
											sra.area_code,
											DATE_FORMAT(
												sn.create_time,
												'%Y%m%d%H%i%S'
											) AS c_time
										FROM
											system_news sn
										LEFT JOIN system_customer sc ON sn.sourceId = sc.id
										LEFT JOIN system_customer_level scl ON scl.id = sc.levelId
										LEFT JOIN system_relative_area sra on sn.id = sra.relative_id
										LEFT JOIN system_province sp on sra.province_code = sp.code
										LEFT JOIN system_city sci on sra.city_code = sci.code
										LEFT JOIN system_area sa on sra.area_code = sa.code

										WHERE
											sn. STATUS = 0
										AND sc.levelId = 4
										and sra.relative_type = 0
										and sra.city_code = ''' + library_areacode['cityCode'] + '''
										ORDER BY c_time DESC'''
			library_news_statement = '''SELECT sn.id,
											sn.sourceId,
											sn.title,
											sra.province_code,
											sra.city_code,
											sra.area_code,
											DATE_FORMAT(
												sn.create_time,
												'%Y%m%d%H%i%S'
											) AS c_time
										FROM
											system_news sn
										LEFT JOIN system_customer sc ON sn.sourceId = sc.id
										LEFT JOIN system_customer_level scl ON scl.id = sc.levelId
										LEFT JOIN system_relative_area sra on sn.id = sra.relative_id
										LEFT JOIN system_province sp on sra.province_code = sp.code
										LEFT JOIN system_city sci on sra.city_code = sci.code
										LEFT JOIN system_area sa on sra.area_code = sa.code
										
										WHERE
											sn. STATUS = 0
										AND sn.type = 3
										and sra.relative_type = 0
										and sra.city_code = ''' + library_areacode['cityCode'] + '''
										ORDER BY c_time DESC'''
		else:
			platfrom_news_statement = '''SELECT '''+ ''' ''' +\
									  			'''sn.id,sn.sourceId,
												sn.title,
												sra.province_code,
												sra.city_code,
												sra.area_code,
												DATE_FORMAT(
													sn.create_time,
													'%Y%m%d%H%i%S'
												) AS c_time
											FROM
												system_news sn
											LEFT JOIN system_customer sc ON sn.sourceId = sc.id
											LEFT JOIN system_customer_level scl ON scl.id = sc.levelId
											LEFT JOIN system_relative_area sra ON sn.id = sra.relative_id
											LEFT JOIN system_province sp ON sra.province_code = sp. CODE
											LEFT JOIN system_city sci ON sra.city_code = sci. CODE
											LEFT JOIN system_area sa ON sra.area_code = sa. CODE
											WHERE
												sn. STATUS = 0
											AND sn.type = 1
											AND sra.relative_type = 0
											AND (sra.area_code = ''' + library_areacode['areaCode'] +  \
												''' OR (sra.city_code = ''' + library_areacode['cityCode'] +  \
												''' AND sra.area_code = 'all')
												OR (sra.province_code = ''' + library_areacode['provinceCode'] +  ''' AND sra.city_code = 'all')
												OR (sra.province_code = 'all')
											)
											ORDER BY c_time DESC'''

			area_news_statement = '''SELECT sn.id,
											sn.sourceId,
											sn.title,
											sra.province_code,
											sra.city_code,
											sra.area_code,
											DATE_FORMAT(
												sn.create_time,
												'%Y%m%d%H%i%S'
											) AS c_time
										FROM
											system_news sn
										LEFT JOIN system_customer sc ON sn.sourceId = sc.id
										LEFT JOIN system_customer_level scl ON scl.id = sc.levelId
										LEFT JOIN system_relative_area sra on sn.id = sra.relative_id
										LEFT JOIN system_province sp on sra.province_code = sp.code
										LEFT JOIN system_city sci on sra.city_code = sci.code
										LEFT JOIN system_area sa on sra.area_code = sa.code

										WHERE
											sn. STATUS = 0
										AND sc.levelId = 4
										and sra.relative_type = 0
										and sra.area_code = ''' + library_areacode['areaCode'] + '''
										ORDER BY c_time DESC'''
			library_news_statement = '''SELECT sn.id,
														sn.sourceId,
														sn.title,
														sra.province_code,
														sra.city_code,
														sra.area_code,
														DATE_FORMAT(
															sn.create_time,
															'%Y%m%d%H%i%S'
														) AS c_time
													FROM
														system_news sn
													LEFT JOIN system_customer sc ON sn.sourceId = sc.id
													LEFT JOIN system_customer_level scl ON scl.id = sc.levelId
													LEFT JOIN system_relative_area sra on sn.id = sra.relative_id
													LEFT JOIN system_province sp on sra.province_code = sp.code
													LEFT JOIN system_city sci on sra.city_code = sci.code
													LEFT JOIN system_area sa on sra.area_code = sa.code

													WHERE
														sn. STATUS = 0
													AND sn.type = 3
													and sra.relative_type = 0
													and sra.area_code = ''' + library_areacode['areaCode'] + '''
													ORDER BY c_time DESC'''

		province_news_statement = '''SELECT sn.id,
									sn.sourceId,
									sn.title,
									sra.province_code,
									sra.city_code,
									sra.area_code,
									DATE_FORMAT(
										sn.create_time,
										'%Y%m%d%H%i%S'
									) AS c_time
								FROM
									system_news sn
								LEFT JOIN system_customer sc ON sn.sourceId = sc.id
								LEFT JOIN system_customer_level scl ON scl.id = sc.levelId
								LEFT JOIN system_relative_area sra on sn.id = sra.relative_id
								LEFT JOIN system_province sp on sra.province_code = sp.code
								LEFT JOIN system_city sci on sra.city_code = sci.code
								LEFT JOIN system_area sa on sra.area_code = sa.code
								
								WHERE
									sn. STATUS = 0
								AND sc.levelId = 2
								and sra.relative_type = 0
								and sra.province_code = ''' + library_areacode['provinceCode'] + '''
								ORDER BY c_time DESC'''
		city_news_statement = '''SELECT sn.id,
								sn.sourceId,
								sn.title,
								sra.province_code,
								sra.city_code,
								sra.area_code,
								DATE_FORMAT(
									sn.create_time,
									'%Y%m%d%H%i%S'
								) AS c_time
							FROM
								system_news sn
							LEFT JOIN system_customer sc ON sn.sourceId = sc.id
							LEFT JOIN system_customer_level scl ON scl.id = sc.levelId
							LEFT JOIN system_relative_area sra on sn.id = sra.relative_id
							LEFT JOIN system_province sp on sra.province_code = sp.code
							LEFT JOIN system_city sci on sra.city_code = sci.code
							LEFT JOIN system_area sa on sra.area_code = sa.code
							
							WHERE
								sn. STATUS = 0
							AND sc.levelId = 3
							and sra.relative_type = 0
							and sra.city_code = ''' + library_areacode['cityCode'] + '''
							ORDER BY c_time DESC'''


		platfrom_news_info = self.obj_tools.sql_event(platfrom_news_statement)
		province_news_info = self.obj_tools.sql_event(province_news_statement)
		city_news_info = self.obj_tools.sql_event(city_news_statement)
		area_news_info = self.obj_tools.sql_event(area_news_statement)
		library_news_info = self.obj_tools.sql_event(library_news_statement)
		platfrom_news_list = []
		province_news_list = []
		city_news_list = []
		area_news_list = []
		library_news_list = []
		# 平台资讯list
		for i in range(len(platfrom_news_info)):
			platfrom_news_list.append(platfrom_news_info[i]['id'])
		# 省级资讯list
		for i in range(len(province_news_info)):
			province_news_list.append(province_news_info[i]['id'])
		# 市级资讯list
		for i in range(len(city_news_info)):
			city_news_list.append(city_news_info[i]['id'])
		# 区县级资讯list
		for i in range(len(area_news_info)):
			area_news_list.append(area_news_info[i]['id'])
		# 图书馆资讯list
		for i in range(len(library_news_info)):
			library_news_list.append(library_news_info[i]['id'])
		all_news_rtn['platfrom_news'] = platfrom_news_list[:6]
		all_news_rtn['province_news'] = province_news_list
		all_news_rtn['city_news'] = city_news_list
		all_news_rtn['area_news'] = area_news_list
		all_news_rtn['library_news'] = library_news_list
		return all_news_rtn
	def _get_library_areacode(self, hallCode=None,areaCode=None):
		if hallCode:
			library_areacode_statement = "SELECT provinceCode,cityCode,areaCode from librarys WHERE hallCode = '" + hallCode + "'"
		if areaCode:
			library_areacode_statement = '''SELECT sp.code as provinceCode ,sc.code as cityCode,sa.code as areaCode FROM system_area sa 
											LEFT JOIN system_city sc on sa.cityCode = sc.code 
											LEFT JOIN system_province sp on sc.provinceCode = sp.code
											WHERE sa.code = ''' +  areaCode

			print(library_areacode_statement)
		library_areacode = self.obj_tools.sql_event(library_areacode_statement)
		if library_areacode == []:
			library_areacode_statement = '''SELECT sp.code as provinceCode ,sc.code as cityCode FROM system_city sc 
											LEFT JOIN system_province sp on sc.provinceCode = sp.code
											WHERE sc.code = ''' + areaCode
			library_areacode = self.obj_tools.sql_event(library_areacode_statement)
			library_areacode[0]['areaCode'] = ""
		return library_areacode[0]


	def _get_allperuser(self):
		'''从library_ebook_reader获取peruser'''
		peruser_statement = '''SELECT DISTINCT peruser FROM library_ebook_reader'''
		peruser_rtn = self.obj_tools.sql_event(peruser_statement)
		return peruser_rtn[0]

	def _get_ebook_allocated(self):
		'''从library_ebook获取已分配的电子书'''
		sql_statement = '''SELECT DISTINCT ebook_id
							FROM
								library_ebook
							WHERE
								(
									ebook_id IS NOT NULL
									OR ebook_id != ""
								)'''
		sql_rtn = self.obj_tools.sql_event(sql_statement)
		return sql_rtn[0]

	def _get_hallcode_ebookallocated(self,ebook_id):
		'''获取某本电子书已分配的图书馆（读者app能够显示的馆）'''
		sql_statement = '''SELECT
							librarys.hallCode
						FROM
							library_ebook,
							librarys
						WHERE
							library_ebook.library_id = librarys.id
						AND library_ebook.ebook_id = ''' + str(ebook_id) + '''
						AND librarys.libraryStatus = '1'
						AND librarys.isShield = 0 AND librarys.isEffective = 1
						AND (
							librarys.hasEbook = 1
							OR librarys.hasEffectiveBook = 1
						)
						AND librarys.lngLat != ''
						AND librarys.lngLat IS NOT NULL '''
		sql_rtn = self.obj_tools.sql_event(sql_statement)
		return sql_rtn[0]

	def _get_hallcode_ebookhadkread(self,ebook_id):
		'''获取某本电子书已阅读的图书馆（读者app能够显示的馆）'''
		sql_statement = '''SELECT hall_code
					FROM
						library_ebook_reader
					WHERE
						ebook_id = ''' + str(ebook_id)
		sql_rtn = self.obj_tools.sql_event(sql_statement)
		return sql_rtn[0]





