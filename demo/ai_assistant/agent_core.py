import os
import re
import ast

# 1. 전역 인덱스 변수
PROJECT_INDEX = {}

def build_index():
    """프로젝트 전체 파일 목록 인덱싱 (제한 없음)"""
    global PROJECT_INDEX
    current_dir = os.getcwd()
    index = {}
    ignore_dirs = {'.git', '.venv', 'target', '__pycache__', 'build', '.idea', 'node_modules'}
    
    for root, dirs, files in os.walk(current_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith((".py", ".java", ".env", ".json", ".csv", ".txt")):
                rel_path = os.path.relpath(os.path.join(root, file), current_dir)
                index[file.lower()] = rel_path
    
    PROJECT_INDEX = index
    return len(index)

def get_code_skeleton(file_path):
    """
    [Cursor Style] 파일의 유전자(구조, 의존성, 내부 호출)를 전수 추출합니다.
    갯수 제한 없이 '의미 있는' 모든 정보를 수집합니다.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            content = "".join(lines)
        
        skeleton = []
        
        # --- JAVA 분석 모드 ---
        if file_path.endswith(".java"):
            # 1. Imports (의존성 지도)
            imports = [l.strip() for l in lines if l.startswith("import ")]
            if imports: skeleton.append(f"[Dependency: Imports]\n" + "\n".join(imports))

            # 2. Fields (공유 변수 및 타입)
            fields = re.findall(r'(private|public|protected)\s+(static\s+)?(final\s+)?([\w<>\s\[\]]+)\s+(\w+)\s*(?:=.*?)?;', content)
            for f_mod, f_static, f_final, f_type, f_name in fields:
                skeleton.append(f"  - Field: {f_type.strip()} {f_name}")

            # 3. Methods & Internal Calls (핵심 로직 지문)
            # 메서드 본문 안에서 호출되는 주요 API/메서드를 추출하여 흐름 파악을 돕습니다.
            method_blocks = re.finditer(r'(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{', content)
            
            for match in method_blocks:
                m_name = match.group(2)
                if m_name in ['if', 'for', 'while', 'switch', 'catch']: continue
                
                skeleton.append(f"  - Method: {m_name}")
                
                # 메서드 내부를 들여다보고 호출되는 주요 심볼들 추출 (무제한)
                start = match.end()
                bracket_count = 1
                end = start
                while bracket_count > 0 and end < len(content):
                    if content[end] == '{': bracket_count += 1
                    elif content[end] == '}': bracket_count -= 1
                    end += 1
                
                body = content[start:end]
                # .methodCall() 또는 ClassName.method() 형태 추출
                calls = set(re.findall(r'\.?(\w+)\s*\(', body))
                # 예약어 제외한 순수 호출 목록
                meaningful_calls = [c for c in calls if c not in ['if', 'for', 'while', 'switch', 'println', 'printf']]
                if meaningful_calls:
                    skeleton.append(f"    (Internal Calls: {', '.join(meaningful_calls)})")

        # --- PYTHON 분석 모드 ---
        elif file_path.endswith(".py"):
            try:
                node = ast.parse(content)
                for item in node.body:
                    if isinstance(item, ast.ClassDef):
                        skeleton.append(f"Python Class: {item.name}")
                        for sub in item.body:
                            if isinstance(sub, ast.FunctionDef):
                                skeleton.append(f"  - Method: {sub.name}")
                    elif isinstance(item, ast.FunctionDef):
                        skeleton.append(f"Function: {item.name}")
            except SyntaxError:
                skeleton.append("(Python Syntax Error)")

        return "\n".join(skeleton)
    except Exception as e:
        return f"(Skeleton Error: {str(e)})"

def get_project_outline():
    if not PROJECT_INDEX: build_index()
    return "--- Full Project Structure ---\n" + "\n".join([f"- {p}" for p in PROJECT_INDEX.values()])

def analyze_project_and_get_response_fast(user_prompt, model, project_outline, current_memory):
    """
    [전수 조사 에이전트]
    AI가 스켈레톤을 보고 '데이터 단절'을 찾기 위해 필요한 모든 파일을 본문 요청하도록 유도
    """
    if not PROJECT_INDEX: build_index()

    # [Step 1] 무제한 스켈레톤 맵 생성
    project_map = "--- INTELLIGENT PROJECT MAP (SKELETON) ---\n"
    for file_name, path in PROJECT_INDEX.items():
        project_map += f"\n[FILE PATH: {path}]\n{get_code_skeleton(path)}\n"

    # [Step 2] AI에게 흐름 기반 파일 선택 요청 (제한 없음)
    selection_prompt = f"""
    당신은 코드 베이스의 '데이터 파이프라인'을 분석하는 아키텍트입니다. 
    제공된 [PROJECT MAP]은 각 파일의 구조와 내부 메서드 호출 관계(Internal Calls)를 담고 있습니다.

    사용자의 질문에 답하기 위해 본문 전체(Full Content)를 읽어야 하는 모든 파일을 선택하세요.
    - 데이터의 발원지(Seed), 변환(Transform), 소비(Sink/Console) 과정을 추적하세요.
    - 'Internal Calls' 정보를 보고 로직이 이어지는 파일은 무조건 포함하세요.
    - 파일 개수에 제한을 두지 마세요. 관련이 있다면 1개든 20개든 전부 선택해야 합니다.

    [PROJECT MAP]
    {project_map}

    [USER QUESTION]
    {user_prompt}

    응답 형식: 파일 경로만 한 줄에 하나씩 작성하세요. (다른 텍스트 금지)
    """
    
    try:
        selection_response = model.generate_content(selection_prompt)
        needed_files = [line.strip().replace('`', '').replace('*', '') 
                        for line in selection_response.text.strip().split('\n') if line.strip()]
        
        # 실제 경로와 대조하여 유효한 것만 필터링
        all_paths = list(PROJECT_INDEX.values())
        final_needed = []
        for nf in needed_files:
            for ap in all_paths:
                if ap.lower() in nf.lower() or nf.lower() in ap.lower():
                    final_needed.append(ap)
                    break
        needed_files = list(set(final_needed))
    except:
        needed_files = []

    # [Step 3] 선택된 파일 전수 로드
    detailed_context = ""
    for path in needed_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                detailed_context += f"\n--- FULL CONTENT OF: {path} ---\n{f.read()}\n"
        except: continue

    # [Step 4] 최종 심층 분석
    final_prompt = f"""
    당신은 '데이터 파이프라인' 전문 분석가입니다. 
    제공된 본문 코드를 바탕으로 데이터가 어디서 증발하거나 타입이 깨졌는지 분석하세요.

    지침:
    1. 데이터가 생성된 후 다음 메서드로 전달되지 않는 '호출 단절'을 찾으세요.
    2. 데이터 타입(long, double 등)이 변환 과정 없이 사용되어 발생하는 오류를 찾으세요.
    3. 결과가 콘솔에 찍히지 않는(System.out 누락) 지점을 정확히 짚으세요.
    4. 분석에 필요하지만 누락된 파일이 있다면 [NEED: 경로]를 남기세요.

    [REFERENCE CODE]
    {detailed_context if detailed_context else '지도를 기반으로 흐름 분석 수행'}

    [USER QUESTION]
    {user_prompt}
    """

    response = model.generate_content(final_prompt, stream=True)
    return response, needed_files