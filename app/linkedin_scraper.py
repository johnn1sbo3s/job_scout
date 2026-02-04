from .logger import logger
from .config import config
from urllib.parse import quote
import time

class LinkedinScraper:
	def __init__(self, page, queries):
		self.page = page
		self.username = config.linkedin_username
		self.password = config.linkedin_password
		self.queries = queries

	def _generate_search_url(self, query):
		base_url = "https://www.linkedin.com/search/results/content/"
		query_encoded = quote(query)
		url = f"{base_url}?keywords={query_encoded}&origin=FACETED_SEARCH&sid=Kb%2C&sortBy=%22date_posted%22"

		return url

	def get_job_posts(self):
		logger.debug("Fazendo login no Linkedin...")
		try:
			self.page.goto("https://www.linkedin.com/login")
			self.page.wait_for_selector("input#username")
			self.page.locator("#username").fill(self.username)
			self.page.locator("#password").fill(self.password)

			try:
				self.page.locator("label[for='rememberMeOptIn-checkbox']").click()
			except:
				pass

			time.sleep(2)
			self.page.locator("button.btn__primary--large.from__button--floating").click()
		except Exception as e:
			logger.error(f"Erro ao fazer login no Linkedin: {e}")
			return []

		all_job_posts = []

		for query in self.queries:
			logger.info(f"Fazendo busca no Linkedin (query: {query})...")
			time.sleep(5)
			try:
				complete_link = self._generate_search_url(query)
				self.page.goto(complete_link)
				self.page.wait_for_selector("div.search-results-container")
				results_container = self.page.locator("div.search-results-container")

				for _ in range(3):
					self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
					self.page.wait_for_timeout(2000)

				job_posts = self.page.locator("div.feed-shared-update-v2")

				for i in range(job_posts.count()):
					job_post = job_posts.nth(i)
					urn = job_post.get_attribute("data-urn")

					if not urn:
						logger.error("Erro ao extrair urn do post")
						continue

					link = f"https://www.linkedin.com/feed/update/{urn}"

					post_text = job_post.locator(".update-components-update-v2__commentary span.break-words span[dir='ltr']").first.inner_text()

					post = {
						"link": link,
						"text": post_text
					}
					all_job_posts.append(post)

			except Exception as e:
				logger.error(f"Erro ao fazer busca no Linkedin: {e}")
				return []

		self.page.close()
		return all_job_posts
