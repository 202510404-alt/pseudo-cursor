import os
import re
import ast

# 전역 인덱스 변수
PROJECT_INDEX = {}

def build_index():
    """프로젝트 전체 파일 목록 인덱싱 (무시할 디렉토리 강화)"""
    global PROJECT_INDEX
    current_dir = os.getcwd()
    index = {}
    # 분석에 방해되는 폴더들 제외
    ignore_dirs = {'.git', '.venv', 'target', '__pycache__', 'build', '.idea', 'node_modules', '.settings', '.metadata'}
    
    for root, dirs, files in os.walk(current_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            # 주요 소스코드 및 설정 파일 확장자
            if file.endswith((".py", ".java", ".env", ".json", ".csv", ".txt", ".xml", ".yml", ".gradle", ".properties")):
                rel_path = os.path.relpath(os.path.join(root, file), current_dir)
                index[file.lower()] = rel_path
    
    PROJECT_INDEX = index
    return len(index)

def get_project_outline():
    """AI에게 전달할 프로젝트 전체 지도 생성"""
    if not PROJECT_INDEX: build_index()
    outline = "--- Full Project Structure ---\n"
    # 경로가 너무 많으면 상위 100개로 제한하여 토큰 절약
    sorted_paths = sorted(PROJECT_INDEX.values())
    for path in sorted_paths[:100]:
        outline += f"- {path}\n"
    if len(sorted_paths) > 100:
        outline += f"... and {len(sorted_paths)-100} more files."
    return outline

def get_code_skeleton(file_path):
    """파일의 뼈대(구조)를 추출하여 AI가 파일 내용을 짐작하게 함"""
    try:
        if not os.path.exists(file_path): return "(File missing)"
            
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            content = "".join(lines)
        
        skeleton = []
        # Java 구조 추출 (클래스명, 메서드명)
        if file_path.endswith(".java"):
            # 클래스/인터페이스 정의 확인
            class_match = re.search(r'(class|interface|enum)\s+(\w+)', content)
            if class_match: skeleton.append(f"[{class_match.group(1).upper()}: {class_match.group(2)}]")

            # 메서드 추출 (생성자 포함)
            method_blocks = re.finditer(r'(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{', content)
            for match in method_blocks:
                m_name = match.group(2)
                if m_name in ['if', 'for', 'while', 'switch', 'catch', 'return']: continue
                skeleton.append(f"  - Method: {m_name}")

        # Python 구조 추출
        elif file_path.endswith(".py"):
            try:
                tree = ast.parse(content)
                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        skeleton.append(f"[CLASS: {node.name}]")
                    elif isinstance(node, ast.FunctionDef):
                        skeleton.append(f"  - Func: {node.name}")
            except: pass

        return "\n".join(skeleton) if skeleton else "(Simple File or No Structure Found)"
    except Exception as e:
        return f"(Error reading skeleton: {str(e)})"

def analyze_project_and_get_response_fast(user_prompt, model, project_outline, error_log=None):
    """
    [짭커서 2호기 핵심 엔진] 
    1단계: 스켈레톤 맵으로 분석 대상 파일 선정
    2단계: 선정된 파일 정밀 분석 및 코드 생성
    """
    if not PROJECT_INDEX: build_index()

    # 1. 스켈레톤 맵 생성 (AI가 '어디를 읽어야 할지' 결정하는 지도)
    project_map = "--- INTELLIGENT PROJECT MAP (Skeletons) ---\n"
    # 현재 폴더(보통 demo나 single) 위주로 스켈레톤 우선 추출
    for file_name, path in PROJECT_INDEX.items():
        if "test" in path.lower(): continue # 테스트 코드는 우선 제외
        project_map += f"\n[FILE: {path}]\n{get_code_skeleton(path)}\n"

    # 2. 분석 대상 파일 선택 요청 (1차 API 호출)
    selection_prompt = f"""
    당신은 숙련된 소프트웨어 아키텍트입니다. 
    다음 에러를 해결하거나 요청을 수행하기 위해 '전체 코드'를 반드시 읽어야 하는 파일을 최대 5개만 고르세요.

    [현재 터미널 에러]
    {error_log if error_log else "정상 작동 중"}

    [프로젝트 스켈레톤 지도]
    {project_map}

    [사용자 요청]
    {user_prompt}

    형식: 파일 경로만 한 줄에 하나씩 응답하세요. 예: src/main/java/App.java
    """
    
    needed_files = []
    try:
        # 1.5-flash 모델일 경우를 대비해 더 명확한 응답 유도
        selection_response = model.generate_content(selection_prompt)
        raw_paths = selection_response.text.strip().split('\n')
        for rp in raw_paths:
            # 경로 클리닝 (따옴표, 불필요한 공백 제거)
            cleaned = re.sub(r'[*`\s]', '', rp)
            if cleaned and ('.' in cleaned): # 확장자가 포함된 경우만
                needed_files.append(cleaned)
    except:
        needed_files = []

    # 3. 선택된 파일 본문 로드
    detailed_context = ""
    actual_loaded_files = []
    for path in needed_files:
        try:
            # 경로 정규화 (AI가 준 경로가 틀릴 수 있으므로 재검사)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    detailed_context += f"\n--- FULL SOURCE OF {path} ---\n{f.read()}\n"
                    actual_loaded_files.append(path)
            else:
                # 인덱스에서 실제 경로 다시 찾기 시도
                file_only = os.path.basename(path).lower()
                if file_only in PROJECT_INDEX:
                    real_path = PROJECT_INDEX[file_only]
                    with open(real_path, "r", encoding="utf-8") as f:
                        detailed_context += f"\n--- FULL SOURCE OF {real_path} ---\n{f.read()}\n"
                        actual_loaded_files.append(real_path)
        except: continue

    # 4. 최종 솔루션 생성 (2차 API 호출)
    final_prompt = f"""
    당신은 '짭커서' 자가 치유 에이전트입니다. 제공된 소스코드를 바탕으로 해결책을 제시하세요.

    [필수 지침]
    1. 코드 수정이 필요하면 반드시 다음 형식을 지키세요:
       TARGET_PATH: 실제/파일/경로
       ```(언어)
       // 수정된 전체 코드
       ```
    2. 에러 로그({error_log})가 있다면, 발생 원인을 먼저 설명하고 고치세요.
    3. 빌드나 실행이 필요하면 'RUN_COMMAND: 명령어'를 한 줄 적으세요. (예: RUN_COMMAND: mvn compile)
    4. 변수 선언(aVal 등)이나 세미콜론 누락 같은 기초적인 실수를 절대 하지 마세요.

    [참조 소스코드 본문]
    {detailed_context if detailed_context else "프로젝트 구조를 바탕으로 추론하세요."}

    [사용자 요청]
    {user_prompt}
    """

    response_stream = model.generate_content(final_prompt, stream=True)
    return response_stream, actual_loaded_files