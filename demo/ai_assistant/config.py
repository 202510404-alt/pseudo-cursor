import os
from dotenv import load_dotenv

# ==========================================================
# 🚨 [필독] 보안 및 실행 설정 (VERY IMPORTANT)
# ==========================================================
# 1. 프로젝트 루트 폴더에 '.env' 파일을 반드시 생성하세요.
# 2. .env 파일 안에 아래 내용을 한 줄 적어 넣으세요:
#    GEMINI_API_KEY=your_actual_api_key_here
#
# ※ 주의: 이 config.py 파일에 직접 키를 쓰지 마세요! 
#    GitHub에 올리는 순간 API 키가 노출되어 계정이 정지됩니다.
# ==========================================================

# .env 파일의 환경 변수를 시스템으로 로드합니다.
load_dotenv()

# [API 설정]
# 환경 변수에서 키를 가져옵니다. .env 파일이 없거나 설정이 틀리면 None이 반환됩니다.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ 경고: GEMINI_API_KEY를 찾을 수 없습니다. .env 파일을 확인하세요!")

# [파일 경로]
MEMORY_FILE = "agent_memory.json"

# --- 핵심 메모리/캐시 설정 (실전형) ---
# 전체 저장소 개수 제한 (성능 최적화용)
MAX_MEMORY_ITEMS = 500  

# ★ 단기 캐시 설정 ★
# 대화 맥락 유지를 위한 최근 대화 보관 개수
MAX_WORKING_CACHE_SIZE = 7 

# --- UI 설정 (Tkinter/Pygame용) ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# 색상 정의 (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (220, 230, 255)
GREEN = (50, 200, 50)

# UI 로그 표시 제한 (너무 많아지면 느려지므로 제한)
CHAT_HISTORY_MAX_LINES = 50