import time
import google.generativeai as genai
from config import GEMINI_API_KEY
from memory_manager import add_working_cache, get_recent_context_for_prompt
from agent_core import analyze_project_and_get_response_fast, get_project_outline

class AIHandler:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = None
        self.model_name = ""
        self.quota_blocked_until = 0
        self.last_error_log = None

    def get_best_model(self):
        """현재 쿼터 기록을 확인하여 최적의 모델을 선택 (2.0 차단 시 절대 엄금)"""
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        except:
            available_models = ["models/gemini-2.0-flash", "models/gemini-1.5-flash"]

        current_time = time.time()
        is_20_blocked = current_time < self.quota_blocked_until

        if is_20_blocked:
            # 2.0이 차단됐다면 1.5-flash 우선 검색
            flash_15 = next((m for m in available_models if 'gemini-1.5-flash' in m), None)
            if flash_15:
                return flash_15, "gemini-1.5-flash (Fallback Mode)"
            # 1.5마저 없으면 2.0이 아닌 다른 모델 강제 선택
            other = next((m for m in available_models if 'gemini-2.0-flash' not in m), available_models[0])
            return other, f"{other} (Emergency)"

        # 차단 상태가 아니라면 2.0 우선
        best_20 = next((m for m in available_models if 'gemini-2.0-flash' in m), None)
        if best_20:
            return best_20, "gemini-2.0-flash"

        return next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0]), "gemini-1.5-flash"

    def run_ai_logic(self, prompt, update_ui_callback, terminal_callback):
        try:
            recent_context = get_recent_context_for_prompt()
            current_outline = get_project_outline()
            full_prompt = f"{recent_context}\n\n[USER REQUEST]\n{prompt}"
            
            # [1차 시도]
            self.model_name, display_name = self.get_best_model()
            self.model = genai.GenerativeModel(self.model_name)
            terminal_callback(f"📡 [1st Attempt] Starting with: {self.model_name}")

            try:
                self._execute_and_report(full_prompt, current_outline, prompt, update_ui_callback)
            except Exception as e:
                if "429" in str(e):
                    # 429 발생 시 즉시 차단 및 모델 교체
                    self.quota_blocked_until = time.time() + 3600
                    old_model = self.model_name
                    self.model_name, display_name = self.get_best_model()
                    self.model = genai.GenerativeModel(self.model_name)
                    
                    terminal_callback(f"🔄 [QUOTA EXCEEDED] {old_model} -> {self.model_name} (Switched)")
                    update_ui_callback("SYSTEM", f"⚠️ 쿼터 초과! {display_name}로 전환하여 재시도합니다.", "system")
                    
                    # [2차 시도]
                    self._execute_and_report(full_prompt, current_outline, prompt, update_ui_callback)
                else:
                    raise e

        except Exception as e:
            error_msg = f"🚨 [FAILED] Model ({self.model_name}): {str(e)}"
            if "429" in str(e):
                error_msg = f"🚨 모든 모델 쿼터 소진 (최종 시도: {self.model_name}). 잠시 후 시도하세요."
            update_ui_callback("SYSTEM", error_msg, "error")
            terminal_callback(f"❌ Critical Error: {str(e)}")

    def _execute_and_report(self, full_prompt, current_outline, raw_prompt, update_ui_callback):
        response_stream, files_used = analyze_project_and_get_response_fast(
            full_prompt, self.model, current_outline, self.last_error_log
        )
        
        full_text = ""
        for chunk in response_stream:
            if chunk.text: full_text += chunk.text
        
        update_ui_callback("AI", full_text)
        add_working_cache(raw_prompt, full_text, files_used, error_log=self.last_error_log)