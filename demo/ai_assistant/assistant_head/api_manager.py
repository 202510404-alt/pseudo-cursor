import time
import google.generativeai as genai
from config import GEMINI_API_KEY
from memory_manager import add_working_cache, get_recent_context_for_prompt

# agent_head 함수를 같은 폴더에서 불러옵니다.
from .agent_head import run_multi_stage_agent

class APIManager:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.quota_blocked_until = {} # 모델별 차단 시간 관리
        self.last_error_log = None
        self.available_models = []
        self._refresh_live_model_list()

    def _refresh_live_model_list(self):
        """서버에서 현재 사용 가능한 최신 모델 리스트를 동기화합니다."""
        try:
            live_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            self.available_models = live_models
            print(f"📡 [System] 모델 동기화 완료: {len(live_models)}개 감지")
        except Exception as e:
            print(f"⚠️ [System] 리스트 갱신 실패: {e}")
            self.available_models = ["models/gemini-2.0-flash", "models/gemini-2.5-flash"]

    def _get_priority_model(self, tier_list):
        """우선순위 리스트 중 가용하고 차단되지 않은 최선의 모델을 반환합니다."""
        current_time = time.time()
        for model_id in tier_list:
            if model_id in self.available_models:
                if current_time > self.quota_blocked_until.get(model_id, 0):
                    return model_id
        return "models/gemini-2.0-flash" # 최후의 보루

    def get_model_for_tier(self, target_tier):
        """
        [기존 인터페이스 호환용] 
        기존 코드들이 이 함수를 호출하므로, 이름을 유지하면서 내부적으로 우선순위를 결정합니다.
        """
        priority_map = {
            "PRO": ["models/gemini-3.1-pro-preview", "models/gemini-2.5-pro", "models/gemini-2.0-flash"],
            "NORMAL": ["models/gemini-2.5-flash", "models/gemini-2.0-flash", "models/gemini-2.0-flash-lite"],
            "FLASH": ["models/gemini-2.5-flash-lite", "models/gemini-2.0-flash-lite", "models/gemini-2.0-flash"]
        }
        
        selected_id = self._get_priority_model(priority_map.get(target_tier, priority_map["FLASH"]))
        return selected_id, selected_id.split('/')[-1]

    def execute_with_fallback(self, prompt, target_tier, stage_name, update_ui_callback, terminal_callback, file_count=0):
        """
        [전략적 실행기] 
        429 발생 시 티어를 낮추며 재시도합니다. (PRO -> NORMAL -> FLASH)
        """
        # 파일 개수가 인자로 오면 티어를 강제로 조정하는 로직 (기존 설계 반영)
        actual_tier = target_tier
        if file_count > 0:
            if file_count <= 2: actual_tier = "FLASH"
            elif file_count <= 5: actual_tier = "NORMAL"
            else: actual_tier = "PRO"

        model_name, display_name = self.get_model_for_tier(actual_tier)
        terminal_callback(f"🚀 [{stage_name}] 가동: {display_name} (Tier: {actual_tier})")
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text, display_name
            
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg:
                self.quota_blocked_until[model_name] = time.time() + 600
                terminal_callback(f"🔄 [429 Error] {display_name} 차단됨. 즉시 하위 티어로 폴백...")
                
                # 티어 순차 강등 로직
                next_tier = {"PRO": "NORMAL", "NORMAL": "FLASH", "FLASH": "ERROR"}
                new_tier = next_tier.get(actual_tier, "ERROR")
                
                if new_tier == "ERROR":
                    raise Exception(f"모든 사용 가능한 모델의 쿼터가 만료되었습니다. ({err_msg})")
                
                return self.execute_with_fallback(prompt, new_tier, stage_name, update_ui_callback, terminal_callback, file_count=0)
            
            else:
                debug_info = f"Stage: {stage_name} | Model: {model_name} | Error: {err_msg}"
                terminal_callback(f"❌ {debug_info}")
                raise Exception(debug_info)

    def run_ai_logic(self, prompt, update_ui_callback, terminal_callback):
        """[지휘본부] 에이전트 헤드 가동"""
        try:
            recent_context = get_recent_context_for_prompt()
            
            # 자가 치유를 위한 에러 로그 주입
            error_directive = f"\n\n🚨 [이전 터미널 에러 분석]\n{self.last_error_log}" if self.last_error_log else ""

            self_healing_directive = f"""
[SYSTEM INSTRUCTION]
당신은 자율 에이전트입니다. 코드 수정 후 'TARGET_PATH'와 'RUN_COMMAND'를 반드시 포함하십시오.
{error_directive}
"""
            full_prompt = f"{prompt}\n\n{self_healing_directive}"

            # 🚀 다단계 에이전트 호출
            final_text, files_used = run_multi_stage_agent(
                user_prompt=full_prompt,
                recent_context=recent_context,
                ai_handler=self, 
                update_ui_callback=update_ui_callback,
                terminal_callback=terminal_callback,
                error_log=self.last_error_log
            )

            if final_text:
                update_ui_callback("AI", final_text)
                add_working_cache(prompt, final_text, files_used, error_log=self.last_error_log)
            
            self.last_error_log = None

        except Exception as e:
            terminal_callback(f"❌ [Crashed] {e}")
            update_ui_callback("SYSTEM", f"🚨 오류 발생: {e}", "error")