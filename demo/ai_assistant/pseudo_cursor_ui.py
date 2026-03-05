import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading 
from datetime import datetime
import re
import subprocess 

from agent_core import build_index
from ai_handler import AIHandler

class PseudoCursorInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Pseudo-Cursor v2.0 (Self-Healing Modular)")
        
        self.ai_handler = AIHandler()
        self.is_processing = False 
        self.code_blocks_map = {} 

        self.setup_ui()
        self.initial_setup()

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)

        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=110, height=20, 
                                                     font=("Malgun Gothic", 11), bg="#fdfdfd", fg="#222222")
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")
        self.chat_display.config(state=tk.DISABLED)

        self.terminal_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=110, height=10, 
                                                         font=("Consolas", 10), bg="#121212", fg="#00FF41")
        self.terminal_display.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="nsew")
        self.terminal_display.config(state=tk.NORMAL)
        self.terminal_display.insert(tk.END, "--- [SYSTEM] PSEUDO-TERMINAL READY ---\n")
        self.terminal_display.config(state=tk.DISABLED)

        # 스타일 설정
        self.chat_display.tag_configure("system", foreground="#008080", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("user", foreground="#0056b3", font=("Malgun Gothic", 11, "bold"))
        self.chat_display.tag_configure("ai_text", foreground="#333333", font=("Malgun Gothic", 11))
        self.chat_display.tag_configure("ai_code", background="#1e1e1e", foreground="#d4d4d4", 
                                        font=("Consolas", 11), spacing1=8, spacing3=8)
        self.chat_display.tag_configure("error", foreground="#d9534f", font=("Malgun Gothic", 11, "bold"))

        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = tk.Entry(input_frame, font=("Malgun Gothic", 12), bg="#ffffff", relief=tk.SOLID, bd=1)
        self.input_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew", ipady=5)
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
                build_index()
                m_name, d_name = self.ai_handler.get_best_model()
                self.root.after(0, lambda: self.add_message("SYSTEM", f"짭커서 가동! (사용 모델: {d_name})"))
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
        self.ai_handler.run_ai_logic(
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
        self.chat_display.insert(tk.END, f"\n[{timestamp}] {sender}: ", tag_name if tag_name else sender.lower())

        if sender == "AI":
            # 명령어 실행 체크
            cmd_match = re.search(r'RUN_COMMAND:\s*(.*)', text)
            if cmd_match:
                cmd = cmd_match.group(1).strip()
                self.root.after(100, lambda c=cmd: self.run_terminal_command(c))

            # 코드 블록 및 파일 경로 파싱
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
                    self.chat_display.insert(tk.END, f"{code_content}\n", ("ai_code", unique_tag))
                    self.chat_display.tag_bind(unique_tag, "<Button-1>", lambda e, t=unique_tag: self.apply_to_file(t))
                else:
                    self.chat_display.insert(tk.END, part, "ai_text")
        else:
            self.chat_display.insert(tk.END, text + "\n", tag_name if tag_name else "user")

        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def apply_to_file(self, tag_name):
        data = self.code_blocks_map.get(tag_name)
        if not data: return
        file_path, code = data['path'], data['code']
        if messagebox.askyesno("Confirm Update", f"[{file_path}]\n파일을 수정하시겠습니까?"):
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
                # 'demo' 폴더가 있으면 거기서 실행, 없으면 현재 경로
                working_dir = os.path.join(os.getcwd(), "demo")
                if not os.path.exists(working_dir): working_dir = os.getcwd()
                
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=working_dir)
                stdout, stderr = process.communicate()
                
                if stdout: self.write_terminal(stdout)
                if stderr: 
                    self.write_terminal(stderr, is_error=True)
                    self.ai_handler.last_error_log = stderr
                else:
                    self.ai_handler.last_error_log = None
            except Exception as e:
                self.write_terminal(f"Execution Failed: {str(e)}", is_error=True)
        threading.Thread(target=target, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x1000")
    app = PseudoCursorInterface(root)
    root.mainloop()