import re
import unicodedata
from difflib import SequenceMatcher
from typing import List

def normalize_unicode(text):
    return unicodedata.normalize('NFKC', text)

def dediac_ar(text):
    return re.sub(r'[\u064B-\u065F\u0670]', '', text)

def normalize_alef_ar(text):
    return re.sub(r'[أإآ]', 'ا', text)

def normalize_alef_maksura_ar(text):
    return re.sub(r'ى', 'ي', text)

def normalize_teh_marbuta_ar(text):
    return re.sub(r'ة', 'ه', text)

emoji_mapping = {
    "😊": " ابتسامة  ", "😂": " ضحك  ", "😍": " حب  ",
    "😡": " غضب  ", "❤️": " قلب  ", "🎉": " احتفال  ",
    "👍": " موافق  ", "👎": " غير موافق  ", "😢": " حزن  ",
    "🤔": " تفكير  ", "🔥": " نار  ", "💯": " مئة  ",
    "😘": " قبلة  ", "😁": " فرح ", "🙏": " دعاء ",
    "✨": " بريق  ", "⭐": " نجمة ", "🎯": " هدف ",
    "💔": " قلب مكسور ", "😴": " نوم ", "🤣": " ضحك ","🌚":  " محتار  ",
    "🥰": " حب كبير ", "😭": " بكاء ", "😎": " رائع ",
    "🤩": " انبهار ", "🥺": " توسل ", "😤": " غضب قوي ","🤮": " اشمئزاز ","👏":" ممتاز  ","😮":" مفاجأة ","😋":"يمي ","🌝":" ابتسامة ","🙂":" مستغرب "
}

def reduce_repeated_words(text: str, max_consecutive: int = 2) -> str:
    """
    يقلل تكرار نفس الكلمة إذا جاءت متتالية أكثر من max_consecutive.
    مثال: "حلو حلو حلو حلو" -> "حلو حلو" (إذا max_consecutive=2)
    """
    if not text:
        return text

    tokens = text.split()
    out = []
    prev = None
    count = 0

    for tok in tokens:
        if tok == prev:
            count += 1
        else:
            prev = tok
            count = 1

        if count <= max_consecutive:
            out.append(tok)

    return " ".join(out)

def preprocess_arabic_text(text):
    if not isinstance(text, str): return ""
    for emoji, rep in emoji_mapping.items():
        text = text.replace(emoji, rep)
    text = reduce_repeated_words(text, max_consecutive=2)
    text = normalize_unicode(text)
    text = dediac_ar(text)
    text = normalize_alef_ar(text)
    text = normalize_alef_maksura_ar(text)
    text = normalize_teh_marbuta_ar(text)
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'(.)\1{2,}', r'\1', text) # حذف التكرار
    text = re.sub(r'\s+', ' ', text).strip()
    text = reduce_repeated_words(text, max_consecutive=2)
    return text

def normalize_basic(s: str) -> str:
    s = re.sub(r"http\S+|www\.\S+", " ", s)
    s = re.sub(r"#\w+", " ", s)
    s = re.sub(r"@\w+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(.)\1{2,}", r"\1", s)
    return s

def remove_non_arabic(text: str) -> str:
    return re.sub(
        r"[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF0-9\s.,!?؟،٪%\-–—()]+",
        "",
        text
    )

def similar(a, b, thr=0.90):
    return SequenceMatcher(None, a, b).ratio() >= thr

def dedup(comments: List[str]) -> List[str]:
    out = []
    for c in comments:
        c = normalize_basic(c)
        if not c:
            continue
        if not any(similar(c, x) for x in out):
            out.append(c)
    return out

def chunk(lst, n=30):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]