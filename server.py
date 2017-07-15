from __future__ import unicode_literals
#-*- coding:utf-8 -*-

import socket
import subprocess
import sys
import re, urllib, os, sys, urllib2
import MySQLdb
import youtube_dl

urlopen = urllib2.urlopen
encode = urllib.urlencode
retrieve = urllib.urlretrieve
cleanup = urllib.urlcleanup()

reload(sys)
sys.setdefaultencoding('utf-8')

db = MySQLdb.connect("localhost", "monitor", "password", "temps")
curs=db.cursor()

HOST = ""
PORT = 8888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Socket created')
s.bind((HOST, PORT))
print ('Socket bind complete')
s.listen(1)
print ('Socket now listening')

class MyLogger(object):
	def debug(self, msg):
		pass
	def warning(self, msg):
	 	pass
	def error(self, msg):
	 	print(msg)

def my_hook(d):
	if d['status'] == 'finished':
		print('Done downloading, now converting ...')

def video_title(url):
	try:
		webpage = vrlopen(url).read()
		title = str(webpage).split('<title>')[1].split('</title>')[0]
	except:
		title = 'Youtube Song'
	return title


def down_load(song):
	if "youtube.com/" not in song:
		try:
			query_string = encode({"search_query" : song})
			html_content = urlopen("https://www.youtube.com/results?" + query_string)
			search_results = re.findall(r'href=\"\/watch\?v=(.{11})',html_content.read())
		except:
			print('Network Error')
			return None
#		command = "youtube-dl -cit --embed-thumbnail --no-warnings --extract-audio --audio-format mp3 " + search_results[0]
#		print('song : %s ' %song)
		ydl_opts = {
			'outtmpl':'/home/pi/Desktop/music_list/'+song+'-%(id)s.%(ext)s',
			'format': 'bestaudio/best',
			'postprocessors':[{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
			'logger': MyLogger(),
			'progress_hooks': [my_hook],
		}
		
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			info_dict = ydl.extract_info(search_results[0], download=False)
			audio_title = info_dict.get('title', None)
			id = info_dict.get('id', None)
			print(info_dict['title'])
			ydl.download([search_results[0]])
		print('file_name : %s'% audio_title)
#		song = video_title(song)
		dir_name = "home/pi/Desktop/music_list/"+ song + "-" + id + ".mp3"
		print(dir_name)
		sql = "INSERT INTO list(songname,filename) VALUES('%s','%s')" % (song, dir_name )
		
		try:
			curs.execute(sql)
			db.commit()
		except:
			db.roolback()
		db.close()
#		song = video_title(song)
#		print('title : %s'% song)
	else:
#		command = "youtube-dl -cit --embed-thumbnail --no-warnings --extract-audio --audio-format mp3 " + song[song.find("=")+1:]
		song = video_title(song)
	try:
		print('Downloading %s'% song)
#		os.system(command)
	except:
#		print('Error downloading %s'% song)
		return None

def main():
	while True:
		conn, addr = s.accept()
		print("conneted by", addr)

		data=conn.recv(1024)
		data=data.decode("utf").strip()
		if not data: break
		print("Received: "+data)
		down_load(data)
		conn.close
	s.close()


main()
