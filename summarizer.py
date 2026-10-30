import re
from collections import Counter

STOPWORDS = set("""a about above after again all also am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have having he her
here hers him his how i if in into is it its itself just me more most my no nor not now of off on once only or
other our out over own same she should so some such than that the their them then there these they this those
through to too under until up very was we were what when where which while who whom why will with would you your
said says""".split())


def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“])', text.strip())
    return [p.strip() for p in parts if len(p.split()) >= 6]


def summarize(text, max_sentences=3):
    sentences = split_sentences(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences) if sentences else text.strip()[:500]

    words = [w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOPWORDS and len(w) > 2]
    freq = Counter(words)
    top = max(freq.values()) if freq else 1

    scored = []
    for i, s in enumerate(sentences):
        tokens = [w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOPWORDS and len(w) > 2]
        if not tokens:
            continue
        score = sum(freq[t] / top for t in tokens) / len(tokens) ** 0.5
        if i < 3:
            score *= 1.2
        scored.append((score, i, s))

    best = sorted(scored, reverse=True)[:max_sentences]
    return " ".join(s for _, _, s in sorted(best, key=lambda x: x[1]))
