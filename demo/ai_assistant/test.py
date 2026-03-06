import google.generativeai as genai
import sys
import os

# 기존 프로젝트의 config.py에서 API 키를 가져옵니다.
try:
    from config import GEMINI_API_KEY
except ImportError:
    print("❌ config.py 파일이나 GEMINI_API_KEY를 찾을 수 없습니다.")
    sys.exit(1)

def list_all_gemini_models():
    print("🔍 구글 Gemini API 서버에 연결하여 사용 가능한 전체 모델 목록을 가져옵니다...\n")
    genai.configure(api_key=GEMINI_API_KEY)
    
    try:
        models = genai.list_models()
        
        print("=" * 65)
        print(f"{'모델 이름 (Model Name)':<40} | {'버전/설명'}")
        print("=" * 65)
        
        count = 0
        for m in models:
            # 텍스트/코드 생성(generateContent)이 가능한 모델만 필터링하여 출력
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name:<38} | {m.version if hasattr(m, 'version') else 'N/A'}")
                count += 1
                
        print("=" * 65)
        print(f"총 {count}개의 텍스트 생성 가능 모델이 검색되었습니다.")
        print("=" * 65)
        
        # 우리가 찾는 핵심 모델들이 리스트에 있는지 확인
        print("\n[🎯 주요 모델 존재 여부 확인]")
        model_names = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        flash_15 = any('gemini-1.5-flash' in name for name in model_names)
        flash_20 = any('gemini-2.0-flash' in name for name in model_names)
        
        print(f"👉 gemini-1.5-flash 계열 존재함? : {'🟢 YES' if flash_15 else '🔴 NO'}")
        print(f"👉 gemini-2.0-flash 계열 존재함? : {'🟢 YES' if flash_20 else '🔴 NO'}")
        
    except Exception as e:
        print(f"\n❌ API 호출 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    list_all_gemini_models()