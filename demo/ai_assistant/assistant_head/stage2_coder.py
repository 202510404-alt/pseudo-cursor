import os
from . import project_scanner # 같은 폴더의 모듈을 불러올 땐 점(.)을 씁니다!

def run_stage2(user_prompt, target_files, recent_context, ai_handler, update_ui_callback, terminal_callback):
    file_count = len(target_files)
    if file_count == 0:
        terminal_callback("⚠️ [Stage 2] 대상 파일을 찾지 못했습니다.")
        return "수정할 파일을 찾지 못했습니다. 요청을 구체적으로 적어주세요.", []

    terminal_callback(f"📝 [Stage 2] {file_count}개 파일 정밀 분석 준비...")

    # 파일 개수에 따른 티어(Tier) 동적 분기
    if file_count <= 2:   target_tier = "FLASH"   
    elif file_count <= 4: target_tier = "NORMAL"  
    else:                 target_tier = "PRO"     

    detailed_context = ""
    actual_loaded_files = []
    project_root = project_scanner.get_project_root() # 절대 경로 루트 보호막
    
    for path in target_files:
        try:
            abs_path = os.path.join(project_root, path)
            if os.path.exists(abs_path):
                with open(abs_path, "r", encoding="utf-8") as f:
                    detailed_context += f"\n--- FULL SOURCE OF {path} ---\n{f.read()}\n"
                    actual_loaded_files.append(path)
            else:
                file_only = os.path.basename(path).lower()
                if file_only in project_scanner.PROJECT_INDEX:
                    real_path = project_scanner.PROJECT_INDEX[file_only]
                    real_abs_path = os.path.join(project_root, real_path)
                    with open(real_abs_path, "r", encoding="utf-8") as f:
                        detailed_context += f"\n--- FULL SOURCE OF {real_path} ---\n{f.read()}\n"
                        actual_loaded_files.append(real_path)
        except: continue

    stage2_prompt = f"""
{recent_context}

당신은 메인 코딩 에이전트입니다. 소스코드를 바탕으로 사용자의 요청을 수행하세요.

[필수 지침]
1. 코드 수정 시 반드시 다음 형식을 지키세요:
   TARGET_PATH: 실제/파일/경로.java
   ```(언어)
   // 수정된 전체 코드
   ```
2. 빌드/실행 테스트를 위해 아래 명령어를 포함하세요. (IDE argfile 금지)
   RUN_COMMAND: javac -encoding UTF-8 -d bin src/main/java/com/example/single/console/*.java src/main/java/com/example/single/core/*.java && java -cp bin com.example.single.console.SingleConsoleMain

[참조 소스코드 본문]
{detailed_context}

[사용자 요청]
{user_prompt}
"""
    
    update_ui_callback("SYSTEM", f"⚙️ {file_count}개의 파일을 {target_tier} 모델로 작성합니다...", "system")
    
    final_text, used_tier = ai_handler.execute_with_fallback(
        prompt=stage2_prompt,
        target_tier=target_tier,
        stage_name="Stage 2 (Coding)",
        update_ui_callback=update_ui_callback,
        terminal_callback=terminal_callback
    )

    return final_text, actual_loaded_files