import os
import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading 
from datetime import datetime
import re

# 설정 및 모듈 임포트
from config import *
from memory_manager import load_memory, add_working_cache, get_recent_context_for_prompt
from agent_core import build_index, analyze_project_and_get_response_fast, get_project_outline

class AgentInterfaceTkinter:
    def __init__(self, root, initial_memory):
        self.root = root
        self.root.title("AI Flow Architect - Real Code Copier")
        
        self.model = None
        self.is_processing = False 
        self.code_blocks_map = {} # {태그이름: 코드내용}

        self.setup_ui()
        self.initial_setup()

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # 1. 채팅 디스플레이
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=110, height=35, 
                                                      font=("Consolas", 11), bg="#ffffff")
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")
        self.chat_display.config(state=tk.DISABLED)

        # 스타일 설정
        self.chat_display.tag_configure("system", foreground="#28a745", font=("Consolas", 10, "bold"))
        self.chat_display.tag_configure("user", foreground="#0056b3", font=("Consolas", 11, "bold"))
        self.chat_display.tag_configure("ai", foreground="#212529", font=("Consolas", 11))
        self.chat_display.tag_configure("path", foreground="#6f42c1", font=("Consolas", 10, "italic"))
        self.chat_display.tag_configure("error", foreground="#dc3545", font=("Consolas", 11, "bold"))
        
        # [코드 블록 전용 태그]
        self.chat_display.tag_configure("code_block_style", 
                                        background="#1e1e1e", 
                                        foreground="#d4d4d4", 
                                        font=("Consolas", 10),
                                        spacing1=10, spacing3=10, 
                                        lmargin1=40, lmargin2=40)

        # 2. 입력 영역
        input_frame = tk.Frame(self.root)
        input_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = tk.Entry(input_frame, font=("Malgun Gothic", 12))
        self.input_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_entry.bind("<Return>", lambda event: self.process_input()) 

        self.send_button = tk.Button(input_frame, text="🔍 분석 시작", command=self.process_input, 
                                     width=15, bg="#007bff", fg="white", font=("Malgun Gothic", 10, "bold"))
        self.send_button.grid(row=0, column=1)

    def add_message(self, sender, text, tag_name=None):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 발신자 태그 설정
        display_tag = tag_name if tag_name else sender.lower()
        self.chat_display.insert(tk.END, f"\n[{timestamp}] {sender}: ", display_tag)

        if sender == "AI":
            parts = re.split(r'(```[\s\S]*?```)', text)
            for part in parts:
                if part.startswith("```"):
                    code_content = re.sub(r'^```\w*\n', '', part)
                    code_content = code_content.strip("`").strip()
                    
                    unique_tag = f"code_tag_{len(self.code_blocks_map)}"
                    self.code_blocks_map[unique_tag] = code_content
                    
                    self.chat_display.insert(tk.END, f"\n{code_content}\n", ("code_block_style", unique_tag))
                    
                    self.chat_display.tag_bind(unique_tag, "<Button-1>", lambda e, t=unique_tag: self.copy_to_clipboard(t))
                    self.chat_display.tag_bind(unique_tag, "<Enter>", lambda e: self.chat_display.config(cursor="hand2"))
                    self.chat_display.tag_bind(unique_tag, "<Leave>", lambda e: self.chat_display.config(cursor=""))
                else:
                    self.chat_display.insert(tk.END, part, "ai")
        else:
            self.chat_display.insert(tk.END, text + "\n", display_tag)

        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def copy_to_clipboard(self, tag_name):
        code = self.code_blocks_map.get(tag_name)
        if code:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("복사 완료", "코드가 클립보드에 복사되었습니다!")

    def initial_setup(self):
        threading.Thread(target=self._initialize_backend, daemon=True).start()

    def _initialize_backend(self):
        """[수정됨] 사용 가능한 모델을 자동으로 찾아 초기화합니다."""
        try:
            file_count = build_index()
            genai.configure(api_key=GEMINI_API_KEY)
            
            # 현재 계정에서 사용 가능한 모델 목록 조회
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 1.5-flash 모델 우선 검색, 없으면 첫 번째 가용한 모델 선택
            target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), 
                                available_models[0] if available_models else None)

            if not target_model:
                raise Exception("사용 가능한 Gemini 모델을 찾을 수 없습니다. API 키를 확인하세요.")

            self.model = genai.GenerativeModel(target_model)
            self.root.after(0, lambda: self.add_message("SYSTEM", f"준비 완료! [모델: {target_model}] [인덱싱: {file_count}개 파일]"))
        except Exception as e:
            self.root.after(0, lambda: self.add_message("SYSTEM", f"초기화 실패: {str(e)}", "error"))

    def process_input(self):
        if self.is_processing or not self.model: return
        prompt = self.input_entry.get().strip()
        if not prompt: return

        self.add_message("USER", prompt)
        self.input_entry.delete(0, tk.END)
        self.is_processing = True
        self.send_button.config(state=tk.DISABLED, text="🔍 분석 중...")
        
        threading.Thread(target=self._run_ai_logic, args=(prompt,), daemon=True).start()

    def _run_ai_logic(self, prompt):
        try:
            recent_context = get_recent_context_for_prompt()
            current_outline = get_project_outline()
            full_prompt = f"{recent_context}\n\n[NEW QUESTION]\n{prompt}"
            
            response_stream, files_used = analyze_project_and_get_response_fast(
                full_prompt, self.model, current_outline, None
            )
            
            full_text = ""
            for chunk in response_stream:
                if chunk.text: full_text += chunk.text
            
            self.root.after(0, lambda: self.add_message("AI", full_text))
            add_working_cache(prompt, full_text, files_used)
            
        except Exception as e:
            self.root.after(0, lambda: self.add_message("SYSTEM", f"분석 오류: {str(e)}", "error"))
        finally:
            self.root.after(0, self._reset_ui_state)

    def _reset_ui_state(self):
        self.is_processing = False
        self.send_button.config(state=tk.NORMAL, text="🔍 분석 시작")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x900")
    app = AgentInterfaceTkinter(root, load_memory())
    app.run()