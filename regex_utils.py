import regex


def to_split_regex(phrase: str) -> regex.Pattern:
    def escape(s: str) -> str:
        return regex.escape(s)

    phrase = phrase.replace("[XXX]", "KrexAYplCU")  # Replace placeholder

    elision_patterns = {
        "de": r"(?:de|d'|du|en)",
        "que": r"(?:que|qu')",
        "la": r"(?:la|l')",
        "le": r"(?:le|l')",
        "à": r"(?:à|au)",
        ",": r",?",
    }

    # Tokenize words, whitespace, punctuation
    tokens = regex.findall(r"(\p{L}+|\s+|[^\p{L}\s]+)", phrase)

    processed_tokens = []
    for token in tokens:
        lower = token.lower()
        if lower in elision_patterns:
            processed_tokens.append(elision_patterns[lower])
        elif lower == " ":
            processed_tokens.append(token)
        else:
            processed_tokens.append(escape(token))

    pattern = "".join(processed_tokens)
    pattern = (
        pattern.replace(" KrexAYplCU", r"\s?.*?")
        .replace("’", r"['’]")
        # Bandaid fixes
        .replace("des faits", r"des\s?faits")
        .replace("autre domaine", r"autre\s?domaine")
        .replace("nous désormais", r"nous\s?désormais")
        .replace("actualité sportive", r"actualité\s?sportive")
    )

    return regex.compile(pattern, flags=regex.IGNORECASE | regex.UNICODE)
