import argparse
from patchright.sync_api import sync_playwright
from app import Storage, Scraper, config, Evaluator, get_notifier, logger, LinkedinScraper
import json
import time

def run_linkedin(browser):
	context = browser.new_context(
		viewport={'width': 1920, 'height': 1080}
	)
	logger.info("Iniciando busca no Linkedin...")
	linkedin_scraper = LinkedinScraper(context.new_page(), '("vue" OR "vue.js") AND (frontend OR front-end) AND "vaga"')
	linkedin_posts = linkedin_scraper.get_job_posts()

	for post in linkedin_posts:
		if db.is_visited(post["link"]):
			continue

		score_result = evaluator.evaluate_linkedin_post(post, config.resume, config.profile)
		logger.info(f"Score: {score_result.score}/100 | Decisão: {score_result.decision}")

		job_data = {
			"title": score_result.title,
			"company": score_result.company,
			"link": post["link"],
			"subscription_link": post["link"],
		}

		if score_result.score >= config.min_score:
			notifier.notify_job(job_data, score_result)
		else:
			logger.debug(f"Score abaixo do mínimo ({config.min_score})")

		job_data["evaluation"] = score_result.to_dict()
		db.save_job(job_data, "linkedin")

	logger.info("Busca no Linkedin finalizada")

def run_meu_padrinho(browser):
	JOB_FILTERS = {
		"termoBusca": "",
		"cargos": ["frontend"],
		"formasTrabalho": ["remoto"],
		"niveis": [],
		"plataformas": [],
		"vagaEasyApply": False,
		"vagaVerificadaPorIa": False,
		"tiposContratacao": [],
		"apenasComRecrutador": False,
		"comEmailDeContato": False,
	}

	storage_state = {
		"cookies": [],
		"origins": [{
			"origin": "https://meupadrinho.com.br",
			"localStorage": [{
				"name": "job_filters",
				"value": json.dumps(JOB_FILTERS, ensure_ascii=False)
			}]
		}]
	}

	context = browser.new_context(storage_state=storage_state)
	scraper = Scraper(context)
	links = scraper.get_job_links()

	if not links:
		logger.warning("Nenhuma vaga encontrada nesta execução")
		return

	for link in links:
		if db.is_visited(link):
			continue

		logger.info(f"Analisando vaga: {link}")

		try:
			job_data = scraper.get_job_details(link)
			logger.info(f"Título: {job_data['title']}")

			score_result = evaluator.evaluate(job_data, config.resume, config.profile)
			logger.info(f"Score: {score_result.score}/100 | Decisão: {score_result.decision}")

			if score_result.score >= config.min_score:
				notifier.notify_job(job_data, score_result)
			else:
				logger.debug(f"Score abaixo do mínimo ({config.min_score})")

			job_data["evaluation"] = score_result.to_dict()
			db.save_job(job_data, "meu-padrinho")
		except Exception as e:
			logger.exception(f"Erro ao analisar vaga: {e}")

		time.sleep(10)

	logger.info("Fechando navegador da busca MP...")

def main():
	parser = argparse.ArgumentParser(description="Job Matcher - Meu Padrinho")
	parser.add_argument("--dry-run", action="store_true", help="Não notifica, só mostra resultados")
	parser.add_argument("--force", action="store_true", help="Reavalia vagas já vistas")
	args = parser.parse_args()

	logger.info("=== Iniciando Job Scout ===")

	if not config.api_key:
	  logger.error("Faltando API_KEY")
	  return

	if not config.resume:
	  logger.error("Faltando currículo")
	  return

	with sync_playwright() as p:
		browser = p.chromium.launch()

		run_meu_padrinho(browser)
		run_linkedin(browser)

		browser.close()

		logger.info("=== Job Scout finalizado ===")

if __name__ == "__main__":
	db = Storage(db_path=config.db_path)
	evaluator = Evaluator(api_key=config.api_key, model=config.model)
	notifier = get_notifier()

	main()