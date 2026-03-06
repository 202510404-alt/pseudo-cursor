import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading 
from datetime import datetime
import re
import subprocess 

# [수정 1] 새롭게 바뀐 3단계 두뇌 'APIManager'를 임포트합니다.
try:
    from assistant_head.api_manager import APIManager
except ImportError as e:
    print(f"🚨 모듈 임포트 실패: {e}")
    # 테스트를 위한 가짜 클래스 (APIManager 스펙에 맞춤)
    class APIManager:
        def __init__(self): self.last_error_log = None
        def get_model_for_tier(self, tier): return "gemini-2.0-flash", "Gemini 2.0 Flash"
        def run_ai_logic(self, p, update_ui_callback, terminal_callback):
            ticks = chr(96) * 3
            msg = f"안녕하세요! 테스트 모드입니다.\n\nTARGET_PATH: hello.py\n{ticks}python\nprint('테스트 완료!')\n{ticks}"
            update_ui_callback("AI", msg)

class PseudoCursorInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Pseudo-Cursor v2.0 (Clean UI & MSA 3-Stage AI)")
        
        # [수정 2] ai_handler 대신 api_manager로 이름 변경
        self.api_manager = APIManager()
        self.is_processing = False 
        self.code_blocks_map = {} 

        self.setup_ui()
        self.initial_setup()

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)

        # 채팅창 설정 - 기본 배경을 흰색으로
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=110, height=25, 
                                                      font=("Malgun Gothic", 11), bg="#ffffff", fg="#222222")
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        self.chat_display.config(state=tk.DISABLED)

        # 터미널 설정
        self.terminal_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=110, height=10, 
                                                          font=("Consolas", 10), bg="#121212", fg="#00FF41")
        self.terminal_display.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="nsew")
        self.terminal_display.config(state=tk.DISABLED)

        # --- 스타일 태그 정의 (중요) ---
        self.chat_display.tag_configure("system", foreground="#008080", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("user", foreground="#0056b3", font=("Malgun Gothic", 11, "bold"))
        self.chat_display.tag_configure("ai", foreground="#e67e22", font=("Malgun Gothic", 11, "bold"))
        
        # 일반 대화: 배경 흰색(#ffffff)
        self.chat_display.tag_configure("ai_text", foreground="#333333", background="#ffffff", font=("Malgun Gothic", 11))
        
        # 코드 블록: 배경 어두운 회색(#1e1e1e), 글자 연한 회색(#d4d4d4)
        self.chat_display.tag_configure("ai_code", background="#1e1e1e", foreground="#d4d4d4", 
                                        font=("Consolas", 11), spacing1=8, spacing3=8)
        
        self.chat_display.tag_configure("error", foreground="#d9534f", font=("Malgun Gothic", 11, "bold"))

        # 입력창 영역
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = tk.Entry(input_frame, font=("Malgun Gothic", 12), bg="#ffffff", relief=tk.SOLID, bd=1)
        self.input_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew", ipady=7)
        self.input_entry.bind("<Return>", lambda event: self.process_input()) 

        self.send_button = tk.Button(input_frame, text="⚡ 분석 및 실행", command=self.process_input, 
                                     width=15, bg="#007acc", fg="white", font=("Malgun Gothic", 10, "bold"))
        self.send_button.grid(row=0, column=1)

    def write_terminal(self, text, is_error=False):
        self.terminal_display.config(state=tk.NORMAL)
        self.terminal_display.insert(tk.END, text + "\n")
        if is_error:
            self.terminal_display.tag_add("term_error", "insert linestart", "insert lineend")
            self.terminal_display.tag_config("term_error", foreground="#FF6B6B")
        self.terminal_display.see(tk.END)
        self.terminal_display.config(state=tk.DISABLED)

    def initial_setup(self):
        def init():
            try:
                # [수정 3] build_index() 삭제! 
                # 이제 1단계 에이전트가 알아서 파일을 찾으므로 초기화 때 전체 폴더를 뒤질 필요가 없습니다.
                m_name, d_name = self.api_manager.get_model_for_tier("NORMAL")
                self.root.after(0, lambda: self.add_message("SYSTEM", f"짭커서 가동 완료! (기본 모델: {d_name})", "system"))
            except Exception as e:
                self.root.after(0, lambda: self.add_message("SYSTEM", f"초기화 오류: {str(e)}", "error"))
        threading.Thread(target=init, daemon=True).start()

    def process_input(self):
        if self.is_processing: return
        prompt = self.input_entry.get().strip()
        if not prompt: return
        
        self.add_message("USER", prompt)
        self.input_entry.delete(0, tk.END)
        self.is_processing = True
        self.send_button.config(state=tk.DISABLED, text="⚡ 분석 중...")
        
        threading.Thread(target=self._run_logic_wrapper, args=(prompt,), daemon=True).start()

    def _run_logic_wrapper(self, prompt):
        # [수정 4] api_manager로 실행
        self.api_manager.run_ai_logic(
            prompt,
            update_ui_callback=lambda s, t, tag=None: self.root.after(0, self.add_message, s, t, tag),
            terminal_callback=lambda m: self.root.after(0, self.write_terminal, m)
        )
        self.root.after(0, self._reset_ui_state)

    def _reset_ui_state(self):
        self.is_processing = False
        self.send_button.config(state=tk.NORMAL, text="⚡ 분석 및 실행")

    def add_message(self, sender, text, tag_name=None):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        name_tag = tag_name if tag_name else sender.lower()
        self.chat_display.insert(tk.END, f"\n[{timestamp}] {sender}: ", name_tag)

        if sender == "AI":
            cmd_match = re.search(r'RUN_COMMAND:\s*(.*)', text)
            if cmd_match:
                cmd = cmd_match.group(1).strip()
                self.root.after(100, lambda c=cmd: self.run_terminal_command(c))

            # 코드 블록 파싱 (기존 로직 유지)
            pattern = re.compile(r'(TARGET_PATH:.*?`{3}[\s\S]*?`{3})', re.DOTALL)
            parts = pattern.split(text)

            for part in parts:
                if not part: continue

                path_match = re.search(r'TARGET_PATH:\s*(.*?)\n', part)
                code_match = re.search(r'`{3}(?:\w+)?\n([\s\S]*?)`{3}', part)

                if path_match and code_match:
                    file_path = path_match.group(1).strip()
                    code_content = code_match.group(1).strip()
                    unique_tag = f"apply_{len(self.code_blocks_map)}"
                    self.code_blocks_map[unique_tag] = {'code': code_content, 'path': file_path}
                    
                    self.chat_display.insert(tk.END, f"\n📂 {file_path} (클릭하여 반영)\n", "system")
                    self.chat_display.insert(tk.END, f"{code_content}\n", ("ai_code", unique_tag))
                    
                    self.chat_display.tag_bind(unique_tag, "<Button-1>", lambda e, t=unique_tag: self.apply_to_file(t))
                    self.chat_display.tag_bind(unique_tag, "<Enter>", lambda e: self.chat_display.config(cursor="hand2"))
                    self.chat_display.tag_bind(unique_tag, "<Leave>", lambda e: self.chat_display.config(cursor=""))
                else:
                    self.chat_display.insert(tk.END, part, "ai_text")
        else:
            self.chat_display.insert(tk.END, text + "\n", name_tag)

        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def apply_to_file(self, tag_name):
        data = self.code_blocks_map.get(tag_name)
        if not data: return
        file_path, code = data['path'], data['code']
        if messagebox.askyesno("Confirm", f"[{file_path}]\n파일에 반영하시겠습니까?"):
            try:
                full_path = os.path.join(os.getcwd(), file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(code)
                self.write_terminal(f"✔ File Updated: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def run_terminal_command(self, command):
        def target():
            self.write_terminal(f"\n> Executing: {command}")
            try:
                working_dir = os.getcwd()
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=working_dir)
                stdout, stderr = process.communicate()
                
                if stdout: self.write_terminal(stdout)
                if stderr: 
                    self.write_terminal(stderr, is_error=True)
                    # [치유 발동 포인트]
                    self.api_manager.last_error_log = stderr
                    
                    # 만약 사용자가 '자동 치유' 모드를 원한다면 여기서 바로 다음 시도를 트리거할 수 있습니다.
                    # self.root.after(1000, lambda: self._run_logic_wrapper("터미널 에러를 확인하고 자가 치유를 시작해."))
            except Exception as e:
                self.write_terminal(f"Failed: {str(e)}", is_error=True)
        threading.Thread(target=target, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x900")
    app = PseudoCursorInterface(root)
    root.mainloop()