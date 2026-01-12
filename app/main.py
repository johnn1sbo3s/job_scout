import argparse
from patchright.sync_api import sync_playwright
from app import Storage, Scraper, config, Evaluator, Notifier
import json
import time

def main():
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

        print("Buscando vagas...")
        links = scraper.get_job_links()

        if not links:
            print("Nenhuma nova vaga encontrada.")
            browser.close()
            return

        for link in links:
            if db.is_visited(link):
                continue

            print(f"Analisando nova vaga: https://meupadrinho.com.br{link}")
            job_data = scraper.get_job_details(link)

            score_result = evaluator.evaluate(job_data, config.resume, config.profile)

            if score_result.score >= config.min_score:
                if not args.dry_run:
                    success = notifier.notify_job(job_data, score_result)
                    if success:
                        print(f"Notificação enviada!\n")
                else:
                    print(f"[DRY-RUN] Notificação seria enviada\n")
            else:
                print(f"Score abaixo do mínimo ({config.min_score})\n")

            job_data["evaluation"] = score_result.to_dict()
            db.save_job(job_data)
            print(f"Vaga '{job_data['title']}' salva!")
            time.sleep(10)

        browser.close()

if __name__ == "__main__":
    main()