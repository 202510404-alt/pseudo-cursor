import os
import re
import ast

# 전역 인덱스 변수
PROJECT_INDEX = {}

def get_project_root():
    """
    현재 파일(project_scanner.py)이 assistant_head 폴더 안에 있으므로,
    무조건 상위 폴더(프로젝트 최상단)를 절대 경로로 구합니다.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build_index():
    """프로젝트 전체 파일 목록 인덱싱 (무시할 디렉토리 및 경로 문제 해결)"""
    global PROJECT_INDEX
    project_root = get_project_root()
    index = {}
    
    # 자기 자신(assistant_head) 내부의 파일이 대상이 되는 것도 방지할 수 있습니다
    ignore_dirs = {'.git', '.venv', 'target', '__pycache__', 'build', '.idea', 'node_modules', '.settings', '.metadata', 'assistant_head'}
    
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith((".py", ".java", ".env", ".json", ".csv", ".txt", ".xml", ".yml", ".gradle", ".properties")):
                # 최상단 기준 상대 경로로 변환
                rel_path = os.path.relpath(os.path.join(root, file), project_root)
                # 윈도우(\) 경로를 리눅스/AI 표준(/)으로 강제 통일
                rel_path = rel_path.replace('\\', '/')
                index[file.lower()] = rel_path
    
    PROJECT_INDEX = index
    return len(index)

def get_code_skeleton(file_path):
    """절대 경로를 사용하여 뼈대(구조) 추출 (오류 방지)"""
    try:
        project_root = get_project_root()
        abs_path = os.path.join(project_root, file_path)
        
        if not os.path.exists(abs_path): return "(File missing)"
            
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        skeleton = []
        if file_path.endswith(".java"):
            class_match = re.search(r'(class|interface|enum)\s+(\w+)', content)
            if class_match: skeleton.append(f"[{class_match.group(1).upper()}: {class_match.group(2)}]")

            method_blocks = re.finditer(r'(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{', content)
            for match in method_blocks:
                m_name = match.group(2)
                if m_name in ['if', 'for', 'while', 'switch', 'catch', 'return']: continue
                skeleton.append(f"  - Method: {m_name}")

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

def get_project_map():
    """1단계를 위한 지능형 스켈레톤 맵 생성"""
    if not PROJECT_INDEX: build_index()
    project_map = "--- INTELLIGENT PROJECT MAP (Skeletons) ---\n"
    for file_name, path in PROJECT_INDEX.items():
        if "test" in path.lower(): continue 
        project_map += f"\n[FILE: {path}]\n{get_code_skeleton(path)}\n"
    return project_map

# project_scanner.py 맨 아래에 추가
def scan_project(root_path=None):
    """stage3_healer와의 호환성을 위한 별명 함수"""
    return get_project_map()