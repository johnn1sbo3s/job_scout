import json
import os
import re
import requests
from dataclasses import dataclass, asdict
from .logger import logger

ROUTELLM_BASE_URL = "https://routellm.abacus.ai/v1"


@dataclass
class EvalResult:
    score: float
    decision: str
    confidence: float
    reasons: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    notes: str

    @staticmethod
    def from_dict(d):
        return EvalResult(
            score=float(d.get("score", 0)),
            decision=str(d.get("decision", "skip")),
            confidence=float(d.get("confidence", 0.5)),
            reasons=d.get("reasons", []),
            matched_skills=d.get("matched_skills", []),
            missing_skills=d.get("missing_skills", []),
            notes=d.get("notes", "")
        )

    def to_dict(self):
        return asdict(self)


class Evaluator:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = ROUTELLM_BASE_URL

    def _extract_json(self, text):
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            pass

        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not m:
            raise ValueError(f"Resposta sem JSON válido: {text[:500]}")
        return json.loads(m.group(0))

    def evaluate(self, job_data, resume_text, profile, timeout_s=60):
        logger.debug(f"Enviando requisição para LLM (modelo: {self.model})")

        language = profile.get("language", "pt-BR")

        system = (
            f"Você é um avaliador de vagas de emprego. "
            f"TODAS as respostas devem ser escritas exclusivamente em {language}. "
            f"Não misture idiomas. "
            f"Avalie o fit entre o candidato e a vaga com base no currículo e preferências. "
            f"Responda APENAS com JSON válido (sem markdown, sem explicações extras)."
        )

        user_prompt = {
            "candidate": {
                "resume": resume_text,
                "profile": {
                    "target_seniority": profile.get("target_seniority", []),
                    "must_have": profile.get("must_have", []),
                    "can_have": profile.get("can_have", []),
                    "avoid": profile.get("avoid", []),
                    "notes": profile.get("notes", ""),
                }
            },
            "job": {
                "title": job_data.get("title", ""),
                "company": job_data.get("company", ""),
                "description": job_data.get("description", ""),
            },
            "instructions": [
                "Calcule um score de 0 a 100 baseado no fit geral.",
                "Se a vaga mencionar tecnologias do 'must_have', aumente o score.",
                "Se mencionar tecnologias do 'avoid', reduza drasticamente o score.",
                "Se a senioridade não bater com 'target_seniority', reduza o score.",
                "Se a descrição for vaga/incompleta, reduza a 'confidence'.",
                "Decida 'apply' se score >= 70 e não tiver red flags, senão 'skip'.",
            ],
            "output_format": {
                "score": "number (0-100)",
                "decision": "string ('apply' ou 'skip')",
                "confidence": "number (0.0-1.0)",
                "reasons": "array of strings (motivos principais)",
                "matched_skills": "array of strings (tecnologias que batem)",
                "missing_skills": "array of strings (requisitos que faltam)",
                "notes": "string (observações extras)"
            }
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout_s,
            )
            r.raise_for_status()

            data = r.json()
            content = data["choices"][0]["message"]["content"]
            result_dict = self._extract_json(content)
            logger.debug("Resposta recebida do LLM")

            return EvalResult.from_dict(result_dict)
        except Exception as e:
            logger.exception(f"Erro ao avaliar vaga: {e}")
            raise
