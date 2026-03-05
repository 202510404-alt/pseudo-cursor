import os
import json
import re
from datetime import datetime
from config import MEMORY_FILE, MAX_WORKING_CACHE_SIZE

# --- 1. 캐시 저장/불러오기 ---
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
    # 시스템 과부하를 방지하기 위해 MAX_WORKING_CACHE_SIZE(권장 15~20) 내에서 조절합니다.
    final_cache = cache_list[:MAX_WORKING_CACHE_SIZE]
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_cache, f, indent=4, ensure_ascii=False)

# --- 2. 캐시 업데이트 로직 ---
def add_working_cache(user_prompt, ai_response_text, related_files=None):
    cache = load_memory()
    
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_query": user_prompt,
        "ai_response": ai_response_text.strip(),
        "related_files": related_files if related_files else []
    }
    
    # 최신 데이터를 맨 앞으로
    cache.insert(0, new_entry)
    save_memory(cache)
    print(f"🧠 [Memory Sync] 휘발성 맥락 저장 완료 (현재 세션 파일: {len(related_files) if related_files else 0}개)")

def get_recent_context_for_prompt():
    """
    [Sliding Window 전략] 
    전체 대화 중 핵심 맥락 유지를 위해 최근 7개 대화로 휘발성 제한을 둡니다.
    """
    cache = load_memory()
    if not cache:
        return ""

    # 1. 대화 흐름의 휘발성: 최근 7개 대화만 유지 (토큰 효율 및 집중도 향상)
    # 제가 판단하기에 7개 정도가 '초기 원인 분석'과 '현재 수정 단계'를 동시에 잡는 최적값입니다.
    MAX_CONVERSATION_WINDOW = 7
    recent_cache = cache[:MAX_CONVERSATION_WINDOW]
    
    context_list = []
    for m in reversed(recent_cache): 
        context_list.append(f"User: {m['user_query']}\nAI: {m['ai_response']}")
    
    # 2. 파일 힌트의 보존성: 파일 목록은 조금 더 긴 호흡(최근 15개 대화 분량)으로 추적합니다.
    # 대화 내용은 잊어도, 어떤 파일들을 조사해왔는지는 더 길게 기억해야 파이프라인 단절을 안 놓칩니다.
    cumulative_files = set()
    for m in cache[:15]: 
        if m.get('related_files'):
            cumulative_files.update(m['related_files'])
    
    file_hint = ""
    if cumulative_files:
        file_hint = f"\n\n🚨 [핵심 기억: 누적 파이프라인 분석 경로]\n"
        file_hint += "당신은 프로젝트를 탐색하며 다음 파일들의 연관성을 이미 파악했습니다:\n- " 
        file_hint += "\n- ".join(cumulative_files)
        file_hint += "\n\n위 파일들 간의 데이터 타입 불일치와 호출 누락 여부를 현재 질문과 연결하여 분석하세요."
    
    return "--- Recent Flow Context (Optimized) ---\n" + "\n---\n".join(context_list) + file_hint

def clear_memory():
    """맥락이 꼬였을 때를 위한 수동 초기화"""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        print("🧹 Memory cleared.")