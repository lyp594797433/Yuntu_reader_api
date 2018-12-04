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

	def count_pageview_app(self,ebook_id,identity,hallcode):
		'''查询APP电子书阅读量'''
		req_type = 'GET'
		temp_dict = {}
		temp_dict['id'] = ebook_id
		temp_dict['identity'] = identity
		temp_dict['libCode'] = hallcode
		temp_dict['visitType'] = 1
		temp_dict['fromSearch'] = 0
		API_URL = "http://" + self.app_add + "/userApp/ebook/info"
		req = obj_tools.call_rest_api(API_URL, req_type=req_type, data_rtn=temp_dict)
		# rtn_temp = req.text
		# rtn = json.loads(rtn_temp)
		rtn = req['data']
		return rtn['number']




	def add_ebookpageview(self,ebook_id,hallcode=None,num=1):
		'''增加某本电子书阅读量'''
		req_type = 'POST'
		temp_dict= {}
		API_URL = "http://" + self.app_add + "/userApp/ebook/addEbookReadRecord"
		if hallcode is None:
			get_hallcode_ebookallocated = self._get_hallcode_ebookallocated(ebook_id)
			get_hallcode_ebookhadkread = self._get_hallcode_ebookhadkread(ebook_id)
			libcode_list = list(set(get_hallcode_ebookallocated) - set(get_hallcode_ebookhadkread))
		get_ebook_name = self._get_ebookname(ebook_id)
		ebook_name = get_ebook_name['bookName']
		temp_dict['ebookId'] = ebook_id
		peruser_list = self._get_allperuser(ebook_id)
		if num > len(peruser_list):
			num = len(peruser_list)
		for x in range(1,num+1):
			if hallcode is None:
				peruser_list = self._get_allperuser(ebook_id)
				get_hallcode_ebookallocated = self._get_hallcode_ebookallocated(ebook_id)
				get_hallcode_ebookhadkread = self._get_hallcode_ebookhadkread(ebook_id)
				libcode_list = list(set(get_hallcode_ebookallocated) - set(get_hallcode_ebookhadkread))
				if len(libcode_list) <2:
					obj_log.info("请更换电子书..............................")
					return False
			libcode = libcode_list[x-1]
			peruser = peruser_list[x-1]
			temp_dict['libCode'] = libcode
			temp_dict['peruser'] = peruser
			req = obj_tools.call_rest_api(API_URL,req_type=req_type,data_rtn=temp_dict)
			if req['status'] == 200:
				obj_log.info('增加图书馆{0}电子书:{1} 阅读量第{2}次成功........'.format(libcode,ebook_name,x))
			else:
				obj_log.info('增加图书馆{0}电子书:{1} 阅读量第{2}次失败........'.format(libcode,ebook_name,x))
				return False
			if x == num:
				count_app_pageview = self.count_pageview_app(ebook_id,peruser,libcode)
		'''阅读量与数据库对比'''
		count_pageview_db = self._get_ebookpageview_count(ebook_id)
		if count_app_pageview == count_pageview_db:
			obj_log.info("数据库阅读量：{}".format(count_pageview_db))
			obj_log.info("APP阅读量：{}".format(count_app_pageview))
			obj_log.info("数据库阅读量与APP阅读量一致.........")
			return True
		else:
			obj_log.info("数据库阅读量：{}".format(count_pageview_db))
			obj_log.info("APP阅读量：{}".format(count_app_pageview))
			obj_log.info("数据库阅读量与APP阅读量不一致.........")
			return False

		return True


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

