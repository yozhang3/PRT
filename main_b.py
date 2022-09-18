import tarfile
import os
import glob
import sys
import re
import shutil
import time
from datetime import datetime
import math

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

def time_convert(msg_time, time_dif):
    mmatch=re.match(r'(.{15})(.{7})', msg_time)
    mtime=datetime.strptime(mmatch.group(1), "%b %d %H:%M:%S")
    mtime_tail=mmatch.group(2)
    mtime=str(datetime.fromtimestamp(mtime.timestamp()+time_dif))
    newtime=mtime+mtime_tail
    return newtime


def time_dif(gen_t, curtime):
	curtime=datetime.strptime(curtime, "%Y-%m-%d %H:%M:%S")
	gen_t=datetime.strptime(gen_t, "%Y-%m-%d %H:%M:%S")
	time_dif=curtime.timestamp()-gen_t.timestamp()
	return time_dif

def current_time(curtime):
	try:
		tuple_t=time.strptime(curtime, "%m/%d/%Y %I:%M:%S %p")
	except ValueError as e:
		tuple_t=time.strptime(curtime, "%m/%d/%Y %H:%M:%S")
	newtime=time.strftime("%Y-%m-%d %H:%M:%S", tuple_t)
	return newtime

def generate_showtech(prt_folder):
	for each in os.listdir(prt_folder):
		if re.match(r'show\-output.*', each):
			os.rename(prt_folder+'/'+each, prt_folder+'/tech.log')
		elif re.match(r'description.*', each):
			os.rename(prt_folder+'/'+each, prt_folder+'/description.log')


def generate_output(prt_folder, hours_d, time_seg, start_time):
	if hours_d==time_seg:
		max=0
	else:
		max=hours_d-time_seg

	with open (prt_folder+'/output.html', "w") as newf:
		with open ('output.html', "r") as f:
			for line in f:
				if re.search('name\=\"start\_time.*\>', line):
					newf.write(re.sub('name\=\"start\_time.*\>', 'name="start_time" min="0" max="'+str(max)+'" step="0.01" value="'+str(start_time)+'">', line))
				elif re.search('This\ PRT.*', line):
					newf.write(re.sub('This\ PRT.*\<', 'This PRT file contains about '+str(hours_d)+'-hour log messages, to reduce overall network traffic volume, the green bar would contain about '+str(time_seg)+'-hour log messages.<', line))
				elif re.search('\"prt\_folder\"\ value\=\"', line):
					newf.write(re.sub('\"prt\_folder\"\ value\=\"', '"prt_folder" value="'+prt_folder, line))
				elif re.search('iframe', line):
					newf.write(re.sub('iframe\ src\=\"', 'iframe src="/'+prt_folder, line))
				else:
					newf.write(line)

def generate_fixed_allmsgs(prt_folder, all_messages, start_time, fixed_size, file_size, hours_d, time_seg):
	if hours_d==time_seg:
		shutil.copy(prt_folder+'/'+all_messages, prt_folder+'/all_messages_r')
	else:
		start_pointer=math.ceil(start_time*file_size/hours_d)
		with open(prt_folder+'/all_messages_r', 'w') as newf:
			with open (prt_folder+'/'+all_messages, 'r', errors = 'ignore') as f:
				f.seek(start_pointer, 0)
				line=f.readline()
				line=f.readline()
				while line is not None and line !='':
					newf.write(line)
					line=f.readline()
					if (f.tell()-start_pointer)>=fixed_size:
						line=f.readline()
						newf.write(line)
						break


