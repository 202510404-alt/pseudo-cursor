# 같은 assistant_head 폴더 내부의 모듈들을 불러오기 위해 . (점)을 사용합니다
from . import project_scanner
from . import stage1_selector
from . import stage2_coder
from . import stage3_healer

def run_multi_stage_agent(user_prompt, recent_context, ai_handler, update_ui_callback, terminal_callback, error_log=None):
    """
    [에이전트 헤드(오케스트레이터)] 
    상황에 맞게 1단계, 2단계, 3단계를 호출하여 파이프라인을 실행합니다.
    """
    if not project_scanner.PROJECT_INDEX: 
        project_scanner.build_index()

    if error_log:
        return stage3_healer.run_stage3(
            user_prompt, error_log, recent_context, ai_handler, 
            update_ui_callback, terminal_callback
        )

    project_map = project_scanner.get_project_map()
    target_files = stage1_selector.run_stage1(
        user_prompt, project_map, ai_handler, 
        update_ui_callback, terminal_callback
    )

    final_text, actual_loaded_files = stage2_coder.run_stage2(
        user_prompt, target_files, recent_context, ai_handler, 
        update_ui_callback, terminal_callback
    )

    return final_text, actual_loaded_files