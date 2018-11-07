# -*- coding=utf-8 -*-
import sys,utils,unittest,runner,log,time,HTMLTestRunner,os
from test_case import Test_case
import test_case
from selenium import webdriver
to_list = ["18782019436@163.com"]
obj_log = log.get_logger()
# log_file = r"E:\PycharmProjects\remote_yunyun_api\log\yuntu.log"
log_file = (os.path.split(os.path.realpath(__file__)))[0] + '\\' + 'log\yuntu.log'
fp = open(log_file,'w')
class Yuntu_case(unittest.TestCase):
	@classmethod
	def setUp(self):
		self.obj_test_case = Test_case(all_config)
	@classmethod
	def tearDown(self):
		# driver.close()
		pass

	def multi_upload_movie(self):
		obj_log.info('Upload movie start................')
		self.assertEqual(test_case.multi_upload_vedios(), True)
		time.sleep(2)

	def multi_add_new(self):
		obj_log.info('Add new start................')
		self.assertEqual(test_case.multi_new_add(["AABCE","AAALA"], type="2"), True)

	def add_new_arear(self):
		obj_log.info('Add new start................')
		self.assertEqual(self.obj_test_case.new_add("AAAAC", type="3", num=20), True)

	def upload_movie(self):
		obj_log.info('Upload movie start................')
		for i in range(2000):
			self.assertEqual(self.obj_test_case.movie_upload(), True)
			time.sleep(1)

	def del_videos(self):
		obj_log.info('Delete movie start................')
		self.assertEqual(self.obj_test_case.vidoes_del(), True)
	def app_banner(self):
		obj_log.info('Get library banner start................')
		self.assertEqual(self.obj_test_case.banner_compare(areaCode="510107"), True)
		# self.assertEqual(self.obj_test_case.banner_compare(areaCode="620200"), True)
		# self.assertEqual(self.obj_test_case.banner_compare(hallCode="AJAJ"), True)



def suite():
	suite = unittest.TestSuite()
	suite.addTest(Yuntu_case("app_banner"))
	# suite.addTest(Yuntu_case("add_new_arear"))
	# suite.addTest(Yuntu_case("del_videos"))
	# suite.addTest(Yuntu_case("upload_movie"))

	# suite.addTest(Yuntu_case("tearDown"))

	return suite

if __name__ == '__main__':
	obj_tools = utils.Tools()
	all_config = obj_tools.all_config
	unitrunner = unittest.TextTestRunner(fp)
	'''测试报告生成'''
	# now_time = time.strftime("%Y%m%d%H%M", time.localtime(time.time()))
	# filename = "E:\Yunyun_api\Report\\" + now_time + "testReport.html"
	# fp = open(filename, 'wb')
	# unitrunner = HTMLTestRunner.HTMLTestRunner(
	# 	stream=fp,
	# 	title=u'云图测试报告',
	# 	description=u'测试用例详细信息'
	# )

	test_suite = suite()
	rtn1 = unitrunner.run(test_suite)
	fp.close()
	html_report = fp.name
	'''邮件发送'''
	# sendmail = obj_tools.send_mail(to_list,html_report)
	print('Test Result:', rtn1)
