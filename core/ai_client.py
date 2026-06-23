"""
AI 客户端 — DeepSeek API 封装（流式 + 缓存）
v5: 支持运行时 API Key 覆盖
"""
from openai import OpenAI
from config import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, DEEPSEEK_MAX_TOKENS, get_active_api_key
from core.cache import get_cache


def get_client() -> OpenAI:
    return OpenAI(api_key=get_active_api_key(), base_url=DEEPSEEK_BASE_URL)


def stream_ai(messages: list, max_tokens: int = None, feature: str = ""):
    """流式调用 DeepSeek API，自动缓存已完成响应用于后续命中"""
    if max_tokens is None:
        max_tokens = DEEPSEEK_MAX_TOKENS
    cache = get_cache()

    # 先查缓存（仅当缓存命中时直接 yield 完整内容）
    cached = cache.get(messages, feature)
    if cached is not None:
        yield cached
        return

    client = get_client()
    full_response = ""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            max_tokens=max_tokens,
            messages=messages,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token
                yield token

        # 流式结束后存入缓存
        if full_response and feature:
            cache.set(messages, feature, full_response)

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Invalid" in error_msg:
            yield "\n\n[错误] API Key 无效，请检查 .env 文件"
        elif "429" in error_msg or "Rate" in error_msg:
            yield "\n\n[提示] 请求太频繁，请稍后再试"
        elif "Connection" in error_msg or "Timeout" in error_msg:
            yield "\n\n[错误] 网络连接失败，请检查网络后重试"
        else:
            yield f"\n\n[错误] {error_msg}"


def chat_ai(messages: list, max_tokens: int = None, feature: str = "") -> str:
    """非流式调用，带缓存"""
    if max_tokens is None:
        max_tokens = DEEPSEEK_MAX_TOKENS
    cache = get_cache()
    cached = cache.get(messages, feature)
    if cached is not None:
        return cached

    client = get_client()
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            max_tokens=max_tokens,
            messages=messages,
        )
        result = response.choices[0].message.content
        if result and feature:
            cache.set(messages, feature, result)
        return result
    except Exception as e:
        return f"[错误] {e}"
