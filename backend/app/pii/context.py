def context_score(text, match_start, context_keywords):
    window = 30  # chars before/after
    context = text[max(0, match_start-window):match_start+window]
    return any(kw.lower() in context.lower() for kw in context_keywords)
