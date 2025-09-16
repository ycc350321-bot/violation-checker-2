import tkinter as tk
from tkinter import ttk, scrolledtext
import re
import threading

class ViolationWordChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("违规词匹配工具")
        self.root.geometry("800x600")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="违规词匹配工具（精确匹配）", font=("Arial", 16))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # 左侧违规词输入框
        ttk.Label(main_frame, text="违规词列表（每行一个）:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.violation_text = scrolledtext.ScrolledText(main_frame, width=30, height=10)
        self.violation_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 右侧待检查文本输入框
        ttk.Label(main_frame, text="待检查标题（每行一个标题）:").grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        self.check_text = scrolledtext.ScrolledText(main_frame, width=30, height=10)
        self.check_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 匹配按钮
        self.check_button = ttk.Button(main_frame, text="开始匹配", command=self.start_check_thread)
        self.check_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 结果显示框 - 匹配到的违规词
        ttk.Label(main_frame, text="匹配到的违规词:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        self.result_text = scrolledtext.ScrolledText(main_frame, width=80, height=10)
        self.result_text.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def start_check_thread(self):
        """启动检查线程，避免界面卡顿"""
        self.check_button.config(state='disabled')
        self.progress.start(10)
        self.status_var.set("正在匹配...")
        
        # 启动后台线程
        thread = threading.Thread(target=self.check_violation_words)
        thread.daemon = True
        thread.start()
        
        # 定期检查线程是否完成
        self.check_thread_status(thread)
    
    def check_thread_status(self, thread):
        """检查线程状态"""
        if thread.is_alive():
            # 线程仍在运行，稍后再次检查
            self.root.after(100, lambda: self.check_thread_status(thread))
        else:
            # 线程已完成，更新UI
            self.progress.stop()
            self.check_button.config(state='normal')
    
    def check_violation_words(self):
        # 获取违规词列表并转换为小写
        violation_words = self.violation_text.get("1.0", tk.END).strip().splitlines()
        violation_words = [word.strip().lower() for word in violation_words if word.strip()]
        
        # 获取待检查标题列表
        titles = self.check_text.get("1.0", tk.END).strip().splitlines()
        titles = [title.strip() for title in titles if title.strip()]
        
        # 在主线程中清空结果文本框
        self.root.after(0, lambda: self.clear_result_texts())
        
        if not violation_words:
            self.root.after(0, lambda: self.show_error("未输入任何违规词", "错误：未输入违规词"))
            return
        
        if not titles:
            self.root.after(0, lambda: self.show_error("未输入任何标题", "错误：未输入标题"))
            return
        
        # 查找匹配的违规词（精确匹配）
        found_words = set()  # 使用集合来避免重复
        titles_with_matches = []  # 存储包含匹配的标题
        
        for title in titles:
            # 转换为小写进行匹配
            lower_title = title.lower()
            title_matches = []
            
            for word in violation_words:
                # 使用正则表达式进行精确匹配（全词匹配）
                pattern = r'\b' + re.escape(word) + r'\b'
                matches = re.finditer(pattern, lower_title)
                
                for match in matches:
                    found_words.add(word)
            
        # 在主线程中更新结果
        self.root.after(0, lambda: self.update_results(found_words))
    
    def clear_result_texts(self):
        """清空结果文本框"""
        self.result_text.delete("1.0", tk.END)
    
    def show_error(self, error_msg, status_msg):
        """显示错误信息"""
        self.result_text.insert(tk.END, error_msg)
        self.status_var.set(status_msg)
    
    def update_results(self, found_words):
        """更新结果"""
        # 显示匹配到的违规词
        if found_words:
            result = f"发现 {len(found_words)} 个违规词:\n"
            for i, word in enumerate(found_words, 1):
                result += f"{i}. {word}\n"
            self.result_text.insert(tk.END, result)
            self.status_var.set(f"匹配完成：发现 {len(found_words)} 个违规词")
        else:
            self.result_text.insert(tk.END, "未发现任何违规词")
            self.status_var.set("匹配完成：未发现违规词")

if __name__ == "__main__":
    root = tk.Tk()
    app = ViolationWordChecker(root)
    root.mainloop()
