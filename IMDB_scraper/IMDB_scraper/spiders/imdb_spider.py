import scrapy 

class ImdbSpider(scrapy.Spider):
	name = 'imdb_spider'

	start_urls = ['https://www.imdb.com/title/tt5348176/']
	
	def parse(self, response):
		'''yields the cast & crew page for the given work'''
				
		for url in self.start_urls:
			credURL = url + 'fullcredits/'
			yield scrapy.Request(url=credURL, callback=self.parse_full_credits)

	def parse_full_credits(self, response):
		'''Yields URLs for IMDB pages of each actor in the work'''
		
		# Get list of URLs for actor pages
		actor_urls = [a.attrib["href"] for a in response.css("td.primary_photo a")]
		for url in actor_urls:
			#href only contains ID, not full link
			actorURL = 'https://www.imdb.com' + url
			yield scrapy.Request(url=actorURL, callback=self.parse_actor_page) 

	def parse_actor_page(self, response):
		'''yields actor and film/show names as a key-value pair for each acting credit'''
		
		# Every title is written as 'actor name - IMDB'
		# We can extract just the name using string indexing
		title = response.css('title::text').getall()[0]
		name = title[:len(title) - 7]

		# From div.filmo-rows, we filter out film/tv IDs 
		# that are not acting credits 
		credIDs = response.css('div.filmo-row::attr(id)').getall()
		projects = [l[6:] for l in credIDs if 'actor' in l]

		titleFunc = lambda p: response.css('div.filmo-row a[href*="' + p + '"]::text').get()
		# Then, find the film/tv show name under the correct link
		actedList = [titleFunc(p) for p in projects]

		for acted in actedList:
			yield {'actor' : name, 'movie_or_TV_name' : acted}