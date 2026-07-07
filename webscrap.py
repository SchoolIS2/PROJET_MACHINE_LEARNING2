JUMIA_BASE_URL = "https://www.jumia.ci"

JUMIA_SEARCH_URL = JUMIA_BASE_URL + "/catalog/?q={query}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

# Mots à retirer d'une phrase du type "j'ai une montre casio"
# pour ne garder que les mots "produit" utiles à la recherche.
STOPWORDS_FR = {
    "j'ai", "jai", "j", "ai", "je", "veux", "voudrais", "cherche",
    "recherche", "voici", "voila", "il", "me", "faut", "un", "une",
    "des", "de", "du", "la", "le", "les", "et", "avec", "pour",
    "svp", "sil", "vous", "plait", "plaît", "acheter", "achete",
    "acheté", "trouve", "trouver", "montre", "moi",  # "montre" ici = verbe "montrer"
}


# Dictionnaire "métier" : vocabulaire fréquent des catégories vendues
# sur Jumia CI. Sert de référentiel pour corriger les fautes de frappe
# (ex: "motre" -> "montre"). Vous pouvez librement l'enrichir.
PRODUCT_VOCAB = [
    "montre", "telephone", "smartphone", "ordinateur", "laptop",
    "tablette", "ecouteur", "casque", "chargeur", "cable", "television",
    "televiseur", "frigo", "refrigerateur", "congelateur", "climatiseur",
    "ventilateur", "cuisiniere", "micro-onde", "mixeur", "blender",
    "chaussure", "sandale", "basket", "vetement", "robe", "chemise",
    "pantalon", "jean", "veste", "sac", "sac a main", "parfum",
    "creme", "maquillage", "rouge a levre", "bijou", "collier",
    "bague", "bracelet", "lunette", "casio", "samsung", "iphone",
    "tecno", "infinix", "xiaomi", "hisense", "nasco", "lg", "sony",
    "matelas", "canape", "table", "chaise", "lit", "armoire",
    "imprimante", "clavier", "souris", "manette", "console", "jeu",
    "batterie", "powerbank", "haut-parleur", "enceinte", "fer a repasser",
    "aspirateur", "moto", "velo", "pneu", "jouet", "couche", "biberon",
]
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List

# from config import STOPWORDS_FR, PRODUCT_VOCAB   # <-- décommenter une fois séparé

try:
    from rapidfuzz import fuzz, process as rf_process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

try:
    from spellchecker import SpellChecker
    HAS_SPELLCHECKER = True
except ImportError:
    HAS_SPELLCHECKER = False


# ---------------------------------------------------------------------------
# 2) NETTOYAGE + COMPRÉHENSION / CORRECTION ORTHOGRAPHIQUE
# ---------------------------------------------------------------------------

