import json
from patchright.sync_api import BrowserContext
from .logger import logger

class Scraper:
    def __init__(self, context: BrowserContext):
        self.context = context

    def get_job_links(self):
        logger.debug("Aguardando carregamento da página...")
        page = self.context.new_page()
        page.goto("https://meupadrinho.com.br/", wait_until="domcontentloaded")

        page.wait_for_selector("a.card-job", timeout=10000)

        main_frame = page.locator("div.flex.flex-col.space-y-4.max-w-4xl.mx-auto")
        card_jobs = main_frame.locator("a.card-job").all()

        links = [card.get_attribute("href") for card in card_jobs]
        page.close()

        logger.info(f"Encontrados {len(links)} links de vagas")
        return [f"https://meupadrinho.com.br{l}" for l in links if l]

    def get_job_details(self, job_link):
        logger.debug(f"Extraindo detalhes da vaga: {job_link}")

        page = self.context.new_page()
        page.goto(job_link, wait_until="domcontentloaded")

        # Seletor do H1 que você encontrou
        h1_selector = "h1.text-2xl.md\\:text-3xl.font-serif.font-bold.mb-2.text-claude-dark"
        page.wait_for_selector(h1_selector)
        title = page.locator(h1_selector).text_content().strip()

        company_element = page.locator("div.flex.items-center.flex-wrap.gap-x-4.gap-y-1.mb-1.text-claude-gray-700")
        company = company_element.locator("span.font-medium").text_content().strip()

        description_items = page.locator("ul.space-y-1.text-claude-gray-700.text-sm.pl-2").all_inner_texts()
        description = "; ".join(filter(None, [t.strip() for t in description_items])).replace("\n", " ")

        subscription_link = page.locator("a").filter(has_text="Candidatar-se agora ").get_attribute("href")

        page.close()
        return {
            "title": title,
            "company": company,
            "description": description,
            "link": job_link,
            "subscription_link": subscription_link
        }