import re
import json

def run_stage1(user_prompt, project_map, ai_handler, update_ui_callback, terminal_callback):
    terminal_callback("🔍 [Stage 1] 프로젝트 스켈레톤 맵 분석 중...")

    stage1_prompt = f"""
당신은 숙련된 소프트웨어 아키텍트입니다. 
다음 스켈레톤 지도를 분석하여 사용자의 요청을 수행하기 위해 '전체 코드'를 읽고 수정해야 할 파일을 선택하세요.

[프로젝트 스켈레톤 지도]
{project_map}

[사용자 요청]
{user_prompt}

[TASK]
수정해야 할 파일의 상대 경로를 JSON 배열 형태로만 반환하십시오. 최대 5개까지만 선택하세요.
예시: ["src/main/java/com/example/App.java"]
"""
    # 1단계는 가벼운 판단이므로 FLASH(Lite) 사용
    stage1_response, _ = ai_handler.execute_with_fallback(
        prompt=stage1_prompt,
        target_tier="FLASH",
        stage_name="Stage 1 (File Selection)",
        update_ui_callback=update_ui_callback,
        terminal_callback=terminal_callback
    )

    if not stage1_response: return []

    target_files = []
    try:
        json_match = re.search(r'\[.*\]', stage1_response, re.DOTALL)
        if json_match:
            target_files = json.loads(json_match.group(0))
        else:
            raw_paths = stage1_response.strip().split('\n')
            for rp in raw_paths:
                cleaned = re.sub(r'[*`\s]', '', rp)
                if cleaned and ('.' in cleaned): target_files.append(cleaned)
    except Exception:
        target_files = []

    return target_files