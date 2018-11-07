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

