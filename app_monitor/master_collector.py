
#! /usr/bin/python
# -*- coding: utf8 -*-


"""
Master Collector for MX140 v1.0
-------------- ----------------
"""

#from __future__ import unicode_literals
import twitter, twython
import json, cPickle
import tokenizer
import os
from collections import Counter
import time, random
import git
from datetime import datetime
from email.utils import parsedate_tz, mktime_tz


# ------------------------------------------------ ------------------------------------------------>
# ------------------------------------------------>
def dual_login(app_data, user_data):
    """
    login, oauthdance and creates .credential file for specified user
    """
    APP_NAME = app_data['AN']
    CONSUMER_KEY = app_data['CK']
    CONSUMER_SECRET = app_data['CS']
    CREDENTIAL = '.'+user_data['UN']+'.credential'
    try:
        (oauth_token, oauth_token_secret) = twitter.oauth.read_token_file(CREDENTIAL)
        print '[Load]: %s' % CREDENTIAL
    except IOError, e:
        (oauth_token, oauth_token_secret) = twitter.oauth_dance(APP_NAME, CONSUMER_KEY, CONSUMER_SECRET)
        twitter.oauth.write_token_file(CREDENTIAL, oauth_token, oauth_token_secret)
        print '[Save:] %s' % CREDENTIAL
    api1 = twitter.Twitter(domain='api.twitter.com', api_version='1.1',
        auth=twitter.oauth.OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET))
    api2 = twython.Twython(CONSUMER_KEY, CONSUMER_SECRET, oauth_token, oauth_token_secret)
    return api1, api2



def do_log(dat_file=".mx140.dat"):
    # login
    global api01, api02
    print "[APISTATE]: ",
    app_data, user_data = cPickle.load(open(dat_file,'r'))
    api01, api02 = dual_login(app_data, user_data)
    print "ok"
    return

def do_checkpath():
	# pathchek
    global out_dir
    print '[PATH_STATE]: ',
    out_dir = "out/"
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    print 'ok'
    return


def fetch_tweets_from_list(owner_screen_name="MX_en140",\
			slug="mx140-opinion",\
			include_entities="false",\
			count="200",\
			since_id="600000000000000000",\
			max_id="0"):
	"""
	fetches all more recent tweets from a given list
	returns a batch list with all more recent twitter status objects
	"""
	#global very_last_id
	batch = []
	# primer collect, trata de traerlos todos
	try:
		new_statuses = api01.lists.statuses(owner_screen_name=owner_screen_name,\
											slug=slug,\
											include_entities=include_entities,\
											count=count,\
											since_id=since_id)
		if (len(new_statuses) > 2):
			batch.extend(new_statuses)
			max_id = new_statuses[-1]["id"]-1
			# update the since_id
			very_last_id = new_statuses[0]["id"]
			print "[get]:",len(new_statuses),"new statuses"
			print "\t\tfrom:", new_statuses[-1]["id"], "created at:", new_statuses[-1]["created_at"]
			print "\t\tto:", new_statuses[0]['id'], "created_at:", new_statuses[0]["created_at"]
	except:
		print "[FAIL]: max_id = ", max_id
		new_statuses = []
	# una vez hecho el primer collect, trae mas
	while(len(new_statuses)>2):
		try:
			new_statuses = api01.lists.statuses(owner_screen_name=owner_screen_name, \
												slug=slug, \
												include_entities=include_entities, \
												count=count, \
												since_id=since_id, \
												max_id=max_id)
			batch.extend(new_statuses)
			max_id = new_statuses[-1]["id"]-1
			print "[get]:",len(new_statuses),"new statuses"
			print "\t\tfrom:", new_statuses[-1]["id"], "created at:", new_statuses[-1]["created_at"]
			print "\t\tto:", new_statuses[0]['id'], "created_at:", new_statuses[0]["created_at"]
		except:
			print "[FAIL]: max_id = ", max_id
			new_statuses = []
			break
	# before leave, update marks
	batch.reverse()
	return batch


def count_words(texts_batch, stopwords = []):
	"""
	tokenize, count and filter stop words from a batch of texts
	return a counter or dictionary object
	"""
	tokens = []
	T = tokenizer.Tokenizer()
	# tokenize
	for text in texts_batch:
		tokens.extend(T.tokenize(text))
	# count
	C = Counter(tokens)
	# filter
	for sw in stopwords:
		if C.has_key(sw): C.pop(sw)
	for k in C.keys():
		if len(k)<4: C.pop(k)
	return C



def enlight_bag(bag=[]):
	"""
	select only interesting attributes of the status object, enlightening it
	"""
	newbag = [{'t':s['text'], \
				'u':s['user']['screen_name'], \
				'n':s['user']['name'], \
				'i':s['user']['profile_image_url'], \
				'c':str(datetime.fromtimestamp(mktime_tz(parsedate_tz(s['created_at']))))[5:], \
				'l':u"https://twitter.com/"+s['user']['screen_name']+u"/status/"+s['id_str']\
				} for s in bag]
	return newbag

