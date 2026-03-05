import os
import json
from datetime import datetime
from config import MEMORY_FILE, MAX_WORKING_CACHE_SIZE

# --- 1. 캐시 저장/불러오기 (기존과 동일) ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, UnicodeDecodeError):
            return []
    return []

def save_memory(cache_list):
    final_cache = cache_list[:MAX_WORKING_CACHE_SIZE]
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_cache, f, indent=4, ensure_ascii=False)

# --- 2. 캐시 업데이트 로직 (error_log 추가) ---
def add_working_cache(user_prompt, ai_response_text, related_files=None, error_log=None):
    cache = load_memory()
    
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_query": user_prompt,
        "ai_response": ai_response_text.strip(),
        "related_files": related_files if related_files else [],
        "terminal_error": error_log  # <-- 신규: 터미널 에러 기록 추가
    }
    
    cache.insert(0, new_entry)
    save_memory(cache)
    print(f"🧠 [Memory Sync] 휘발성 맥락 저장 완료")

def get_recent_context_for_prompt():
    cache = load_memory()
    if not cache:
        return ""

    MAX_CONVERSATION_WINDOW = 7
    recent_cache = cache[:MAX_CONVERSATION_WINDOW]
    
    context_list = []
    for m in reversed(recent_cache):
        # 대화 내용 구성 시 에러 로그가 있었다면 같이 언급해줌
        err_info = f"\n(당시 발생한 에러: {m['terminal_error'][:200]}...)" if m.get('terminal_error') else ""
        context_list.append(f"User: {m['user_query']}{err_info}\nAI: {m['ai_response']}")
    
    # 파일 힌트 로직 (기존과 동일)
    cumulative_files = set()
    for m in cache[:15]: 
        if m.get('related_files'):
            cumulative_files.update(m['related_files'])
    
    file_hint = ""
    if cumulative_files:
        file_hint = f"\n\n🚨 [핵심 기억: 누적 파이프라인 분석 경로]\n"
        file_hint += "- " + "\n- ".join(cumulative_files)
        file_hint += "\n\n위 파일들의 관계를 바탕으로 분석을 이어가세요."
    
    return "--- Recent Flow Context (Optimized) ---\n" + "\n---\n".join(context_list) + file_hint

def clear_memory():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        print("🧹 Memory cleared.")