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





