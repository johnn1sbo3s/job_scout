import telebot
from .config import config
from .logger import logger
import re

class BaseNotifier:
  def notify_job(self, job_data, score_result):
    raise NotImplementedError

class ConsoleNotifier(BaseNotifier):
  def notify_job(self, job_data, score_result):
    title = job_data.get("title", "Sem título")
    company = job_data.get("company", "N/A")
    score = score_result.score
    reasons = score_result.reasons or []

    logger.info("Nova vaga encontrada (modo console)")
    logger.info(f"Título: {title}")
    logger.info(f"Empresa: {company}")
    logger.info(f"Score: {score}/100")

    if reasons:
      logger.info("Motivos da avaliação:")
      for r in reasons:
        logger.info(f" - {r}")

    return True

class TelegramNotifier(BaseNotifier):
  def notify_job(self, job_data, score_result):
    def escape_markdown(text):
      if not text:
        return ""
      text = str(text)
      text = text.replace('_', r'\_')
      text = text.replace('*', r'\*')
      return text

    try:
      title = escape_markdown(job_data['title'])
      company = escape_markdown(job_data.get('company', 'N/A'))
      notes = escape_markdown(score_result.notes) if score_result.notes else ""

      message = "🔔 *Nova vaga encontrada!*\n\n"
      message += f"🔥 *{title}*\n"
      message += f"🏢 Empresa: {company}\n"
      message += f"🎯 Score: *{score_result.score}/100*\n"
      message += f"💪 Confiança: {score_result.confidence:.0%}\n\n"

      if score_result.matched_skills:
        skills = ', '.join([escape_markdown(s) for s in score_result.matched_skills])
        message += f"✅ *Tecnologias que batem:*\n{skills}\n\n"

      if score_result.missing_skills:
        skills = ', '.join([escape_markdown(s) for s in score_result.missing_skills])
        message += f"❌ *Tecnologias que faltam:*\n{skills}\n\n"

      if score_result.reasons:
        message += "💡 *Motivos principais:*\n"
        for reason in score_result.reasons:
          message += f"• {escape_markdown(reason)}\n"
        message += "\n"

      if notes:
        message += f"📝 {notes}\n\n"

      mp_link = f"https://meupadrinho.com.br{job_data['link']}"
      apply_link = job_data.get("subscription_link", "")
      message += f"👉 [Candidate-se!]({apply_link})\n"
      message += f"🔎 [Veja a vaga no Meu Padrinho]({mp_link})\n"

      self.bot.send_message(
        self.chat_id,
        message,
        parse_mode='Markdown',
        disable_web_page_preview=True
      )

      logger.info(f"Notificação enviada para o chat {self.chat_id}")
      return True
    except Exception as e:
      logger.error(f"Falha ao enviar notificação: {e}")
      return False

def get_notifier():
  if not config.telegram_bot_token or not config.telegram_chat_id:
    logger.warning("Telegram não configurado. Usando ConsoleNotifier.")
    return ConsoleNotifier()

  return TelegramNotifier()