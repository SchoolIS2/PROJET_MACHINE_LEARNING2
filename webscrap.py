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
