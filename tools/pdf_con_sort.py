
import sys, os, re
from os.path import join

from fileutil.pdf_table import pdf_all_tables

re_bra = re.compile('（.*）|\\(.*\\)|自动|\n|：|:')

def con_rename(con_dir):
	for file_ in sorted(os.listdir(con_dir)):
		#print(file_)
		cont_l = []
		con_file = join(con_dir, file_)
		tables = pdf_all_tables(con_file)
		for table in tables:
			if table and table[0][0] in ('产品名称',):
				for r in table:
					row = [re_bra.sub("", cell) for cell in r]
					cont_l.extend([row[i:i+2] for i in range(0,len(row),2)])
		row = {}
		for k, v in cont_l:
			row[k] = v
		if not file_.startswith(row["出借期开始日"]):
			file_new = "_".join([row["出借期开始日"],file_])
			print(file_new)
			os.rename(con_file, join(con_dir, file_new))

con_rename(sys.argv[1])
