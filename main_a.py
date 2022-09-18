import tarfile
import os
import glob
import sys
import re
import shutil
import time
from datetime import datetime
import math
# from xml.etree import ElementTree as ET
# from xml.dom import minidom
#print (os.path.split(os.path.realpath(__file__))[0])

#print (pwd)
#aaa='\033[94m'+'TEST'
#print(aaa)

def span_c(str, c):
	newstr='<span class="'+c+'">'+str+'</span>'
	return newstr

def para_c(str, c):
	if c:
		newpara='<p class="'+c+'">'+str+'</p>\n'
	else:
		newpara='<p>'+str+'</p>\n'
	return newpara

def head_c(str):
    newhead='<head>\n'+str+'\n</head>'
    return newhead

def body_c(str):
    newbody='<body>\n'+str+'\n</body>'
    return newbody

def html_c(str):
	newhtml='<html>\n'+str+'\n</html>'
	return newhtml

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def current_time(curtime):
    try:
        newtime=datetime.strptime(curtime, "%m/%d/%Y %I:%M:%S %p")
    except ValueError as e:
        newtime=datetime.strptime(curtime, "%m/%d/%Y %H:%M:%S")
    return newtime

def prt_extract(prt_path, target_path):
	try:
		tar=tarfile.open(prt_path, "r:gz")
		tar.extractall(target_path)
		# file_names=tar.getnames()
		# for file_name in file_names:
		#     tar.extract(file_name, target_path)
		tar.close()
		# top_path=target_path
		if len(os.listdir(target_path))==1:
			src_path=target_path+os.sep+os.listdir(target_path)[0]
			shutil.copytree(src_path, target_path, dirs_exist_ok=True)
					# for item in glob.glob(each_item+os.sep+"*"):
					# 	shutil.copy(item, target_path)
			shutil.rmtree(src_path)
	except Exception as err:
		print(err)

def msg_merge(msg_tar_path):
	tmp_msg=re.search(r'\/(\w+)\.tar\.gz', msg_tar_path).group(1)
	tmp_msg_folder=re.match(r'(.*\/\w+)\.tar\.gz', msg_tar_path).group(1)
	if not os.path.exists(tmp_msg_folder):
		os.makedirs(tmp_msg_folder)
	else:
		try:
			shutil.rmtree(tmp_msg_folder)
			os.makedirs(tmp_msg_folder)
		except OSError as err:
			print("Error: %s : %s" % (tmp_msg_folder, err.strerror))
	prt_extract(msg_tar_path, tmp_msg_folder)
	tmp_msgs=tmp_msg_folder+'/tmp_msgs'
	file=open(tmp_msgs, 'w')
	file.close()
	with open(tmp_msgs, 'ab') as f:
		message_files=[]
		for each in os.listdir(tmp_msg_folder):
			if re.search(r'messages', each):
				message_files.append(each)
		message_files.sort(reverse=True)
		for each in message_files:
			with open(tmp_msg_folder+'/'+each, 'rb') as m:
				f.write(m.read())
	with open(tmp_msgs, 'rb') as f:
		files=f.read()
	shutil.rmtree(tmp_msg_folder)
	return files

def message_merge(msg_tar_path):
	tmp_msg_folder=re.match(r'(.*\/\w+)\.tar\.gz', msg_tar_path).group(1)
	if not os.path.exists(tmp_msg_folder):
		os.makedirs(tmp_msg_folder)
	else:
		try:
			shutil.rmtree(tmp_msg_folder)
			os.makedirs(tmp_msg_folder)
		except OSError as err:
			print("Error: %s : %s" % (tmp_msg_folder, err.strerror))
	try:
		tar=tarfile.open(msg_tar_path, "r:gz")
		tar.extractall(tmp_msg_folder)
		# file_names=tar.getnames()
		# for file_name in file_names:
		#     tar.extract(file_name, target_path)
		tar.close()

		tmp_msgs=tmp_msg_folder+'/tmp_msgs'
		file=open(tmp_msgs, 'w')
		file.close()
		with open(tmp_msgs, 'ab') as f:
			message_files=[]
			if os.path.isdir(tmp_msg_folder+'/messages'):
				tmp_msg_folder=tmp_msg_folder+'/messages'
			for each in os.listdir(tmp_msg_folder):
				if re.search(r'messages', each):
					message_files.append(each)
			message_files.sort(reverse=True)
			for each in message_files:
				each_msg=tmp_msg_folder+'/'+each
				with open(each_msg, 'rb') as m:
					f.write(m.read())
		with open(tmp_msgs, 'rb') as f:
			files=f.read()
		shutil.rmtree(tmp_msg_folder)
		return files
	except Exception as err:
		print(err)

def generate_chooseTime(prt_folder, hours_d, time_seg):
	if hours_d==time_seg:
		max=0
	else:
		max=hours_d-time_seg
	# shutil.copy('chooseTime.html', prt_full_folder)
	with open (prt_folder+'/chooseTime.html', "w") as newf:
		with open ('chooseTime.html', "r") as f:
			for line in f.readlines():
				if re.search('name\=\"start\_time.*\>', line):
					newf.write(re.sub('name\=\"start\_time.*\>', 'name="start_time" min="0" max="'+str(max)+'" step="0.01" value="'+str(max)+'">', line))
				elif re.search('This\ PRT.*', line):
					newf.write(re.sub('This\ PRT.*\<', 'This PRT file contains about '+str(hours_d)+'-hour log messages, to reduce overall network traffic volume, the green bar would contain about '+str(time_seg)+'-hour log messages.<', line))
				elif re.search('\"prt\_folder\"\ value\=\"', line):
					newf.write(re.sub('\"prt\_folder\"\ value\=\"', '"prt_folder" value="'+prt_folder, line))
				else:
					newf.write(line)


