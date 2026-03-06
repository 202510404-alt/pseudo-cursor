import re
import os
from . import project_scanner

def extract_error_context(error_log, terminal_callback, requested_files=None):
    """
    에러 로그 및 AI가 이전 루프에서 추가로 요청한 파일들을 수집합니다.
    """
    project_root = project_scanner.get_project_root()
    skeleton = project_scanner.scan_project(project_root)
    
    # 1. 정규표현식으로 에러 로그 내 파일 추출
    found_paths = set(re.findall(r'([a-zA-Z0-9_./\\]+\.(?:java|py|cpp|js|ts|h|hpp|cs|html|css|json))', error_log))
    
    # 2. 만약 AI가 이전 루프(NEXT_STEP_ADVICE)에서 특정 파일을 요청했다면 포함
    if requested_files:
        found_paths.update(requested_files)
    
    error_files_context = ""
    valid_files = []
    
    for path in found_paths:
        clean_path = path.replace('\\', '/')
        abs_path = os.path.join(project_root, clean_path)
        
        if os.path.exists(abs_path):
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    error_files_context += f"\n--- FULL SOURCE: {clean_path} ---\n{content}\n"
                    valid_files.append(clean_path)
            except Exception as e:
                if terminal_callback:
                    terminal_callback(f"⚠️ 파일 로딩 실패 ({clean_path}): {e}")
                    
    return skeleton, error_files_context, valid_files

def run_stage3(*args, **kwargs):
    """
    인자 개수 제한을 완전히 없앤 무제한 수용 버전입니다.
    api_manager가 무엇을 던지든 필요한 것만 골라 사용합니다.
    """
    # 1. 필요한 인자들을 안전하게 추출 (순서가 아닌 '이름' 혹은 '위치' 기반)
    # kwargs(이름 지정 인자)에서 먼저 찾고, 없으면 args(순서 인자)에서 인덱스로 찾습니다.
    
    error_log = kwargs.get('error_log') or (args[5] if len(args) > 5 else "")
    recent_context = kwargs.get('recent_context') or (args[4] if len(args) > 4 else "")
    prompt = kwargs.get('prompt') or (args[0] if len(args) > 0 else "")
    requested_files = kwargs.get('requested_files') # 이전 루프에서 넘어온 파일 요청
    
    # 터미널 콜백 함수 (에러 출력용)
    terminal_callback = kwargs.get('terminal_callback') or (args[3] if len(args) > 3 else None)

    # 2. 파일 소스코드 추출
    skeleton, error_files_context, valid_files = extract_error_context(
        error_log, 
        terminal_callback, 
        requested_files
    )
    
    # 3. 최종 치유 프롬프트 생성
    enhanced_context = f"{recent_context}\n\n[ORIGINAL USER REQUEST]: {prompt}"
    
    final_prompt = build_healing_prompt(
        skeleton, 
        enhanced_context, 
        error_log, 
        error_files_context
    )
    
    # 4. 결과 반환
    return final_prompt, valid_files
    
    # 3. api_manager가 사용할 수 있게 반환
    # (일반적으로 api_manager는 여기서 반환된 프롬프트를 AI 모델에게 던집니다.)
    return final_prompt, valid_files

def build_healing_prompt(skeleton, recent_context, error_log, error_files_context):
    """
    AI 리드 엔지니어 모드(Autonomous Engineer Mode V2) - 무한 루프 및 파일 요청 전략 강화
    """
    return f"""
[PROJECT ARCHITECTURE (SKELETON)]
{skeleton}

[RECENT DIALOGUE CONTEXT]
{recent_context}

[TERMINAL ERROR LOG]
{error_log}

[FULL SOURCE CODES OF RELEVANT FILES]
{error_files_context if error_files_context else "(로드된 파일 내용이 없습니다. SKELETON을 보고 필요한 파일을 NEXT_STEP_ADVICE에 요청하십시오.)"}


[CRITICAL COMMAND: AUTONOMOUS ENGINEER MODE V2]
당신은 시스템의 모든 권한을 가진 리드 소프트웨어 엔지니어입니다.
현재 '자가 치유 무한 루프' 상태이며, 성공할 때까지 반복합니다.

1. **전역적 분석 및 무제한 수정**:
   - 에러의 근본 원인이 의존성(Dependency) 문제라면, 관련된 모든 파일을 동시에 수정하십시오. 
   - 파일 수정 개수에는 제한이 없으며, TARGET_PATH를 여러 번 사용하여 한꺼번에 출력하십시오.

2. **지능적 파일 요청 (중요)**:
   - 현재 제공된 코드만으로 에러를 해결할 수 없다고 판단되면, 억지로 추측하여 수정하지 마십시오.
   - 대신, 다음 루프의 당신(AI)을 위해 **어떤 파일의 소스코드가 더 필요한지** SKELETON을 보고 정확한 경로를 찾아내십시오.
   - 그 경로를 `NEXT_STEP_ADVICE`에 **"NEED_FILE: 경로/파일명"** 형식으로 명시하십시오.

3. **환경 제어**: 
   - RUN_COMMAND 작성 시, 불필요한 Warning(JDK 등)이 터미널을 가리지 않도록 억제 명령(예: 2>$null 또는 2>/dev/null)을 반드시 포함하십시오.

코드 수정 출력 형식 (각 파일마다 반복):
TARGET_PATH: 경로/파일명.확장자
```(언어)
// 수정된 파일 전체 코드
실행 명령어 (빌드와 실행을 하나로 합친 단일 명령):
RUN_COMMAND: (명령어)

(필요 시에만 작성)
NEXT_STEP_ADVICE: "NEED_FILE: 요청할/파일/경로.java | 원인 분석: 특정 클래스의 메서드 정의 확인 필요"
"""