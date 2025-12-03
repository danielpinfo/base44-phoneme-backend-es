# ============================
#  UNIVERSAL BASE44 MAPPER
#  FINAL VERSION
# ============================

IPA_TO_BASE44 = {
    # ----- Stops -----
    "p": "P",
    "b": "B",
    "t": "T",
    "d": "D",
    "k": "K",
    "g": "G",

    # ----- Affricates -----
    "tʃ": "CH",
    "dʒ": "JH",

    # ----- Fricatives -----
    "f": "F",
    "v": "V",
    "θ": "TH",
    "ð": "DH",
    "s": "S",
    "z": "Z",
    "ʃ": "SH",
    "ʒ": "ZH",
    "x": "J",       # Spanish "j" = velar fricative
    "h": "H",

    # ----- Nasals -----
    "m": "M",
    "n": "N",
    "ɲ": "NY",
    "ŋ": "NG",

    # ----- Liquids / Approximants -----
    "l": "L",
    "ʎ": "LL",
    "r": "R",
    "ɾ": "RR",
    "j": "Y",
    "w": "W",

    # ----- Vowels -----
    "a": "A",
    "e": "E",
    "i": "I",
    "o": "O",
    "u": "U",

    "æ": "AE",
    "ɑ": "AA",
    "ʌ": "UH",
    "ə": "AX",
    "ɛ": "EH",
    "ɪ": "IH",
    "ɔ": "AW",
    "ʊ": "UU",

    # ----- Diphthongs -----
    "ai": "AI",
    "au": "AU",
    "ei": "EI",
    "oi": "OI",
    "ou": "OU",
    "ia": "IA",
    "ua": "UA",
    "ie": "IE",
    "ue": "UE",

    # ----- Stress marks (ignored) -----
    "ˈ": "",
    "ˌ": "",

    # ----- Fallback -----
    "?": "?"
}


def ipa_to_base44_units(ipa_units: list[str]) -> list[str]:
    out = []
    for unit in ipa_units:
        clean = unit.replace("ˈ", "").replace(".", "")
        out.append(IPA_TO_BASE44.get(clean, "?"))
    return out
