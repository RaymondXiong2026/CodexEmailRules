from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class KBItem:
    store_id: str
    primary: str
    secondary: str
    title: str
    content: str


class HybridRAG:
    def __init__(self, kb_items: list[KBItem]):
        self.kb_items = kb_items
        corpus = [k.content for k in kb_items] or [""]
        self.vectorizer = TfidfVectorizer()
        self.matrix = self.vectorizer.fit_transform(corpus)

    def search(self, store_id: str, primary: str, query: str, top_k: int = 3) -> dict[str, Any]:
        filtered = [k for k in self.kb_items if k.store_id == store_id and k.primary == primary]
        if not filtered:
            return {"hits": [], "score": 0.0}

        indices = [self.kb_items.index(k) for k in filtered]
        qv = self.vectorizer.transform([query])
        scores = cosine_similarity(qv, self.matrix[indices]).flatten()
        rank = np.argsort(scores)[::-1][:top_k]

        hits = []
        for i in rank:
            item = filtered[int(i)]
            hits.append(
                {
                    "title": item.title,
                    "content": item.content,
                    "score": float(scores[int(i)]),
                    "secondary": item.secondary,
                }
            )
        return {"hits": hits, "score": float(scores[rank[0]]) if len(rank) else 0.0}
