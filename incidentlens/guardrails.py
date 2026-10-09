"""Explicit policy checks, Presidio redaction and optional local safety classification."""

import re
from collections import Counter

import httpx
import spacy
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerRegistry
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from incidentlens.config import Settings
from incidentlens.models import Finding

INJECTION = re.compile(
    r"ignore\s+(?:all\s+)?(?:previous|prior|system)\s+instructions"
    r"|reveal\s+(?:your\s+)?system\s+prompt|(?:print|reveal|exfiltrate)\s+(?:the\s+)?api\s+key"
    r"|<\|(?:im_start|system)\|>|\[INST\]|override\s+(?:the\s+)?system",
    re.I,
)
HARMFUL = re.compile(r"(?:steal|exfiltrate)\s+(?:credentials|passwords)|deploy\s+ransomware", re.I)
PUBLIC_DOMAIN_TERMS = (
    "Checkout Service",
    "Payments API",
    "Ledger Database",
    "Inventory API",
    "Stock Database",
    "Identity Service",
    "Commerce Team",
    "Payments Team",
    "Platform Team",
    "Supply Team",
    "Security Team",
    "Metric",
    "Demo API",
)


class Guardrails:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        if cfg.pii_ner:
            model = "en_core_web_sm"
            if not spacy.util.is_package(model):
                raise RuntimeError("PII NER requires en_core_web_sm. See setup instructions.")
        else:
            # Blank English NLP provides tokenization; PERSON detection requires the NER profile.
            model = str(cfg.data_dir / "spacy-tokenizer")
            if not (cfg.data_dir / "spacy-tokenizer").exists():
                spacy.blank("en").to_disk(model)
        nlp = SpacyNlpEngine(models=[{"lang_code": "en", "model_name": model}])
        nlp.load()
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers(nlp_engine=nlp)
        # Avoid the stock email recognizer's external public-suffix lookup; .test is deliberate.
        registry.remove_recognizer("EmailRecognizer")
        registry.add_recognizer(
            PatternRecognizer(
                supported_entity="API_KEY",
                patterns=[Pattern("demo_or_live_key", r"\b(?:sk|pk)-[A-Za-z0-9_-]{16,}\b", 0.95)],
            )
        )
        registry.add_recognizer(
            PatternRecognizer(
                supported_entity="EMAIL_ADDRESS",
                patterns=[
                    Pattern(
                        "synthetic_or_real_email",
                        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                        0.95,
                    )
                ],
            )
        )
        self.analyzer = AnalyzerEngine(nlp_engine=nlp, registry=registry)
        self.anonymizer = AnonymizerEngine()
        self.entities = ["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "API_KEY"]
        if cfg.pii_ner:
            self.entities.append("PERSON")

    def redact(self, text: str) -> tuple[str, list[Finding]]:
        results = self.analyzer.analyze(text=text, language="en", entities=self.entities)
        public_spans = [
            m.span()
            for term in PUBLIC_DOMAIN_TERMS
            for m in re.finditer(re.escape(term), text, re.I)
        ]
        results = [
            r
            for r in results
            if not (
                r.entity_type == "PERSON"
                and (
                    any(start <= r.start and r.end <= end for start, end in public_spans)
                    or text[r.start : r.end].strip(" \n\t|").lower()
                    in {term.lower() for term in PUBLIC_DOMAIN_TERMS}
                )
            )
        ]
        counts = Counter(r.entity_type for r in results)
        clean = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={"DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"})},
        ).text
        return clean, [Finding(kind=k, action="redacted", count=v) for k, v in counts.items()]

    def blocked(self, text: str) -> str | None:
        if INJECTION.search(text):
            return "prompt_injection"
        if HARMFUL.search(text):
            return "content_policy"
        return None

    def classify(self, text: str) -> bool:
        """Optional Llama Guard through Ollama. Failure is propagated, never treated as safe."""
        if not self.cfg.llama_guard_model:
            return True
        response = httpx.post(
            self.cfg.ollama_url + "/api/chat",
            json={
                "model": self.cfg.llama_guard_model,
                "messages": [{"role": "user", "content": text}],
                "stream": False,
            },
            timeout=45,
        )
        response.raise_for_status()
        verdict = response.json()["message"]["content"].strip().lower()
        if verdict.startswith("unsafe"):
            return False
        if verdict == "safe":
            return True
        raise ValueError("Safety classifier returned an unrecognized verdict")
