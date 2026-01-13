import argparse
from patchright.sync_api import sync_playwright
from app import Storage, Scraper, config, Evaluator, Notifier, logger
import json
import time

def main():
    logger.info("=== Iniciando Job Scout ===")

    parser = argparse.ArgumentParser(description="Job Matcher - Meu Padrinho")
    parser.add_argument("--dry-run", action="store_true", help="Não notifica, só mostra resultados")
    parser.add_argument("--force", action="store_true", help="Reavalia vagas já vistas")
    args = parser.parse_args()

    if not config.api_key:
        print("Faltando API_KEY")
        return

    if not config.resume:
        print("Faltando currículo")
        return

    # carrega config
    db = Storage(db_path=config.db_path)
    evaluator = Evaluator(api_key=config.api_key, model=config.model)
    notifier = Notifier()

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

    # scrape
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(storage_state=storage_state)

        scraper = Scraper(context)
        links = scraper.get_job_links()

        if not links:
            logger.warning("Nenhuma vaga encontrada nesta execução")
            return

        for link in links:
            if db.is_visited(link):
                logger.debug(f"Pulando vaga já visitada: {link}")
                continue

            logger.info(f"Analisando vaga: https://meupadrinho.com.br{link}")

            try:
                job_data = scraper.get_job_details(link)
                logger.info(f"  Título: {job_data['title']}")

                score_result = evaluator.evaluate(job_data, config.resume, config.profile)
                logger.info(f"  Score: {score_result.score}/100 | Decisão: {score_result.decision}")

                if score_result.score >= config.min_score and not args.dry_run:
                    notifier.notify_job(job_data, score_result)
                else:
                    logger.debug(f"Score abaixo do mínimo ({config.min_score})")

                job_data["evaluation"] = score_result.to_dict()
                db.save_job(job_data)
            except Exception as e:
                logger.exception(f"Erro ao analisar vaga: {e}")

            time.sleep(10)

        logger.info("Fechando navegador...")
        browser.close()

        logger.info("=== Job Scout finalizado ===")

if __name__ == "__main__":
    main()