container = """
<div class="twcontainer">
 	<img src="TOKEN_I" alt="TOKEN_N" style="float:left; margin:0 15px 20px 0;" />
	<table>
    	<tr> 
    		<td>
    			<a class="name" href="https://twitter.com/TOKEN_U" target="_blank">TOKEN_N</a>
    		</td> 
    	</tr>
    	<tr> 
    		<td>
    			<span class="screenname">
    				<a href="https://twitter.com/TOKEN_U" target="_blank">@TOKEN_U</a>
    			</span>
    			<span class="createdtime"> 
    				<a href="TOKEN_L" target="_blank">TOKEN_C</a> 
    			</span>
    		</td>
    	</tr>
    	<tr> <td class="tweettext">TOKEN_T</td> </tr>
  	</table>
  	<hr>
</div>
"""
titler = """
<div class="tooltiphead">
        <div class="toptitle">
        		<div><a target="_blank" href="https://twitter.com/search?q=TOKEN_H" class="spantitle">
        			<span>TOKEN_H</span></a>
        		</div>
    			<div><a href="#">
    				<span class="spancount">TOKEN_O</span>
    				<br>
    				<span class="spanmenc">menciones</span></a>
    			</div>
        </div>
</div>
"""
ender="""
<div class="twend">
	<div>
		<span class="ender1">Palabras Asociadas:</span><br><br>
		<span class="ender2">TOKEN_RW</span>
	</div>
</div>
"""
# ------------------------------------------------>
# ------------------------------------------------ ------------------------------------------------>



