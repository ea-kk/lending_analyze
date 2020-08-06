
# [Python骚操作，提取pdf文件中的表格数据](https://cloud.tencent.com/developer/article/1408826)

import pdfplumber

def pdf_all_tables(pdf_file, password=""):
	pdf = pdfplumber.open(pdf_file, password=password)
	tables = []
	for page in pdf.pages:
		tables.extend(page.extract_tables())
	pdf.close()
	return tables