def main():
	# pwd=os.getcwd()
	prt_file=sys.argv[1]
	fixed_size=100000000
	fixed_days=7
	# prt_files=[]
	# for each in os.listdir(pwd):
	#     each_fullname=pwd+os.sep+each
	#     if not os.path.isdir(each_fullname):
	#         if re.search(r'prt.*tar\.gz', each_fullname, re.I):
	#             prt_files.append(each_fullname)
	#
	# if not prt_files:
	#     print("There is no PRT files in this folder")
	# else:
	#     for prt_file in prt_files:
	prt_folder=re.search(r'(prt.*)\.tar\.gz', prt_file, re.I).group(1)

	if not os.path.exists(prt_folder):
	    os.makedirs(prt_folder)
	else:
	    try:
	        shutil.rmtree(prt_folder)
	        os.makedirs(prt_folder)
	    except OSError as err:
	        print("Error: %s : %s" % (prt_folder, err.strerror))

	prt_extract(prt_file, prt_folder)
	# prt_full_folder=pwd+os.sep+prt_folder

	#
	file=open(prt_folder+'/all_messages', 'w')
	file.close()
	archive_folder=prt_folder+'/archive'
	archive_tar=prt_folder+'/archive.tar.gz'
	os.makedirs(archive_folder)
	prt_extract(archive_tar, archive_folder)
	main_folder=prt_folder+'/archive/main'
	with open(prt_folder+'/all_messages', 'ab') as f:
		main_files=[]
		if len(os.listdir(main_folder))>0:
			for each in os.listdir(main_folder):
				main_files.append(each)
			main_files.sort()
			basedate=datetime.strptime(re.search(r'(\d{8}).*', main_files[-1], re.I).group(1), "%Y%m%d")
			for each in main_files:
				eachdate=datetime.strptime(re.search(r'(\d{8}).*', each, re.I).group(1), "%Y%m%d")
				if (basedate-eachdate).days<=fixed_days:
					main_tar=main_folder+'/'+each
					main_tar_msgs=msg_merge(main_tar)
					f.write(main_tar_msgs)
		messages=prt_folder+'/messages.tar.gz'
		f.write(message_merge(messages))

	with open(prt_folder+'/status.xml', "r") as statusf:
		for line in statusf.readlines():
			time_search=re.search(r'\<Current\_Time\>(.*)\<\/Current\_Time\>', line, re.I)
			if time_search:
				curtime=time_search.group(1)
				curtime=current_time(curtime)

	for each in os.listdir(prt_folder):
		file_search=re.match(r'logcat.+', each, re.I)
		if file_search:
			with open(prt_folder+os.sep+each, "r", errors = 'ignore') as genf:
				for line in genf:
					time_search=re.search(r'\d{4}\ \D{3}\ (.{15}).*(syslog\-genprt\ \-\ prt)', line, re.I)
					if time_search:
						gen_t=datetime.strptime(time_search.group(1), "%b %d %H:%M:%S")

	with open(prt_folder+'/all_messages', "r", errors = 'ignore') as genf:
		time_rev=0
		for line in genf:
			if time_rev==0:
				time_search=re.search(r'\d{4}\ \D{3}\ (.{15}).*', line, re.I)
				if time_search:
					old_t=datetime.strptime(time_search.group(1), "%b %d %H:%M:%S")
					if old_t>gen_t:
						time_rev=1
						gen_temp=gen_t.replace(year=curtime.year)
						old_temp=old_t.replace(year=(curtime.year-1))
						if (gen_temp-old_temp).days>=fixed_days:
							time_rev_reboot_event=1
						else:
							gen_t=gen_temp
							old_t=old_temp
							break
					else:
						if (gen_t-old_t).days<=fixed_days:
							break
			else:
				if time_rev_reboot_event==1:
					time_search=re.search(r'\d{4}\ \D{3}\ (.{15}).*', line, re.I)
					if time_search:
						if abs((old_t-(datetime.strptime(time_search.group(1), "%b %d %H:%M:%S"))).days)>1:
							old_t=datetime.strptime(time_search.group(1), "%b %d %H:%M:%S")
							break

	hours_d=round((gen_t.timestamp()-old_t.timestamp())/3600, 2)
	# old_t=old_t.decode('utf-8')
	# gen_t=gen_t.decode('utf-8')

	file_size=os.stat(prt_folder+'/all_messages').st_size
	if file_size<=fixed_size:
		time_seg=hours_d
	else:
		time_seg=round(hours_d*fixed_size/file_size, 2)

	with open(prt_folder+'/argv.txt', "w") as argvf:
		strs=prt_folder+","+str(old_t)+","+str(gen_t)+","+str(curtime)+","+str(file_size)+","+str(hours_d)+","+str(fixed_size)+","+str(time_seg)
		argvf.write(strs)

	# with open(prt_folder+'/all_messages', "rb") as genf:
	# 	with open(prt_folder+'/all_messages_s', "wb") as targf:
	# 		contents=genf.read()
	# 		targf.write(contents.decode('utf-16').encode('utf-8'))


	generate_chooseTime(prt_folder, hours_d, time_seg)
	# generate_all_sip_msgs(prt_folder, "all_messages", gen_t, curtime)


if __name__ == '__main__':
    main()
