import os
import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading 
from datetime import datetime
import re
import subprocess 

# 설정 및 모듈 임포트
from config import *
from memory_manager import add_working_cache, get_recent_context_for_prompt
from agent_core import build_index, analyze_project_and_get_response_fast, get_project_outline

class PseudoCursorInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Pseudo-Cursor v2.0 (Terminal & Self-Healing)")
        
        self.model = None
        self.is_processing = False 
        self.code_blocks_map = {} 
        self.last_error_log = None 

        self.setup_ui()
        self.initial_setup()

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=3) # 채팅창 비중
        self.root.grid_rowconfigure(1, weight=1) # 터미널 비중

        # 1. 채팅창
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=110, height=20, 
                                                      font=("Consolas", 11), bg="#1e1e1e", fg="#d4d4d4")
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        self.chat_display.config(state=tk.DISABLED)

        # 2. 터미널 창
        self.terminal_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=110, height=10, 
                                                          font=("Consolas", 10), bg="#000000", fg="#00FF00")
        self.terminal_display.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="nsew")
        self.terminal_display.insert(tk.END, "--- PSEUDO-TERMINAL READY ---\n")
        self.terminal_display.config(state=tk.DISABLED)

        # 태그 설정
        self.chat_display.tag_configure("system", foreground="#6A9955", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("user", foreground="#569CD6", font=("Consolas", 11, "bold"))
        self.chat_display.tag_configure("ai", foreground="#D4D4D4", font=("Consolas", 11))
        self.chat_display.tag_configure("error", foreground="#F44747", font=("Consolas", 11, "bold"))

        # 입력 영역
        input_frame = tk.Frame(self.root, bg="#2d2d2d")
        input_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = tk.Entry(input_frame, font=("Malgun Gothic", 12), bg="#3c3c3c", fg="white", insertbackground="white")
        self.input_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_entry.bind("<Return>", lambda event: self.process_input()) 

        self.send_button = tk.Button(input_frame, text="⚡ 분석 및 실행", command=self.process_input, 
                                     width=15, bg="#007acc", fg="white", font=("Malgun Gothic", 10, "bold"))
        self.send_button.grid(row=0, column=1)

    def write_terminal(self, text, is_error=False):
        self.terminal_display.config(state=tk.NORMAL)
        self.terminal_display.insert(tk.END, text + "\n")
        if is_error:
            self.terminal_display.tag_add("term_error", "insert linestart", "insert lineend")
            self.terminal_display.tag_config("term_error", foreground="#FF5555")
        self.terminal_display.see(tk.END)
        self.terminal_display.config(state=tk.DISABLED)

    def run_terminal_command(self, command):
        def target():
            self.write_terminal(f"\n> Executing: {command}")
            try:
                # 자바 프로젝트 위치(demo) 기준 실행
                working_dir = os.path.join(os.getcwd(), "demo")
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                           text=True, cwd=working_dir)
                stdout, stderr = process.communicate()
                
                if stdout: self.write_terminal(stdout)
                if stderr: 
                    self.write_terminal(stderr, is_error=True)
                    self.last_error_log = stderr
                    self.root.after(0, lambda: self.add_message("SYSTEM", "빌드 에러 감지! '고쳐줘'라고 입력하면 분석을 시작합니다.", "error"))
                else:
                    self.last_error_log = None
                    self.root.after(0, lambda: self.add_message("SYSTEM", "명령어 실행 성공!", "system"))

            except Exception as e:
                self.write_terminal(f"Execution Failed: {str(e)}", is_error=True)

        threading.Thread(target=target, daemon=True).start()

    def add_message(self, sender, text, tag_name=None):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"\n[{timestamp}] {sender}: ", tag_name if tag_name else sender.lower())

        if sender == "AI":
            # 1. RUN_COMMAND 감지
            cmd_match = re.search(r'RUN_COMMAND:\s*(.*)', text)
            if cmd_match:
                cmd = cmd_match.group(1).strip()
                self.root.after(100, lambda c=cmd: self.run_terminal_command(c))

            # 2. 코드 블록 및 수정 대상 파일 감지
            parts = re.split(r'(TARGET_PATH:.*?```[\s\S]*?```)', text)
            for part in parts:
                path_match = re.search(r'TARGET_PATH:\s*(.*?)\n', part)
                code_match = re.search(r'```(?:\w+)?\n([\s\S]*?)```', part)

                if path_match and code_match:
                    file_path = path_match.group(1).strip()
                    code_content = code_match.group(1).strip()
                    unique_tag = f"apply_{len(self.code_blocks_map)}"
                    self.code_blocks_map[unique_tag] = {'code': code_content, 'path': file_path}
                    
                    self.chat_display.insert(tk.END, f"\n📂 {file_path} (클릭하여 반영)\n", "system")
                    self.chat_display.insert(tk.END, f"{code_content}\n", ("ai", unique_tag))
                    self.chat_display.tag_bind(unique_tag, "<Button-1>", lambda e, t=unique_tag: self.apply_to_file(t))
                else:
                    self.chat_display.insert(tk.END, part, "ai")
        else:
            self.chat_display.insert(tk.END, text + "\n", "ai")

        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def apply_to_file(self, tag_name):
        data = self.code_blocks_map.get(tag_name)
        if not data: return
        file_path, code = data['path'], data['code']
        
        if messagebox.askyesno("확인", f"[{file_path}] 수정하시겠습니까?"):
            try:
                full_path = os.path.join(os.getcwd(), file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(code)
                self.write_terminal(f"✔ File Updated: {file_path}")
                return True
            except Exception as e:
                messagebox.showerror("오류", str(e))
        return False

    def initial_setup(self):
        threading.Thread(target=self._initialize_backend, daemon=True).start()

    def _initialize_backend(self):
        """API 연동 및 모델 자동 선택"""
        try:
            build_index()
            genai.configure(api_key=GEMINI_API_KEY)
            
            # 가용 모델 리스트 확인
            available_models = [m.name for m in genai.list_models() 
                                if 'generateContent' in m.supported_generation_methods]
            
            # 1.5-flash를 우선순위로, 없으면 첫 번째 모델 선택
            target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
            
            self.model = genai.GenerativeModel(target_model)
            self.root.after(0, lambda: self.add_message("SYSTEM", f"짭커서 2.0 가동! (연결 모델: {target_model})"))
        except Exception as e:
            self.root.after(0, lambda: self.add_message("SYSTEM", f"초기화 실패: {str(e)}", "error"))

    def process_input(self):
        if self.is_processing or not self.model: return
        prompt = self.input_entry.get().strip()
        if not prompt: return

        self.add_message("USER", prompt)
        self.input_entry.delete(0, tk.END)
        self.is_processing = True
        self.send_button.config(state=tk.DISABLED, text="⚡ 처리 중...")
        
        threading.Thread(target=self._run_ai_logic, args=(prompt,), daemon=True).start()

    def _run_ai_logic(self, prompt):
        try:
            # 메모리 매니저에서 최근 맥락 가져오기
            recent_context = get_recent_context_for_prompt()
            current_outline = get_project_outline()
            
            # AI 프롬프트 조합
            full_prompt = f"{recent_context}\n\n[USER REQUEST]\n{prompt}"
            
            # agent_core 분석 엔진 실행
            response_stream, files_used = analyze_project_and_get_response_fast(
                full_prompt, self.model, current_outline, self.last_error_log
            )
            
            full_text = ""
            for chunk in response_stream:
                if chunk.text: full_text += chunk.text
            
            self.root.after(0, lambda: self.add_message("AI", full_text))
            
            # 대화 종료 후 메모리에 박제 (에러 로그 포함)
            add_working_cache(prompt, full_text, files_used, error_log=self.last_error_log)
            
        except Exception as e:
            self.root.after(0, lambda: self.add_message("SYSTEM", f"오류: {str(e)}", "error"))
        finally:
            self.root.after(0, self._reset_ui_state)

    def _reset_ui_state(self):
        self.is_processing = False
        self.send_button.config(state=tk.NORMAL, text="⚡ 분석 및 실행")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x1000")
    app = PseudoCursorInterface(root)
    root.mainloop()