# -*- coding=utf-8 -*-
import utils,runner,log,time,json,simplejson,random,threading,requests
# obj_tools = utils.Tools()
obj_log = log.get_logger()
isbn_list = {'A': '9787308156417', 'B': '9787516143261', 'C': '9787509745816', 'D': '9787040213607', 'E': '9787509755280', 'F': '9787516410790', 'G': '9787561466584',
			 'H': '9787561460207', 'I': '9787108032911', 'J': '9787561460232', 'K': '9787509748985','N': '9787030334282', 'O': '9787513535663', 'P': '9787500672012',
			 'Q': '9787502554774', 'R': '9787200008715', 'S': '9787030323859', 'T': '9787121212437', 'U': '9787111465300', 'V': '9787515901701', 'X': '9787511107633',
			 'Z': '9787500086062', 'Test_null': '123456789'}
class Test_case(runner.Runner):
	def __init__(self, all_config):
		runner.Runner.__init__(self, all_config)
		self.obj_tools = utils.Tools()
		self.app_add = self.obj_tools.app_add


	# 资讯新增 hallcode：客户代码 is_need_review：是否需要审核（0:需要 1：不需要）
	def new_add(self, hallcode=None, type="2", is_need_review=0, num=1):
		req_type = "PUT"
		if hallcode:
			hallcode = hallcode.upper()
		temp_dict = {}
		new_AreaDtos_list = []
		new_AreaDtos_rtn = {}
		get_customer_statement = "SELECT hallCode from system_customer WHERE id = (SELECT customerId from librarys WHERE hallCode = '" + hallcode + "')"
		hallcode_temp = self.obj_tools.sql_event(get_customer_statement)
		if hallcode_temp == []:
			customer_code = hallcode
		else:
			customer_code = hallcode_temp[0]['hallCode']
		# 单位资讯
		if type == "2":
			obj_log.info('Add new customer start................')

			sql_statement = "SELECT provinceCode,cityCode,areaCode FROM system_customer WHERE hallCode = " + "'" + hallcode + "'"
			customer_info_statement = "SELECT id, name from system_customer WHERE hallCode = " + "'" + hallcode + "'"
		# 图书馆资讯
		if type == "3":
			obj_log.info('Add new library start................')
			library = hallcode
			sql_statement = "SELECT provinceCode,cityCode,areaCode FROM librarys WHERE hallCode = " + "'" + library + "'"
			customer_info_statement = "SELECT id, name from librarys WHERE hallCode = " + "'" + library + "'"
		# 获取 newAreaDtos

		customer_info = self.obj_tools.sql_event(customer_info_statement)
		newAreaDtos_info = self.obj_tools.sql_event(sql_statement)
		areaAddress_container = ""
		for i in range(len(newAreaDtos_info)):
			new_AreaDtos_rtn['province'] = newAreaDtos_info[i]['provinceCode']
			if newAreaDtos_info[i]['cityCode'] is None:
				new_AreaDtos_rtn['city'] = "all"
			else:
				new_AreaDtos_rtn['city'] = newAreaDtos_info[i]['cityCode']

			if newAreaDtos_info[i]['areaCode'] is None:
				new_AreaDtos_rtn['area'] = "all"
			else:
				new_AreaDtos_rtn['area'] = newAreaDtos_info[i]['areaCode']
			new_AreaDtos_list.append(new_AreaDtos_rtn)
			temp_dict['newAreaDtos'] = new_AreaDtos_list
			print(temp_dict['newAreaDtos'])
			if newAreaDtos_info[i]['cityCode'] is None:
				province_statement = "SELECT name FROM system_province WHERE code = " + new_AreaDtos_rtn['province']
				province_name = self.obj_tools.sql_event(province_statement)
				province_name = province_name[0]['name']
				if i > 0:
					areaAddress_container = areaAddress_container + "," + province_name
					temp_dict['areaAddress'] = areaAddress_container
				else:
					temp_dict['areaAddress'] = province_name
					areaAddress_container = province_name
			elif newAreaDtos_info[0]['cityCode'] is not None and newAreaDtos_info[0]['areaCode'] is None:
				province_statement = "SELECT name FROM system_province WHERE code = " + new_AreaDtos_rtn['province']
				province_name = self.obj_tools.sql_event(province_statement)
				province_name = province_name[0]['name']
				city_statement = "SELECT name FROM system_city WHERE code = " + new_AreaDtos_rtn['city']
				city_name = self.obj_tools.sql_event(city_statement)
				city_name = city_name[0]['name']
				if i > 0:
					areaAddress_container = areaAddress_container + "," + province_name + city_name
					temp_dict['areaAddress'] = areaAddress_container
				else:
					temp_dict['areaAddress'] = province_name + city_name
					areaAddress_container = province_name + city_name

			else:
				province_statement = "SELECT name FROM system_province WHERE code = " + new_AreaDtos_rtn['province']
				province_name = self.obj_tools.sql_event(province_statement)
				province_name = province_name[0]['name']
				city_statement = "SELECT name FROM system_city WHERE code = " + new_AreaDtos_rtn['city']
				city_name = self.obj_tools.sql_event(city_statement)
				city_name = city_name[0]['name']
				area_statement = "SELECT name FROM system_area WHERE code = " + new_AreaDtos_rtn['area']
				area_name = self.obj_tools.sql_event(area_statement)
				area_name = area_name[0]['name']

				if i > 0:
					areaAddress_container = areaAddress_container + "," + province_name + city_name + area_name
					temp_dict['areaAddress'] = areaAddress_container
				else:
					temp_dict['areaAddress'] = province_name + city_name + area_name
					areaAddress_container = province_name + city_name + area_name
		print (temp_dict['areaAddress'])
		# 获取 当前用户ID-currentUserId
		get_add_user = self._get_customer_user_info(customer_code, menu_id="15")
		temp_dict['currentUserId'] = get_add_user['id']
		temp_dict['hight'] = '571'
		# 图片上传
		image_info = self._upload_image()
		temp_dict['image'] = image_info['fileName']
		temp_dict['previemImage'] = image_info['base64']
		# 资讯来源
		temp_dict['source'] = customer_info[0]['name']
		temp_dict['sourceId'] = customer_info[0]['id']
		# temp_dict['timestamp'] = ''

		temp_dict['type'] = type
		temp_dict['width'] = '1470'
		temp_dict['x'] = '0'
		temp_dict['y'] = '150'
		videos_info = {'1/2/1541385889912.mp4': ['218', '68086984']}
		videoUrl_list = list(videos_info.keys())
		videoUrl = random.choice(videoUrl_list)
		temp_dict['videoDuration'] = videos_info[videoUrl][0]
		temp_dict['videoSize'] = videos_info[videoUrl][1]
		temp_dict['videoUrl'] = "http://img.ytsg.cn/video/" + videoUrl
		temp_dict['objVal'] = temp_dict['areaAddress']
		API_URL = "http://" + self.add + "/api/news/newAdd"
		if type == "1":
			obj_log.info("We will add the platform news......")

		else:
			add_customer_username = get_add_user['userName']
			add_customer_password = get_add_user['password']

			for i in range(num):
				now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
				temp_dict['title'] = '标题-' + now_time
				temp_dict['content'] = "<p>" + "内容-" + now_time + "</p>"
				token = self.obj_tools.loginYunyun(customer_code, add_customer_username, add_customer_password)
				req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
				if req['status'] == 200:
					obj_log.info('Add new successfully........')
				else:
					obj_log.info('Add new failed.......')
					return False
				# 获取资讯ID
				get_newId_statement = "SELECT id FROM system_news WHERE sourceId = " + str(
					temp_dict['sourceId']) + " and title = '" + temp_dict['title'] + "'"
				new_id = self.obj_tools.sql_event(get_newId_statement)
				new_id = new_id[0]['id']
				# 资讯审核
				if is_need_review == 0:
					obj_log.info("The new is a customer_news,we need customer user audited it.....")
					sql_statement = "SELECT userName,password from system_user WHERE hallCode = '" + customer_code + "' and remark = 1"
					login_info = self.obj_tools.sql_event(sql_statement)
					admin_customer_password = login_info[0]['password']
					admin_customer_username = login_info[0]['userName']
					token = self.obj_tools.loginYunyun(customer_code, admin_customer_username, admin_customer_password)
					obj_log.info("News audited start...... ")
					new_audited_rtn = self._new_audited(new_id)
		return True
	def movie_upload(self):
		req_type = "PUT"
		now_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
		get_categoryId = self._get_secondcategory()
		temp_dict = {}
		videosChapterDtos_list = []
		videos_list = ["video/2/3/1531727269723.mp4", "video/0/5/1531727271305.mp4", "video/2/2/1531727272622.mp4", "video/2/6/1531727273726.mp4"]
		image_list = self.obj_tools.listdir()
		for k in range(1,3):
			videosSectionDtos_list = []
			videosChapterDtos_rtn = {}
			videosChapterDtos_rtn['sortNum'] = k
			videosChapterDtos_rtn['index'] = k - 1
			videosChapterDtos_rtn['name'] = "第" + str(k) + "章"
			videosChapterDtos_rtn['isParashow'] = "true"
			for i in range(1,3):
				videosSectionDtos_rtn = {}
				videosSectionDtos_rtn['name'] = "第" + str(k) + "章" +  "第" + str(i) + "节"
				videosSectionDtos_rtn['sortNum'] = i
				videosSectionDtos_rtn['index'] = i - 1
				videosSectionDtos_rtn['videoName'] = "第" + str(k) + "章" +  "第" + str(i) + "节" + "视频"
				videosSectionDtos_rtn['videoPath'] = random.choice(videos_list)
				videosSectionDtos_rtn['videoSize'] = 58707397
				videosSectionDtos_rtn['videoTime'] = "200"
				videosSectionDtos_rtn['isupload'] = "true"
				videosSectionDtos_list.append(videosSectionDtos_rtn)
			videosChapterDtos_rtn['videosSectionDtos'] = videosSectionDtos_list

			videosChapterDtos_list.append(videosChapterDtos_rtn)

		temp_dict['videosChapterDtos'] = videosChapterDtos_list
		temp_dict['videosStatus'] = {"index":3}
		firstCategoryId = random.choice(list(get_categoryId.keys()))
		temp_dict['firstCategoryId'] = firstCategoryId
		temp_dict['secondCategoryId'] = random.choice(get_categoryId[firstCategoryId])
		temp_dict['name'] = "视频名称" + now_time
		temp_dict['startTime'] = "2018-7-12"
		temp_dict['endTime'] = "2019-7-12"
		temp_dict['author'] = "lyp"
		temp_dict['content'] = "视频介绍" + now_time
		# image_temp = self.obj_tools.get_imgbas64(r"C:\Users\lyp\PycharmProjects\remote_yunyun_api\img\11.png")
		image_path = random.choice(image_list)
		image_temp = self.obj_tools.get_imgbas64(image_path)
		temp_dict['image'] = "data:image/png;base64," + str(image_temp)

		API_URL = "http://" + self.add + "/api/videos/save"
		print("***************************************")
		# get_user_info = self._get_customer_user_info(hallcode="YTSG", menu_id="89")
		# upload_customer_username = get_user_info['userName']
		# upload_customer_password = get_user_info['password']
		upload_customer_username = "lyp"
		upload_customer_password = "e10adc3949ba59abbe56e057f20f883e"
		token = self.obj_tools.loginYunyun(hallCode="YTSG", username=upload_customer_username, password=upload_customer_password)
		req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
		if req['status'] == 200:
			obj_log.info('Upload videos {} successfully........'.format(temp_dict['name']))
		else:
			obj_log.info('Upload videos failed.......')
			return False
		return True
	def vidoes_del(self):
		req_type = 'DELETE'
		hallCode = "YTSG"
		temp_dict= {}
		videosId_list = []
		videosId_list_statement = "SELECT id FROM `system_videos` where `name` LIKE '%视频名称%'"
		videosId_list_temp = self.obj_tools.sql_event(videosId_list_statement)
		print(videosId_list_temp)
		for temp in videosId_list_temp:
			videosId_list.append(temp['id'])
		for id in videosId_list:
			API_URL = "http://" + self.add + "/api/videos/del/" + str(id)
			temp_dict['currentUserId'] = "216"
			# get_user_info = self._get_customer_user_info(hallCode)
			get_user = "lyp"
			get_pwd = "e10adc3949ba59abbe56e057f20f883e"
			token = self.obj_tools.loginYunyun(hallCode, get_user, get_pwd)
			req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
			if req['status'] == 200:
				obj_log.info('Delete video successfully........')
			else:
				obj_log.info('Delete video failed.......')
				return False

		return True

	def get_banner(self, hallCode=None,areaCode=None):
		banner_list = []
		bannerNoPlatfrom_list = []
		top_news_list = []
		top_platfromNews_list = []
		top_provincenews_list = []
		top_citynews_list = []
		top_areanews_list = []
		top_librarynews_list = []
		if hallCode:
			get_all_new = self._get_newfromdb(hallCode=hallCode)
		if areaCode:
			get_all_new = self._get_newfromdb(areaCode=areaCode)
		if hallCode:
			library_areacode = self._get_library_areacode(hallCode=hallCode)
		if areaCode:
			library_areacode = self._get_library_areacode(areaCode=areaCode)
		obj_log.info(library_areacode)
		get_topNews_statement = '''SELECT id,
								DATE_FORMAT(
										create_time,
										'%Y%m%d%H%i%S'
									) AS c_time
								FROM
									system_news
								WHERE
									STATUS = 0 
								AND top = 1
								ORDER BY c_time DESC'''
		top_news_temp = self.obj_tools.sql_event(get_topNews_statement)
		for i in range(len(top_news_temp)):
			top_news_list.append(top_news_temp[i]['id'])

		for i in top_news_list:
			if i in get_all_new['platfrom_news']:
				get_all_new['platfrom_news'].remove(i)
				top_platfromNews_list.append(i)
			if i in get_all_new['province_news']:
				get_all_new['province_news'].remove(i)
				top_provincenews_list.append(i)
			if i in get_all_new['city_news']:
				get_all_new['city_news'].remove(i)
				top_citynews_list.append(i)
			if i in get_all_new['area_news']:
				get_all_new['area_news'].remove(i)
				top_areanews_list.append(i)
			'''图书馆首页Banner'''
			if hallCode:
				if i in get_all_new['library_news']:
					get_all_new['library_news'].remove(i)
					top_librarynews_list.append(i)
		# 各类资讯优先选择列表
		# print(top_librarynews_list)
		# print(top_areanews_list)
		# print(top_citynews_list)
		# print(top_provincenews_list)
		# print(top_platfromNews_list)
		if hallCode:
			'''图书馆首页Banner'''
			top_librarynews_list.extend(get_all_new['library_news'])
		top_areanews_list.extend(get_all_new['area_news'])
		top_citynews_list.extend(get_all_new['city_news'])
		top_provincenews_list.extend(get_all_new['province_news'])
		top_platfromNews_list.extend(get_all_new['platfrom_news'])

		'''图书馆首页Banner'''
		if hallCode:
			if len(top_librarynews_list) > 4:
				top_librarynews_list = top_librarynews_list[:4]
			librarynews_len = len(top_librarynews_list)
		if areaCode:
			TEMP_NUM = 4
		else:
			TEMP_NUM = 3
		if len(top_areanews_list) > TEMP_NUM:
			top_areanews_list = top_areanews_list[:TEMP_NUM]

		if len(top_citynews_list) > 3:
			top_citynews_list = top_citynews_list[:3]

		if len(top_provincenews_list) > 3:
			top_provincenews_list = top_provincenews_list[:3]

		# if len(top_platfromNews_list) > 3:
		# 	top_platfromNews_list = top_platfromNews_list[:3]


		areanews_len = len(top_areanews_list)
		citynews_len = len(top_citynews_list)
		provincenews_len = len(top_provincenews_list)
		# platfromNews_len = len(top_platfromNews_list)
		if hallCode:
			all_news_len = librarynews_len + areanews_len + citynews_len + provincenews_len
		if areaCode:
			all_news_len = areanews_len + citynews_len + provincenews_len
		while all_news_len > 6:
			if provincenews_len > 1:
				top_provincenews_list.pop(-1)
				if hallCode:
					all_news_len = librarynews_len + areanews_len + citynews_len + provincenews_len
				if areaCode:
					all_news_len = areanews_len + citynews_len + provincenews_len
		while all_news_len > 6:
			if citynews_len > 1:
				top_citynews_list.pop(-1)
				if hallCode:
					all_news_len = librarynews_len + areanews_len + citynews_len + provincenews_len
				if areaCode:
					all_news_len = areanews_len + citynews_len + provincenews_len
		while all_news_len > 6:
			if areanews_len > 1:
				top_areanews_list.pop(-1)
				if hallCode:
					all_news_len = librarynews_len + areanews_len + citynews_len + provincenews_len
				if areaCode:
					all_news_len = areanews_len + citynews_len + provincenews_len
		while all_news_len > 6:
			if librarynews_len > 1:
				top_librarynews_list.pop(-1)
				if hallCode:
					all_news_len = librarynews_len + areanews_len + citynews_len + provincenews_len
				if areaCode:
					all_news_len = areanews_len + citynews_len + provincenews_len
		if hallCode:
			banner_list = (top_librarynews_list + top_areanews_list + top_citynews_list + top_provincenews_list)
		if areaCode:
			banner_list = (top_areanews_list + top_citynews_list + top_provincenews_list)
		if len(banner_list) < 6:
			residue_new = 6 - len(banner_list)
			banner_list.extend(get_all_new['platfrom_news'][:residue_new])
		return banner_list

	def banner_compare(self, hallCode=None,areaCode=None):
		if hallCode:
			get_library_info = self._get_library_areacode(hallCode=hallCode)
			library_areaCode = get_library_info['areaCode']
			library_cityCode = get_library_info['cityCode']
			library_provinceCode = get_library_info['provinceCode']
		if areaCode:
			get_library_info = self._get_library_areacode(areaCode=areaCode)
			library_areaCode = get_library_info['areaCode']
			library_cityCode = get_library_info['cityCode']
			library_provinceCode = get_library_info['provinceCode']
		if areaCode:
			if library_areaCode == "":
				get_areacustomer_statement = "SELECT hallCode FROM system_customer WHERE levelId = '4' AND `cityCode` = " + str(
					library_cityCode) + " " + "and isEffective = 1"
			else:
				get_areacustomer_statement = "SELECT hallCode FROM system_customer WHERE levelId = '4' AND `areaCode` = " + str(
					library_areaCode) + " " + "and isEffective = 1"
			areacustomer_info = self.obj_tools.sql_event(get_areacustomer_statement)
		get_citycustomer_statement = "SELECT hallCode FROM system_customer WHERE levelId = '3' AND `cityCode` = " + str(
										library_cityCode) + " " + "and isEffective = 1"
		citycustomer_info = self.obj_tools.sql_event(get_citycustomer_statement)

		get_provinceCustomer_statement = "SELECT hallCode FROM system_customer WHERE levelId = '2' AND `provinceCode` = " + str(
			library_provinceCode) + " " + "and isEffective = 1"
		provincecustomer_info = self.obj_tools.sql_event(get_provinceCustomer_statement)


		for a in range(4):
			if hallCode:
				get_all_new = self._get_newfromdb(hallCode=hallCode)
			if areaCode:
				get_all_new = self._get_newfromdb(areaCode=areaCode)
			if a >= len(get_all_new['province_news']):
				a = a - len(get_all_new['province_news'])
			else:
				temp = len(get_all_new['province_news']) - a
				get_all_new['province_news'] = get_all_new['province_news'][:temp]
				del_provinceNews = self.new_delete(get_all_new['province_news'])
			if a >= 1:
				# 创建省级News
				print("创建省级资讯...............")
				add_provinceNews = self.new_add(provincecustomer_info[0]['hallCode'],num=a)
			for b in range(4):
				if hallCode:
					get_all_new = self._get_newfromdb(hallCode=hallCode)
				if areaCode:
					get_all_new = self._get_newfromdb(areaCode=areaCode)
				if a >= len(get_all_new['city_news']):
					a = a - len(get_all_new['city_news'])
				else:
					temp = len(get_all_new['city_news']) - a
					get_all_new['province_news'] = get_all_new['city_news'][:temp]
					del_cityNews = self.new_delete(get_all_new['city_news'])
				if b >= 1:
					# 创建市级News
					print("创建市级资讯...............")
					add_cityNews = self.new_add(citycustomer_info[0]['hallCode'],num=b)
				'''首页区县级资讯最多4条，图书馆首页区县级资讯最多3条'''
				if areaCode:
					'''首页区县级资讯'''
					AREA_NUM = 5
				else:
					'''图书馆首页区县级资讯'''
					AREA_NUM = 4
				for c in range(AREA_NUM):
					if hallCode:
						get_all_new = self._get_newfromdb(hallCode=hallCode)
					if areaCode:
						get_all_new = self._get_newfromdb(areaCode=areaCode)
					if a >= len(get_all_new['area_news']):
						a = a - len(get_all_new['area_news'])
					else:
						temp = len(get_all_new['area_news']) - a
						get_all_new['province_news'] = get_all_new['area_news'][:temp]
						del_areaNews = self.new_delete(get_all_new['area_news'])
					if c >= 1:
						# 创建区县级单位News
						print("创建区县级资讯.............")
						if hallCode:
							add_areaNews = self.new_add(hallCode, type="2",num=c)
						if areaCode:
							add_areaNews = self.new_add(areacustomer_info[0]['hallCode'], type="2", num=c)

						if hallCode:
							for d in range(5):
								if hallCode:
									get_all_new = self._get_newfromdb(hallCode=hallCode)
								if areaCode:
									get_all_new = self._get_newfromdb(areaCode=areaCode)
								if a >= len(get_all_new['library_news']):
									a = a - len(get_all_new['library_news'])
								else:
									temp = len(get_all_new['library_news']) - a
									get_all_new['province_news'] = get_all_new['library_news'][:temp]
									del_libraryNews = self.new_delete(get_all_new['library_news'])

								if d >= 1:
									# 创建图书馆News
									print("创建图书馆资讯.............")
									add_libraryNews = self.new_add(hallCode, type="3",num=d)

						if hallCode:
							new_fromdb_list = self.get_banner(hallCode=hallCode)
						if areaCode:
							new_fromdb_list = self.get_banner(areaCode=areaCode)
						print('...............................................................')
						print("数据库：",new_fromdb_list)
						obj_log.info("获取读者APP图书馆banner接口返回值..................")
						app_librarybanner_list = []
						if hallCode:
							'''图书馆Banner'''
							app_librarybanner_temp = self.lib_banner_news(hallCode=hallCode)
						else:
							'''首页Banner'''
							app_librarybanner_temp = self.home_banner_news(areaCode=areaCode)
						for i in app_librarybanner_temp:
							app_librarybanner_list.append(i['newsId'])
						print("APP:",app_librarybanner_list)
						if new_fromdb_list == app_librarybanner_list:
							obj_log.info("资讯列表相同...............")
						else:
							obj_log.info("资讯列表不相同...............")
							return False
						time.sleep(2)
		return True


	# 资讯弃审
	def new_abandoned(self,new_id_list):
		# new_id_list 为 list
		req_type = 'PUT'
		hallCode = "YTSG"
		temp_dict= {}
		currentUserId = "52"
		get_user = "lyp"
		get_pwd = "e10adc3949ba59abbe56e057f20f883e"
		for id in new_id_list:
			API_URL = "http://" + self.add + "/api/news/" + str(id) + "/newAbandoned?currentUserId=" + str(currentUserId)
			# get_user_info = self._get_customer_user_info(hallCode)
			token = self.obj_tools.loginYunyun(hallCode, get_user, get_pwd)
			req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
			if req['status'] == 200:
				obj_log.info('Abandoned news {} successfully........'.format(id ))
			else:
				obj_log.info('Abandoned news {} failed.......'.format(id))
				return False
		return True

	def new_delete(self, new_id_list):
		req_type = 'DELETE'
		#资讯弃审
		abandoned_news = self.new_abandoned(new_id_list)
		temp_dict= {}
		for id in new_id_list:
			get_user_statement = "SELECT id,hallCode,userName,password from system_user WHERE id = (SELECT create_by from system_news WHERE id = " + str(id) +")"
			user_info = self.obj_tools.sql_event(get_user_statement)
			currentUserId = user_info[0]['id']
			hallCode = user_info[0]['hallCode']
			get_user = user_info[0]['userName']
			get_pwd = user_info[0]['password']
			API_URL = "http://" + self.add + "/api/news/" + str(id) + "/newDelete?currentUserId=" + str(currentUserId)
			# get_user_info = self._get_customer_user_info(hallCode)
			token = self.obj_tools.loginYunyun(hallCode, get_user, get_pwd)
			req = self.obj_tools.call_rest_api(API_URL, req_type, data_rtn=temp_dict, token=token)
			if req['status'] == 200:
				obj_log.info('Delete news {} successfully........'.format(id))
			else:
				obj_log.info('Delete news {} failed.......'.format(id))
				return False
		return True

	def lib_banner_news(self, hallCode):
		'''图书馆Banner'''
		req_type = 'GET'
		temp_dict= {}
		locationCode = self._get_library_areacode(hallCode)
		if locationCode['areaCode'] == None:
			areaCode = locationCode['cityCode']
		else:
			areaCode = locationCode['areaCode']
		API_URL = "http://" + self.app_add + "/userApp/news/libBannerNews/" + str(hallCode) + "?locationCode="  + areaCode
		print(API_URL)
		req = requests.get(API_URL)
		rtn = json.loads(req.text)
		if req.status_code == 200:
			obj_log.info('Get libBanner successfully........')
		else:
			obj_log.info('Get libBanner failed.......')
			return False
		return rtn['data']

	def home_banner_news(self, areaCode):
		'''首页Banner'''
		req_type = 'GET'
		temp_dict= {}
		API_URL = "http://" + self.app_add + "/userApp/news/homeNews" + "?locationCode="  + areaCode
		print(API_URL)
		req = requests.get(API_URL)
		rtn = json.loads(req.text)
		if req.status_code == 200:
			obj_log.info('Get home Banner successfully........')
		else:
			obj_log.info('Get home Banner failed.......')
			return False
		return rtn['data']



	def add_notice(self, hallCode='AARH', area=None, name=None):
		'''消息新增'''
		req_type = 'POST'
		temp_dict= {}
		API_URL = "http://" + self.add + "/api/notice/add"
		temp_dict['duration'] = 12
		if obj == 'area':
			temp_dict['content'] = now_time + '新增消息' + '-' + obj.replace()
		req = requests.get(API_URL)
		rtn = json.loads(req.text)
		if req.status_code == 200:
			obj_log.info('Get libBanner successfully........')
		else:
			obj_log.info('Get libBanner failed.......')
			return False
		return rtn['data']

	def add_pageview(self,ebook_id):
		'''增加某本电子书阅读量'''
		req_type = 'POST'
		temp_dict= {}
		API_URL = "http://" + self.add + "/api/notice/add"
		temp_dict['duration'] = 12
		if obj == 'area':
			temp_dict['content'] = now_time + '新增消息' + '-' + obj.replace()
		req = requests.get(API_URL)
		rtn = json.loads(req.text)
		if req.status_code == 200:
			obj_log.info('Get libBanner successfully........')
		else:
			obj_log.info('Get libBanner failed.......')
			return False
		return rtn['data']


