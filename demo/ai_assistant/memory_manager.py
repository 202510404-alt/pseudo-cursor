import os
import json
from datetime import datetime
from config import MEMORY_FILE, MAX_WORKING_CACHE_SIZE

# --- 1. 캐시 저장/불러오기 ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 데이터가 리스트 형태인지 검증
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, UnicodeDecodeError):
            return []
    return []

def save_memory(cache_list):
    # 설정된 최대 캐시 사이즈만큼만 유지 (메모리 비대화 방지)
    final_cache = cache_list[:MAX_WORKING_CACHE_SIZE]
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_cache, f, indent=4, ensure_ascii=False)

# --- 2. 캐시 업데이트 로직 ---
def add_working_cache(user_prompt, ai_response_text, related_files=None, error_log=None):
    """
    사용자 질문, AI 답변, 관련 파일, 그리고 결정적인 '터미널 에러'를 함께 저장합니다.
    """
    cache = load_memory()
    
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_query": user_prompt,
        "ai_response": ai_response_text.strip(),
        "related_files": related_files if related_files else [],
        "terminal_error": error_log  # <-- 터미널 빌드 에러 기록
    }
    
    # 최신 기록을 맨 앞으로
    cache.insert(0, new_entry)
    save_memory(cache)
    print(f"🧠 [Memory Sync] 작업 문맥 저장 완료 (Error Log 포함)")

def get_recent_context_for_prompt():
    """
    AI에게 전달할 이전 대화 맥락을 생성합니다.
    에러가 발생했던 이력을 강조하여 모델이 바껴도 흐름을 놓치지 않게 합니다.
    """
    cache = load_memory()
    if not cache:
        return "[System] 이전 작업 기록이 없습니다. 새로운 분석을 시작합니다."

    # 최근 5~7개의 대화 창 유지
    MAX_CONVERSATION_WINDOW = 7
    recent_cache = cache[:MAX_CONVERSATION_WINDOW]
    
    context_list = []
    # 오래된 기록부터 순서대로 나열
    for m in reversed(recent_cache):
        # 에러 로그가 있다면 AI에게 이 지점을 해결해야 함을 강력히 시사
        error_context = ""
        if m.get('terminal_error'):
            # 에러 로그가 너무 길면 핵심인 뒷부분 위주로 전달 (250자)
            raw_err = str(m['terminal_error'])
            err_summary = raw_err[-250:] if len(raw_err) > 250 else raw_err
            error_context = f"\n[CRITICAL ERROR DURING THIS STEP]:\n{err_summary}"
        
        context_list.append(f"User Request: {m['user_query']}{error_context}\nAI Action: {m['ai_response'][:300]}...")
    
    # 파일 힌트 로직 (AI가 어떤 파일들을 주시해왔는지 알려줌)
    cumulative_files = set()
    for m in cache[:10]: # 최근 10개 작업물에서 파일 경로 추출
        if m.get('related_files'):
            cumulative_files.update(m['related_files'])
    
    file_hint = ""
    if cumulative_files:
        file_hint = f"\n\n🚨 [Project Insight: 지금까지 분석된 주요 파일들]\n"
        file_hint += "- " + "\n- ".join(list(cumulative_files))
        file_hint += "\n\n위 파일들 간의 관계를 유지하며 해결책을 제시하세요."
    
    header = "--- PREVIOUS EXECUTION FLOW & CONTEXT ---\n"
    return header + "\n---\n".join(context_list) + file_hint

def clear_memory():
    """작업 초기화가 필요할 때 사용"""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        print("🧹 Memory cleared.")