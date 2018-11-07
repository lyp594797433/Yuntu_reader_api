#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,log

import time, xlrd, xlwt

import pymysql
import glob
import re
obj_log = log.get_logger()

class ExcelUtil():
	def dict_data(self, excelPath, indexOrName=0):
		self.data = xlrd.open_workbook(excelPath)
		try:
			self.table = self.data.sheet_by_name(indexOrName)
		except Exception as e:
			if type(indexOrName) is not int:
				indexOrName = int(indexOrName)
			self.table = self.data.sheet_by_index(indexOrName)

		# 获叏第一行作为key值
		self.keys = self.table.row_values(0)
		# 获叏总行数
		self.rowNum = self.table.nrows
		# 获叏总列数
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

		conn = pymysql.connect(
			host='120.77.80.162',
			port=3306,
			user='test',
			passwd='123456',
			charset='utf8',
			db='bookplatform_test',
			cursorclass=pymysql.cursors.DictCursor
		)
		# conn = MySQLdb.connect(
		# 	host='rm-wz91b2j3ypnw1fbr6o.mysql.rds.aliyuncs.com',
		# 	port=3306,
		# 	user='ceshiuser',
		# 	passwd='U%#Ceshi47io45',
		# 	charset='utf8',
		# 	db='bookplatform',
		# )
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
		# print(str(len(results))) + "  " + outputpath
		# time.sleep(200)
		for row in range(1, len(results) + 1):
			for col in range(0, len(fields)):
				# print("1111:",results[row - 1]["videos_id"])
				sheet.write(row, col, u'%s' % results[row - 1]["videos_id"])
		workbook.save(outputpath)

	# r'datetest.xls'
	def sql_event(self, statement):
		sql_type = statement.split(" ")[0]

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
			print("Get or change the data into MySql............")
			print(statement)
			cur = conn.cursor()
			a = cur.execute(statement)
		except Exception as e:
			print(e)
		if sql_type in ("SELECT", "select"):
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


if __name__ == "__main__":
	a = 0
	y = []
	outhallcode = []
	filePath = r"E:\1.xlsx"
	sheetName = "table_message"
	info_list1 = []
	info_list2 = []
	library_videos_rtn1 = {}
	library_videos_rtn2 = {}
	data_event = ExcelUtil()
	output_file = r"E:\2.xlsx"
	sql_statement = "SELECT library_id,videos_id FROM system_videos_record where customer_id = 1019 and status = 1"
	info_temp1 = data_event.sql_event(sql_statement)
	print(info_temp1)
	library_id = ""
	for temp in info_temp1:
		if temp["library_id"] != library_id:
			info_list1 = []
		x = temp['videos_id']
		info_list1.append(x)
		# if temp["library_id"] == library_id
		library_videos_rtn1[temp["library_id"]] = info_list1
		library_id = temp["library_id"]
	obj_log.info(library_videos_rtn1)

	input("请删除视频：")
	info_list1 = []
	info_list2 = []
	info_temp1 = data_event.sql_event(sql_statement)
	print(info_temp1)
	library_id = ""
	for temp in info_temp1:
		if temp["library_id"] != library_id:
			info_list1 = []
		x = temp['videos_id']
		info_list1.append(x)
		# if temp["library_id"] == library_id
		library_videos_rtn2[temp["library_id"]] = info_list1
		library_id = temp["library_id"]
	obj_log.info(library_videos_rtn2)
	out_rtn = {}
	for library1, videos1 in library_videos_rtn1.items():

		for library2, videos2 in library_videos_rtn2.items():


			if library1 == library2:
				if videos2 != videos1:
					a = [x for x in videos2 if x not in videos1]
					out_rtn[library1] = a
					print("*****************************")

	obj_log.info(out_rtn)

# for i in info_temp1:
# 	info_list1.append(i["videos_id"])
# 	# to_excel = data_event.export_ToExcle(sql_statement, output_file)

# info_temp2 = data_event.sql_event(sql_statement)
# for i in info_temp2:
# 	info_list2.append(i["videos_id"])


# print([x for x in info_list2 if x not in info_list1])
# b = [y for y in a if y in info_list2]
# print(b)
# temp = data_event.dict_data(filePath)
# 视频名称2018-07-16-13-16-26
# for x in temp:
# 	y.append(str(x['hallCode']))

# for z in y:
# 	outhallcode.append(str(z))

# outhallcode_str = str(outhallcode)

# outhallcode_str = outhallcode_str.strip("[")
# outhallcode_str = outhallcode_str.strip("]")
# print(outhallcode_str)