def generate_all_sip_msgs(prt_folder, all_messages, time_dif):
	style="""
	<style>
	span.s{
	    color: blue;
	    # margin-left: 0px;
	    # margin-top:0px;
	    # margin-bottom:0px;
	    # border:0px;
	    # padding-top:0px;
	    # padding-bottom:0px;
	}
	span.r{
	    color: indigo;
	}
	span.d {
	    color: green;
	}
	span.e {
	    color: red;
		font-weight: bold;
	}
	span.w {
	    color: brown;
		font-weight: bold;
	}
	.sp{
	    margin-left: 50px;
	}
	p {
	#  border: 2px solid powderblue;
	    font-family: 'Arial';
		font-size: 12px;
	    margin: 0;
	    padding: 0;
	}
	</style>"""

	doctype='<!DOCTYPE html>'

	with open(prt_folder+'/'+all_messages, "r", errors = 'ignore') as f:
		allmsg=''
		sipmsg_flag=0
		sipmsg=''
		sipmsg_send=0
		with open(prt_folder+'/allmsgs.html', "w") as allmsgs:
			with open(prt_folder+'/sipmsgs.html', "w") as sipmsgs:
				for line in f:
					# line=line.decode('utf-8')
					line=line.replace('&','&amp')
					line=line.replace('<','&lt')
					line=line.replace('>','&gt')
					newline=''
					if sipmsg_flag==0:
						msg=re.match(r'(\d{4}\ )(\D{3})\ (.{22})(.*)', line, re.M|re.I)
						if msg:
							newtime=time_convert(msg.group(3), time_dif)
							newline=msg.group(1)+'  '+newtime+' '+msg.group(2)+msg.group(4)
							if msg.group(2)=='ERR':
								newline=para_c(msg.group(1)+'  '+span_c(newtime, 'd')+' '+span_c(msg.group(2)+' '+msg.group(4), 'e'), '')
							elif msg.group(2)=='WRN':
								newline=para_c(msg.group(1)+'  '+span_c(newtime, 'd')+' '+span_c(msg.group(2)+' '+msg.group(4), 'w'), '')
							elif re.search(r'\={5}\&gt.*SIP\ MSG\:\:', msg.group(4), re.M):
								newline=para_c(msg.group(1)+'  '+span_c(newtime, 'd')+' '+span_c(msg.group(2)+' '+msg.group(4), 's'), '')
								sipmsg+=newline
								sipmsg_flag=1
								sipmsg_send=1
							elif re.search(r'\&lt\={5}.*SIP\ MSG\:\:', msg.group(4), re.M):
								newline=para_c(msg.group(1)+'  '+span_c(newtime, 'd')+' '+span_c(msg.group(2)+' '+msg.group(4), 'r'), '')
								sipmsg+=newline
								sipmsg_flag=1
							else:
								newline=para_c(msg.group(1)+'  '+span_c(newtime, 'd')+' '+msg.group(2)+' '+msg.group(4), '')
					else:
						if not re.search(r'\:\:End\-Of\-Sip\-Message\:\:', line):
							if sipmsg_send:
								newline=para_c(span_c(line.strip(), 's'), 'sp')
							else:
								newline=para_c(span_c(line.strip(), 'r'), 'sp')
						else:
							sipend=re.match(r'(\d{4}\ )(\D{3})\ (.{22})(.*)', line, re.M|re.I)
							newtime=time_convert(sipend.group(3), time_dif)
							if sipmsg_send:
								newline=para_c(sipend.group(1)+'  '+span_c(newtime, 'd')+' '+span_c(sipend.group(2)+' '+sipend.group(4), 's'), '')
								sipmsg_send=0
								sipmsg_flag=0
							else:
								newline=para_c(sipend.group(1)+'  '+span_c(newtime, 'd')+' '+span_c(sipend.group(2)+' '+sipend.group(4), 'r'), '')
								sipmsg_flag=0
						sipmsg+=newline
					allmsg+=newline
				sipmsgs.write(doctype+html_c(head_c(style)+'\n'+body_c(sipmsg)))
			allmsgs.write(doctype+html_c(head_c(style)+'\n'+body_c(allmsg)))

def main():
	prt_folder = sys.argv[1]
	start_time = float(sys.argv[2])
	# stop_time = sys.argv[3]
	with open(prt_folder+'/argv.txt', "r") as f:
		line=f.readline()
		line=''.join(line)
		old_t=line.split(",")[1]
		gen_t=line.split(",")[2]
		curtime=line.split(",")[3]
		file_size=int(line.split(",")[4])
		hours_d=float(line.split(",")[5])
		fixed_size=int(line.split(",")[6])
		time_seg=float(line.split(",")[7])

	print(prt_folder,start_time,old_t,gen_t,curtime)
	time_diff=time_dif(gen_t, curtime)

	generate_showtech(prt_folder)
	generate_fixed_allmsgs(prt_folder, "all_messages", start_time, fixed_size, file_size, hours_d, time_seg)
	generate_all_sip_msgs(prt_folder, "all_messages_r", time_diff)
	generate_output(prt_folder, hours_d, time_seg, start_time)

if __name__ == '__main__':
    main()
