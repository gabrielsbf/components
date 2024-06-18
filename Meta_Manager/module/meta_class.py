from configparser import ConfigParser
import requests
import json
import threading
from components.Date_Utils.module.date_time_utils import Date_Utils
import os

class Social_Manager(Date_Utils):

	def	__init__(self, account, config_path, data_path, endpoints_path='standard', ):
		super().__init__()
		self.account_name = account
		self.config_path = config_path
		self.cred = self.display_credentials()
		self.url_requests = self.display_credentials('request')
		self.endpoints_path = './components/Meta_Manager/utils/' if endpoints_path=='standard'  else endpoints_path
		self.data_path = data_path 
		

	def	display_credentials(self, section=''):
		parser = ConfigParser()
		parser.read(self.config_path)
		tuple_items = parser.items(self.account_name) if section == '' else parser.items(section)
		obj_items = {i[0] : i[1] for i in tuple_items}
		return obj_items

	def	write_new_temp_token(self, new_token):
		parser = ConfigParser(self.cred)
		parser.read(self.config_path)
		parser.set(self.account_name,"token", new_token)
		with open(self.config_path, 'w') as file:
			parser.write(file)

	def write_new_long_token(self, token_temp):
		parser_app = self.display_credentials('myapp')
		response = self.fetch_data(self.url_requests["domain"]
				+"oauth/access_token?grant_type=fb_exchange_token&client_id="
				+parser_app["client_id"]
				+ "&client_secret="
				+parser_app["client_secret"]
				+"&fb_exchange_token="
				+token_temp)
		access_token = response["access_token"]
		parser = ConfigParser(self.cred)
		parser.read(self.config_path)
		parser.set(self.account_name,"token_30days", access_token)
		with open(self.config_path, 'w') as file:
			parser.write(file)

		return access_token

	def fetch_data(self, url):
		response = requests.get(url)
		return response.json()

	def	test_req(self):
		"""
		----
		Name:
		----
		test_req

		----
		Description: 
		----

		----
		Package Content:
		----
		
		"""
		url_test = "https://graph.facebook.com/v19.0/me?fields=id%2Cname&access_token="
		token = "" if self.cred.get("token_30days") == None else self.cred["token_30days"]
		response = self.fetch_data(url_test + token)
		while response.get("error") != None:
			new_token = input("Give a new token to the: " + self.account_name + " account - ")
			self.write_new_temp_token(new_token)
			token = self.write_new_long_token(new_token)
			response = self.fetch_data(url_test + token)
		return True

	# def extract_metric(self, json_obj):

	def makeRequest(self, *args, media = "", token = "" ):
		arrayRequest = []

		for i in range(len(args)):
			url = self.url_requests['domain'] + media + args[i] + self.url_requests['prefix_acesstoken'] + token
			print("url request is ", url )
			thread = threading.Thread(target=lambda : arrayRequest.append(self.fetch_data(url)))

			thread.start()
			thread.join()
		return arrayRequest

	def getJsonFile(self, file_name, file_folder='.'):

		with open(file_folder + "/" + file_name + ".json") as json_file:
			data = json.load(json_file)
		return data

	def writeJsonFile(self, file_name, archive, file_folder='.'):
		archive = json.dumps(archive)

		with open( file_folder + "/" + file_name + ".json", "w") as json_file:
			json_file.write(archive)

	def endpoints(self, type, period_obj=None):
		js_obj = self.getJsonFile(file_name="endpoints", file_folder = self.endpoints_path)[type]

		date = list(filter(lambda x : x == '$(since_date)' or x == '$(until_date)', js_obj))
		period = period_obj if not(date == []) else None
		def cases(iter):
			match iter:
				case '$(since_date)':
					return period["start_date"]["unix_time"]
				case '$(until_date)':
					return period["final_date"]["unix_time"]
				case _:
					return iter
		url = ''
		for i in js_obj:
			url = ''.join([url, cases(i)])
		return url

	def face_post_by_url(self, link):
		page_id = self.cred["face_page_id"]
		print(f"link is : {link}")
		len_substr = link.rfind('/') + 1
		post_id = link[len_substr:len(link)]
		endpoint = self.endpoints('face_post_desc')
		data = self.makeRequest(page_id +"_"+ post_id + endpoint, token=self.cred["token_30days"])
		return data

	def face_description(self, date_optional=None):
		self.date_optional = date_optional
		date_obj = self.return_period()
		request_validated = self.endpoints('face_desc', date_obj)
		if request_validated == False:
			return False
		face_request = self.makeRequest(request_validated,
										media=self.cred['face_id'],
										token=self.cred['token_30days'])
		print(face_request)
		description_data = list(face_request[0]["data"])

	#print("First Dict JSON New", description_data)
		try: next_page = face_request[0]["paging"]["next"]
		except: next_page = 0

		while next_page != 0:
			# print("Entering in loop While")
			new_request = requests.get(next_page)
			newJson_file = new_request.json()
			dataFile =list(newJson_file["data"])
			# print(f"Data File to Append: \n type: {type(dataFile)}, \n texto: {dataFile}")
			# print("File JSON Data new", dataFile)
			description_data =  description_data + dataFile
			print(f"Description Data File: \n type: {type(description_data)}, \n texto: {description_data}")
			try:
				next_page = newJson_file["paging"]["next"]
			except:
				next_page = 0
				#print("Entering in except")

		def new_key(value):
			new_dict = {}
			new_dict.update({"post_id": value.get("id"),
							"type" : value["attachments"]["data"][0].get("media_type"),
							"permalink_url" : value.get("permalink_url"),
							"message" : value.get("message"),
							"created_time" : value.get("created_time")
							})
			return new_dict

		new_desc = list(map(new_key, description_data))
		print(new_desc)
		return [new_desc, date_obj]

	def face_post_unique_metrics(self, data_obj):
		request_validated1 = self.endpoints('face_metric1')
		request_validated2 = self.endpoints('face_metric2')
		if request_validated1 == False or request_validated2 == False:
			return False
		print(data_obj)
		data = self.makeRequest(data_obj["post_id"] +
								request_validated1,
								data_obj["post_id"] +
								request_validated2,
								token=self.cred['token_30days'])

		metrics_col = {}
		metrics_col["post_id"] = data_obj["post_id"]
		try:		metrics_col["shares"] = data[1]["shares"]["count"]
		except: 	metrics_col["shares"] = 0
		metrics_col["comments"] = data[1]["comments"]["summary"]["total_count"]
		for type in data[0]["data"]:
			metric_title = type["title"]
			values = type["values"][0]
			match metric_title:
					case "Lifetime Total post Reactions by Type.":
						reactions = type["values"][0]["value"]
						metrics_col["like"] = 0 if reactions.get("like")== None else reactions.get("like")
						metrics_col["haha"] = 0 if reactions.get("haha") == None else reactions.get("haha")
						metrics_col["love"] = 0 if reactions.get("love") == None else reactions.get("love")
						metrics_col["sorry"] = 0 if reactions.get("sorry") == None else reactions.get("sorry")
						metrics_col["wow"] = 0 if reactions.get("wow") == None else reactions.get("wow")
						metrics_col["anger"] = 0 if reactions.get("anger") == None else reactions.get("anger")

					case "Lifetime Matched Audience Targeting Consumers on Post":
						metrics_col["unique_clicks_on_post"] = values.get("value")
						#print("cliques únicos no post: ",metrics_col["unique_clicks_on_post"])
					case "Lifetime Engaged Users":
						metrics_col["engaged_users"] = values.get("value")
					case "Lifetime People who have liked your Page and engaged with your post":
						metrics_col["engaged_fans"] = values.get("value")
					case "Lifetime Post Total Reach":
						metrics_col["reach"] = values.get("value")
						#print("Alcance: ", metrics_col["reach"])
					case _:
						print("Não entrei em nenhum case")
		return metrics_col

	def face_post_metrics(self, posts_obj='file', file_name=None):

		if posts_obj == 'file':
			posts = self.getJsonFile(file_name, self.data_path)
		else:
			posts = posts_obj

		def get_metrics(value):
			metrics = self.face_post_unique_metrics(value)
			return metrics
		new_metrics = list(map(get_metrics, posts))
		return new_metrics

	def face_video_metric_unique_metrics(self, video_obj):
		resp = self.makeRequest(video_obj["post_id"] + self.endpoints('face_video_metric'),
						token=self.cred["token_30days"])
		metrics = resp[0]["data"]
		new_video_metrics = {}
		new_video_metrics['post_id'] = video_obj["post_id"]
		for type in metrics:
			metric_title = type["title"]
			lifetime = type["period"]
			values = type["values"][0]
			if lifetime == "lifetime":
				new_video_metrics[metric_title] = values["value"]
		return new_video_metrics

	def face_video_metrics(self, posts_obj='file', file_name=None):
		if posts_obj == 'file':
			videos = self.getJsonFile(file_name, self.data_path)
		else:
			videos = posts_obj
		new_videos = list(map(self.face_video_metric_unique_metrics, videos))
		return new_videos

	def insta_description(self, date_optional=None):
		self.date_optional = date_optional
		date_obj = self.return_period()
		request_validated = self.endpoints('insta_desc', date_obj)
		if request_validated == False:
			return False
		insta_request = self.makeRequest(request_validated,
						media=self.cred['insta_id'],
						token=self.cred['token_30days'])
		js_obj = insta_request[0]
		new_desc = js_obj["data"]
		try: next_page = insta_request[0]["paging"]["next"]
		except: next_page = 0
		while next_page != 0:
			# print("Entering in loop While")
			new_request = requests.get(next_page)
			new_data_file = new_request.json()
			new_data = list(new_data_file["data"])
			new_desc = new_desc + new_data
			try:
				next_page = new_data_file["paging"]["next"]
			except:
				next_page = 0

		return [new_desc, date_obj]

	def insta_post_metric(self, posts):
		if posts["media_product_type"] == "FEED":
			request_validated = self.endpoints('insta_metric_feed')
			if request_validated == False:
				return False
			url = posts["id"] + request_validated
		elif posts["media_product_type"] == "REELS":
			request_validated = self.endpoints('insta_metric_reels')
			if request_validated == False:
				return False
			url = posts["id"] + request_validated
		data = self.makeRequest(url, token=self.cred["token_30days"])
		info = data[0]["data"]
		metrics_dict = {i["name"]: i['values'][0]['value'] for i in info}
		metrics_dict["comments_count"] = posts["comments_count"]
		metrics_dict["like_count"] = posts["like_count"]
		metrics_dict["media_product_type"] = posts["media_product_type"]
		metrics_dict["id"] = posts["id"]
		return metrics_dict

	def insta_metrics(self, posts_archive="file", file_name=None):
		if posts_archive == "file":
			posts = self.getJsonFile(file_name, self.data_path)
		else:
			posts = posts_archive

		def get_metrics(value):
			metrics = self.insta_post_metric(value)
			return metrics
		new_metrics = list(map(get_metrics, posts))
		return new_metrics

	def creating_text_for_obj(self, json, date, separator):
		print(json)
		message = f"""Métricas Facebook - datas:{date[0]} a {date[1]}:
"""
		metric_sum = {"comments" : 0,
					"reach": 0,
					"shares": 0,
					"unique_clicks_on_post": 0}
		def message_text(prefix, obj):
			text = prefix + obj if obj != None else prefix + "(CAMPO AUSENTE)"
			return text
		for obj in json:
			data = message_text("data do post : ", obj["created_time"])
			desc = message_text("mensagem: ", obj["message"])
			link = message_text("link: ", obj["permalink_url"])
			metric_sum["comments"] += obj["comments"]
			metric_sum["reach"] += obj["reach"]
			metric_sum["shares"] += obj["shares"]
			metric_sum["unique_clicks_on_post"] += obj["unique_clicks_on_post"]
			# like:{obj["like"]}
			# haha: {obj["haha"]}
			# love: {obj["love"]}
			# sorry: {obj["sorry"]}
			# wow: {obj["wow"]}
			# anger: {obj["anger"]}
			metrics = f"""****************
MÉTRICAS

compartilhamentos: {obj["shares"]}
comentários: {obj["comments"]}
alcance: {obj["reach"]}
engajamento: {obj["unique_clicks_on_post"]}
"""
			message = '\n'.join([message, link, data, desc,	 metrics, separator])
		sum_metrics = F"""
SOMA MÉTRICAS NO GERAL
compartilhamentos: {metric_sum["shares"]}
comentários: {metric_sum["comments"]}
alcance: {metric_sum["reach"]}
engajamento: {metric_sum["unique_clicks_on_post"]}
"""
		message = '\n'.join([message, sum_metrics])
		return message

	def merging_objects_by_id(self, unique_obj1, obj2, id_field_obj1="post_id", id_field_obj2="post_id"):

		def merging_unique_objects_by_id(unique_obj1, obj2, id_field_obj1, id_field_obj2):
			append_obj = list(filter(lambda x: x[id_field_obj2] == unique_obj1[id_field_obj1], obj2))
			print("APPEND OBJECT : ", append_obj)
			data = append_obj[0]
			for i in data.keys():
				print("i is: " ,i)
				unique_obj1[i] = data[i]
		for i in unique_obj1:
			merging_unique_objects_by_id(i, obj2, id_field_obj1, id_field_obj2)
