import os
import re
import ast

# 전역 인덱스 변수
PROJECT_INDEX = {}

def build_index():
    """프로젝트 전체 파일 목록 인덱싱"""
    global PROJECT_INDEX
    current_dir = os.getcwd()
    index = {}
    ignore_dirs = {'.git', '.venv', 'target', '__pycache__', 'build', '.idea', 'node_modules'}
    
    for root, dirs, files in os.walk(current_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith((".py", ".java", ".env", ".json", ".csv", ".txt", ".xml")):
                rel_path = os.path.relpath(os.path.join(root, file), current_dir)
                index[file.lower()] = rel_path
    
    PROJECT_INDEX = index
    return len(index)

def get_project_outline():
    """
    UI에서 프로젝트 구조를 보여주거나 AI에게 전체 지도를 전달할 때 사용
    """
    if not PROJECT_INDEX: build_index()
    outline = "--- Full Project Structure ---\n"
    for path in sorted(PROJECT_INDEX.values()):
        outline += f"- {path}\n"
    return outline

def get_code_skeleton(file_path):
    """파일의 구조(메서드, 필드, 호출 관계) 추출"""
    try:
        # 파일이 실제로 존재하는지 확인
        if not os.path.exists(file_path):
            return "(File not found)"
            
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            content = "".join(lines)
        
        skeleton = []
        if file_path.endswith(".java"):
            # Imports
            imports = [l.strip() for l in lines if l.startswith("import ")]
            if imports: skeleton.append(f"[Imports]\n" + "\n".join(imports[:5]) + "...")

            # Methods & Internal Calls
            method_blocks = re.finditer(r'(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{', content)
            for match in method_blocks:
                m_name = match.group(2)
                if m_name in ['if', 'for', 'while', 'switch', 'catch']: continue
                skeleton.append(f"  - Method: {m_name}")
                
                # 내부 호출 추출 로직 (중괄호 매칭)
                start = match.end()
                bracket_count = 1
                end = start
                while bracket_count > 0 and end < len(content):
                    if content[end] == '{': bracket_count += 1
                    elif content[end] == '}': bracket_count -= 1
                    end += 1
                body = content[start:end]
                calls = set(re.findall(r'\.?(\w+)\s*\(', body))
                meaningful_calls = [c for c in calls if c not in ['if', 'for', 'while', 'switch', 'println']]
                if meaningful_calls:
                    skeleton.append(f"    (Calls: {', '.join(list(meaningful_calls)[:10])})")

        elif file_path.endswith(".py"):
            try:
                node = ast.parse(content)
                for item in node.body:
                    if isinstance(item, (ast.ClassDef, ast.FunctionDef)):
                        skeleton.append(f"Python {type(item).__name__}: {item.name}")
            except: pass

        return "\n".join(skeleton)
    except Exception as e:
        return f"(Error: {str(e)})"

def analyze_project_and_get_response_fast(user_prompt, model, project_outline, error_log=None):
    """
    [짭커서 2호기 코어] 전수 조사 후 심층 분석
    """
    if not PROJECT_INDEX: build_index()

    # 1. 스켈레톤 맵 생성
    project_map = "--- INTELLIGENT PROJECT MAP ---\n"
    for file_name, path in PROJECT_INDEX.items():
        project_map += f"\n[FILE: {path}]\n{get_code_skeleton(path)}\n"

    # 2. 필요한 파일 선택 요청
    selection_prompt = f"""
    당신은 코드 베이스 아키텍트입니다. 
    사용자의 질문이나 에러를 해결하기 위해 '본문 전체'를 읽어야 할 파일들을 선택하세요.

    [현재 에러 로그]
    {error_log if error_log else "정상 상태"}

    [프로젝트 구조 및 스켈레톤]
    {project_map}

    [사용자 질문]
    {user_prompt}

    응답 형식: 파일 경로만 한 줄에 하나씩 작성하세요. (다른 설명 금지)
    """
    
    needed_files = []
    try:
        selection_response = model.generate_content(selection_prompt)
        # 경로 형태인 것만 필터링 (/, \ 포함 여부로 체크)
        raw_paths = selection_response.text.strip().split('\n')
        for rp in raw_paths:
            cleaned = rp.strip().replace('`', '').replace('*', '')
            if cleaned:
                needed_files.append(cleaned)
    except:
        needed_files = []

    # 3. 선택된 파일 본문 로드
    detailed_context = ""
    actual_loaded_files = []
    for path in needed_files:
        try:
            # 상대 경로/절대 경로 대응
            target_path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)
            if os.path.exists(target_path):
                with open(target_path, "r", encoding="utf-8") as f:
                    detailed_context += f"\n--- FULL CONTENT OF: {path} ---\n{f.read()}\n"
                    actual_loaded_files.append(path)
        except: continue

    # 4. 최종 분석 및 수정 제안
    final_prompt = f"""
    당신은 '짭커서' 자가 치유 에이전트입니다.
    제공된 본문 코드를 분석하여 사용자의 요청을 해결하고, 필요하다면 수정된 코드와 실행 명령어를 제안하세요.

    지침:
    1. 코드 수정 시 반드시 'TARGET_PATH: 경로'를 명시하고 전체 코드를 ```로 감싸세요.
    2. 수정 후 검증이 필요하면 'RUN_COMMAND: 명령어'를 포함하세요.
    3. 에러 로그가 있다면 해당 지점을 우선적으로 고치세요.

    [참조 코드 본문]
    {detailed_context if detailed_context else "지도를 기반으로 분석 수행"}

    [사용자 질문]
    {user_prompt}
    """

    response_stream = model.generate_content(final_prompt, stream=True)
    return response_stream, actual_loaded_files