'''******************************************************************************************************************'''
obj_tools = utils.Tools()
all_config = obj_tools.all_config
obj_runner = Test_case(all_config)
class Multi_new_add(threading.Thread):
	def __init__(self, hallcode, type, is_need_review):
		threading.Thread.__init__(self)
		self.hallcode = hallcode
		self.type = type
		self.is_need_review = is_need_review
		self.ret = ''

	def run(self):
		# self.ret = Runner._new_add(self.hallcode, self.type, self.is_need_review)
		self.ret = obj_runner.new_add(self.hallcode, self.type, self.is_need_review)

	def get_return(self):
		return self.ret

def multi_new_add(hallcode_list, type="2", is_need_review=0):
	thread_list = []
	for hallcode in hallcode_list:
		t = Multi_new_add(hallcode, type, is_need_review)
		thread_list.append(t)

	for thread in thread_list:
		thread.start()

	for thread in thread_list:
		thread.join()

	for thread in thread_list:
		ret = thread.get_return()
		if ret == False:
			return False
	return True
'''视频上传'''
class Multi_upload_vedios(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.ret = ''

	def run(self):
		self.ret = obj_runner.movie_upload()

	def get_return(self):
		return self.ret

def multi_upload_vedios():
	thread_list = []
	for i in range(3):
		t = Multi_upload_vedios()
		thread_list.append(t)

	for thread in thread_list:
		thread.start()

	for thread in thread_list:
		thread.join()

	for thread in thread_list:
		ret = thread.get_return()
		if ret == False:
			return False
	return True

