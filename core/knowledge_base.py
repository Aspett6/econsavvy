"""
知识库检索模块 — 基于 Jieba 分词 + TF-IDF 语义检索
相比 v2 的 1-4 字分块匹配，大幅提升检索精度
"""
import os
import re
import math
from collections import defaultdict

try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


class KnowledgeBase:
    """Jieba 分词 + TF-IDF 知识库检索"""

    def __init__(self, kb_dir="知识库"):
        self.kb_dir = kb_dir
        self.chunks = []          # [(source_file, page_num, text), ...]
        self._tfidf_ready = False
        self._idf = {}            # word → idf
        self._chunk_tf = []       # [{word: tf}, ...] per chunk
        self._vocab = set()

    # ---- 加载 ----
    def load(self) -> int:
        """加载知识库中所有 txt 文件"""
        self.chunks = []
        if not os.path.isdir(self.kb_dir):
            return 0

        for root, dirs, files in os.walk(self.kb_dir):
            for fname in files:
                if not fname.endswith(".txt"):
                    continue
                fpath = os.path.join(root, fname)
                text = self._read_file(fpath)
                for page_num, page_text in self._split_pages(text):
                    clean = page_text.strip()
                    if len(clean) > 20:
                        self.chunks.append((fname.replace(".txt", ""), page_num, clean))

        self._build_index()
        return len(self.chunks)

    def _read_file(self, path: str) -> str:
        for enc in ["utf-8", "gbk", "gb2312", "utf-16"]:
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        return ""

    def _split_pages(self, text: str) -> list:
        """按 '--- 第 X 页 ---' 分割页面"""
        pages = re.split(r"--- 第\s*\d+\s*页\s*---", text)
        result = []
        for i, page in enumerate(pages):
            page = page.strip()
            if page and len(page) > 10:
                result.append((i + 1, page))
        return result

    # ---- 分词 ----
    def _tokenize(self, text: str) -> list:
        """中文分词（Jieba 优先，回退到 n-gram）"""
        if JIEBA_AVAILABLE:
            # Jieba 精确模式分词，过滤停用词和短词
            words = jieba.lcut(text)
            return [w.strip() for w in words if len(w.strip()) >= 2 and not w.strip().isspace()]
        else:
            # 回退：1-4 字 n-gram + 英文单词
            tokens = []
            for match in re.findall(r"[一-龥]{1,4}|[a-zA-Z]+", text.lower()):
                tokens.append(match)
            return tokens

    # ---- TF-IDF 索引 ----
    def _build_index(self):
        """构建 TF-IDF 索引"""
        if not self.chunks:
            return

        # 文档频率
        df = defaultdict(int)
        all_docs_tokens = []

        for _, _, text in self.chunks:
            tokens = self._tokenize(text)
            all_docs_tokens.append(tokens)
            for word in set(tokens):
                df[word] += 1

        N = len(self.chunks)
        self._idf = {word: math.log((N + 1) / (freq + 1)) + 1 for word, freq in df.items()}
        self._vocab = set(self._idf.keys())

        # 每篇文档的 TF
        self._chunk_tf = []
        for tokens in all_docs_tokens:
            tf = defaultdict(float)
            word_count = len(tokens) or 1
            for w in tokens:
                tf[w] += 1.0 / word_count
            self._chunk_tf.append(tf)

        self._tfidf_ready = True

    # ---- 检索 ----
    def search(self, query: str, top_k: int = 5) -> list:
        """TF-IDF 语义检索，返回最相关的知识段落"""
        if not self.chunks:
            return []

        if not self._tfidf_ready:
            # 回退到简单关键词匹配
            return self._keyword_search(query, top_k)

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # 查询 TF
        query_tf = defaultdict(float)
        for w in query_tokens:
            query_tf[w] += 1.0 / len(query_tokens)

        # 计算余弦相似度
        scores = []
        for idx, chunk_tf in enumerate(self._chunk_tf):
            score = self._cosine_similarity(query_tf, chunk_tf)
            if score > 0.001:
                source, page, text = self.chunks[idx]
                scores.append((score, source, page, text))

        scores.sort(key=lambda x: -x[0])

        results = []
        for score, source, page, text in scores[:top_k]:
            results.append({
                "source": source,
                "page": page,
                "text": text[:800],
                "score": round(score, 4),
            })
        return results

    def _cosine_similarity(self, tf_a: dict, tf_b: dict) -> float:
        """余弦相似度"""
        dot_product = 0.0
        norm_a = 0.0
        norm_b = 0.0

        for word, w_a in tf_a.items():
            idf = self._idf.get(word, 1.0)
            weighted_a = w_a * idf
            norm_a += weighted_a ** 2
            w_b = tf_b.get(word, 0)
            dot_product += weighted_a * w_b * idf

        if norm_a < 1e-10:
            return 0.0

        for w_b in tf_b.values():
            norm_b += (w_b * self._idf.get(list(tf_b.keys())[0], 1.0)) ** 2  # approximate

        # Recompute norm_b correctly
        norm_b = 0.0
        for word, w_b in tf_b.items():
            idf = self._idf.get(word, 1.0)
            norm_b += (w_b * idf) ** 2

        if norm_b < 1e-10:
            return 0.0

        return dot_product / (math.sqrt(norm_a) * math.sqrt(norm_b))

    def _keyword_search(self, query: str, top_k: int = 5) -> list:
        """回退方案：简单关键词匹配"""
        keywords = set(self._tokenize(query))
        scored = []
        for source, page, text in self.chunks:
            index_words = set(self._tokenize(text))
            score = len(keywords & index_words)
            if score > 0:
                scored.append((score, source, page, text))
        scored.sort(key=lambda x: -x[0])
        results = []
        for score, source, page, text in scored[:top_k]:
            results.append({
                "source": source,
                "page": page,
                "text": text[:800],
                "score": float(score),
            })
        return results

    # ---- 上下文 ----
    def get_context_for_query(self, query: str, top_k: int = 5) -> tuple:
        """返回注入 AI 对话的上下文文本和来源列表"""
        results = self.search(query, top_k)
        if not results:
            return "", ""

        context_parts = []
        sources = set()
        for r in results:
            context_parts.append(
                f"【来源：《{r['source']}》第{r['page']}页 · 相关度：{r['score']}】\n{r['text']}"
            )
            sources.add(r["source"])

        context = "\n\n---\n\n".join(context_parts)
        source_list = "、".join(sorted(sources)[:5])
        return context, source_list

    def get_catalog(self) -> str:
        """返回知识库内容摘要"""
        if not self.chunks:
            return "（知识库为空）"

        sources = sorted(set(c[0] for c in self.chunks))
        lines = [f"可用知识库（共 {len(self.chunks)} 个段落）："]
        for s in sources:
            count = sum(1 for c in self.chunks if c[0] == s)
            lines.append(f"  - {s}（{count} 页）")
        return "\n".join(lines)


# 全局单例
_kb_instance = None


def get_kb(kb_dir="知识库") -> KnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase(kb_dir)
        n = _kb_instance.load()
        if n > 0:
            print(f"[知识库] Jieba={JIEBA_AVAILABLE} · 已加载 {n} 个段落")
    return _kb_instance