def strip_accents(text: str) -> str:
    """Retire les accents pour faciliter les comparaisons (motre/montre...)."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def tokenize(text: str) -> List[str]:
    """Découpe la phrase en mots simples (lettres/chiffres uniquement)."""
    text = text.lower().replace("’", "'")
    # Sépare "j'ai" en gardant l'apostrophe pour le filtrage stopwords
    tokens = re.findall(r"[a-zàâäéèêëîïôöùûüç0-9']+", text)
    return tokens


def clean_query(raw_text: str) -> List[str]:
    """
    Extrait de la phrase brute la ou les mots-clés "produit" utiles,
    en retirant les mots de liaison usuels.

    Exemple : "j'ai une montre casio" -> ["montre", "casio"]
    """
    tokens = tokenize(raw_text)
    keywords = []
    for tok in tokens:
        tok_norm = strip_accents(tok)
        if tok in STOPWORDS_FR or tok_norm in STOPWORDS_FR:
            continue
        if len(tok) <= 1:
            continue
        keywords.append(tok)
    return keywords


@dataclass
class SpellSuggestion:
    original: str
    corrected: str
    confidence: float          
    source: str                
    was_corrected: bool = field(init=False)

    def __post_init__(self):
        self.was_corrected = self.original.lower() != self.corrected.lower()


def correct_word(word: str, vocab: List[str] = PRODUCT_VOCAB) -> SpellSuggestion:
    """
    Tente de corriger un mot potentiellement mal orthographié.

    Stratégie (le "petit volet de compréhension" demandé) :
      1. Si le mot existe déjà tel quel dans le vocabulaire métier -> OK.
      2. Sinon on cherche le mot du vocabulaire métier le plus proche
         (similarité de chaînes de caractères, tolère 1-2 lettres
         d'erreur, ex: motre -> montre, telefone -> telephone).
      3. Si rien de suffisamment proche dans le vocabulaire métier,
         on retombe sur un correcteur orthographique français général
         (utile pour les marques ou mots hors vocabulaire connu).
      4. Si aucune correction fiable n'est trouvée, on garde le mot
         d'origine (ce peut être un nom de marque, ex: "casio").
    """
    word_l = word.lower()
    word_norm = strip_accents(word_l)

    vocab_norm = {strip_accents(v): v for v in vocab}

    # 1) Mot déjà correct
    if word_norm in vocab_norm:
        return SpellSuggestion(word, vocab_norm[word_norm], 100.0, "vocab_metier")

    # 2) Correction via le vocabulaire métier (rapidfuzz si dispo,
    #    sinon un fallback maison avec difflib)
    best_match, best_score = None, 0.0
    if HAS_RAPIDFUZZ:
        result = rf_process.extractOne(
            word_norm, list(vocab_norm.keys()), scorer=fuzz.ratio
        )
        if result:
            match_norm, score, _ = result
            best_match, best_score = vocab_norm[match_norm], score
    else:
        import difflib
        matches = difflib.get_close_matches(
            word_norm, list(vocab_norm.keys()), n=1, cutoff=0.6
        )
        if matches:
            best_match = vocab_norm[matches[0]]
            best_score = difflib.SequenceMatcher(
                None, word_norm, matches[0]
            ).ratio() * 100

    # Seuil de confiance : en dessous, on considère que ce n'est
    # probablement pas une faute de frappe sur ce mot-clé métier
    if best_match and best_score >= 75:
        return SpellSuggestion(word, best_match, round(best_score, 1), "vocab_metier")

    # 3) Repli sur un correcteur orthographique français généraliste
    if HAS_SPELLCHECKER:
        try:
            spell = SpellChecker(language="fr")
            if word_l not in spell:
                suggestion = spell.correction(word_l)
                if suggestion and suggestion != word_l:
                    return SpellSuggestion(word, suggestion, 60.0, "dictionnaire_fr")
        except Exception:
            pass  # pas de dictionnaire fr dispo localement -> on ignore

    # 4) Rien de fiable -> on ne touche pas au mot (probablement une marque)
    return SpellSuggestion(word, word, 100.0, "inchange")


def understand_and_correct(raw_text: str) -> (List[SpellSuggestion], str):
    """
    Le "volet de compréhension" : à partir de la phrase brute de
    l'utilisateur, renvoie :
      - la liste des suggestions de correction mot par mot
      - la requête finale corrigée, prête à être envoyée à Jumia
    """
    keywords = clean_query(raw_text)
    suggestions = [correct_word(k) for k in keywords]
    corrected_query = " ".join(s.corrected for s in suggestions)
    return suggestions, corrected_query


def print_understanding_report(raw_text: str, suggestions: List[SpellSuggestion]):
    print("—" * 60)
    print(f"Phrase d'entrée         : {raw_text}")
    print("Analyse mot par mot :")
    for s in suggestions:
        if s.was_corrected:
            print(f"  • '{s.original}' -> compris comme '{s.corrected}' "
                  f"(confiance {s.confidence}%, source: {s.source})")
        else:
            print(f"  • '{s.original}' -> gardé tel quel")
    print("—" * 60)