if __name__ == '__main__':

	do_checkpath()
	do_log()
	list_of_lists =  ["mx140-ejecutivo", \
					"mx140-gobernadores", \
					"mx140-opinion", \
					"mx140-senadores", \
					"mx140-diputados", \
					"mx140-pri", \
					"mx140-pan", \
					"mx140-prd"]
	rlis = {"mx140-ejecutivo":"poder ejecutivo", \
				"mx140-gobernadores":"gobernadores", \
				"mx140-diputados":"diputados", \
				"mx140-senadores":"senadores", \
				"mx140-opinion":"lideres de opinion", \
				"mx140-pri":"pri", \
				"mx140-pan":"pan", \
				"mx140-prd":"prd"}


	most_recent_ids = {l:"600000000000000000" for l in list_of_lists}
	#buffers = {l:[] for l in list_of_lists}; cPickle.dump (buffers, open('buffers.cpk','w'))
	#stopwords = [w.strip().rstrip() for w in open('nsw.txt','r').readlines()]
	stopwords = [w.strip().rstrip().decode('utf8','ignore') for w in open('stopwords.txt','r').readlines()]
	#print stopwords
	max_buffer_size = 10000
	max_most_common_words = 30
	min_bag_size = 1
	max_status_buffsize = 10

	while(True):
		# init and load datastructs
		pack_json = {}
		pack_statuses = {}
		all_batch = []
		buffers = cPickle.load(open("buffers.cpk",'r'))
		most_recent_ids = cPickle.load(open("mrids.cpk",'r'))
		status_buff = cPickle.load(open('status.buff','r'))
		
		# fill from lists
		for l in list_of_lists:
			pack_json[l] = {}
			# get all available messages
			batch = fetch_tweets_from_list(owner_screen_name="MX_en140",\
										slug=l,\
										include_entities="false",\
										count="200",\
										since_id=most_recent_ids[l],\
										max_id="0")
			# update most_recent_ids
			try:
				most_recent_ids[l] = batch[-1]['id_str']
			except:
				most_recent_ids[l] = most_recent_ids[l]
			print "[batch]:",l,len(batch), most_recent_ids[l]
		
			# store on buffers
			pack_statuses[l] = batch
			all_batch.extend(batch)
			new_texts = [s['text'].lower() for s in batch]
			buffers[l].extend(new_texts)
			if ( len(buffers[l])>max_buffer_size ):
				buffers[l] = buffers[l][-max_buffer_size:]
			buffers['all'].extend(new_texts)
			if ( len(buffers['all'])>max_buffer_size ):
				buffers['all'] = buffers['all'][-max_buffer_size:]
			print "[buffer]:",l,len(buffers[l]), len(new_texts)

			#count words
			C = count_words(buffers[l], stopwords)
			top_words = C.most_common(max_most_common_words)

			#select messages for each selected word
			bag = []
			#if len(top_words)>0: top_words.reverse()
			for (w,c) in top_words:
				# the bag contains current status with top words
				try:
					bag = [s for s in batch if w in s['text'].lower()]
				except:
					bag = []
				
				pack_json[l][w] = c#{"count": c, "bag":[]}

				# here you filter and administrate messages buffer
				# here you can make dynamic assignments
				
				# so pack only words with enough pressence, enlight the bag
				if ((len(bag)>=min_bag_size) or (len(bag)==0)):
					#pack_json[l][w] = c#{"count": c, "bag":bag[:min_bag_size]}
					lightbag = enlight_bag(bag)
					try:
						status_buff[l][w].extend(lightbag)
					except:
						status_buff[l][w] = lightbag
					# crop status_buff
					if len(status_buff[l][w])>max_status_buffsize: 
						status_buff[l][w] = status_buff[l][w][-max_status_buffsize:]
				#elif len(bag)==0:
				#	pack_json[l][w] = c#{"count": c, "bag":[]};			

		# for the all buffer
		C = count_words(buffers['all'], stopwords)
		top_words = C.most_common(max_most_common_words)
		pack_json['all'] = {w: c for (w,c) in top_words}
		
		for (w,c) in top_words:
			try:
				bag = [s for s in all_batch if w in s['text'].lower()]
			except:
				bag = []
			pack_json['all'][w] = c
			if ((len(bag)>=min_bag_size) or (len(bag)==0)):
				#pack_json['all'][w] = c#{"count": c, "bag":bag[:min_bag_size]}
				lightbag = enlight_bag(bag)
				try:
					status_buff['all'][w].extend(lightbag)
				except:
					status_buff['all'][w] = lightbag
				# crop status_buff
				if len(status_buff['all'][w])>max_status_buffsize: 
					status_buff['all'][w] = status_buff['all'][w][-max_status_buffsize:]
		

		# create containers for all the classes
		containers={}
		#select random list for status update
		current_list = random.choice(list_of_lists)
		current_keyword= ""
		current_asoc_ws = []

		for k in status_buff.keys():
			containers[k]={}
			if k==current_list: 
				current_keyword = random.choice(pack_json[current_list].keys())
			for w in status_buff[k].keys():
				
				if w in pack_json[k].keys():
					containers[k][w] = []
					# cross the array backwards and make containers
					for s in reversed(status_buff[k][w]):
						newC = container.replace('TOKEN_I',s['i']).replace('TOKEN_L',s['l']).replace('TOKEN_C',s['c'])
						newC = newC.replace('TOKEN_N',s['n']).replace('TOKEN_T',s['t']).replace('TOKEN_U',s['u'])
						containers[k][w].append(newC)
					# get most_common related words
					txstat = [s['t'].lower() for s in status_buff[k][w]]
					miniC = count_words(txstat, stopwords)

					if w==current_keyword:
						try: 
							current_asoc_ws= [cws for (cws,co) in miniC.most_common(6)[1:]]
						except:
							current_asoc_ws= [[cws for (cws,co) in miniC.most_common(6)]]
					related_words = ', '.join([cws for (cws,co) in miniC.most_common(6)[1:]])
					#form complete qtip content
					containers[k][w] = titler.replace('TOKEN_H', w.upper()).replace('TOKEN_O',str(pack_json[k][w]))+'<hr>'+('\n'.join(containers[k][w]))+ender.replace('TOKEN_RW', related_words)
		df = open('../mx140/public/js/containers.js','w')
		print >>df, "var tts = "+json.dumps(containers)+";"
		df.close();



		# save files and states
		json.dump(pack_statuses, open(out_dir+"mx140"+"-"+time.asctime()+".json",'w'))
		json.dump (pack_json, open('pack.json','w'))
		nf = open('../mx140/public/js/data.js','w')
		print >>nf, "var data = "+json.dumps(pack_json)+";"
		nf.close()
		cPickle.dump (buffers, open('buffers.cpk','w'))
		cPickle.dump (most_recent_ids, open('mrids.cpk','w'))
		cPickle.dump (status_buff, open('status.buff','w'))
		print ("[saved]: pack.json, buffers.cpk, mrids.cpk, status.buff")
		
		# commit to github (requieres sudo git config --global credential.helper store + login para guardar credentials)
		os.chdir('../mx140')
		git.add('--all')
		git.commit('[*-*]/~ :: Monitor Mx140 V1.0 - '+time.asctime())
 		git.create_simple_git_command('push')()
		os.chdir('../collector')
		print "\n\n[git]: ok :: " , time.asctime() 
		# then sleepover...
		
		#wait, publish something
		#current_list, current_keyword, current_asoc_ws must be ready
		try:
			current_status = u"El grupo de " + \
						rlis[current_list].upper() + \
						u" discute sobre "+ \
						current_keyword.upper() +\
						u" junto a [ " +\
						current_asoc_ws[1] + " ] y [ " +\
						current_asoc_ws[3] +\
						u" ]. [+] en http://mexicoen140.org.mx"
			if len(current_status)<127:
				current_status+=u" #M\u00C9XICOen140"
			ok_status = api01.statuses.update(status=current_status)
			print "[--<]: %s" % (ok_status['text'])
		except twitter.TwitterHTTPError as e:
			print "[x_X]: fuck :: %s" % e
		current_keyword= ""
		current_asoc_ws = []	

		#now procceed
		print "[sleeping]:", time.asctime()
		time.sleep(601)

