import os
import io
import sys
import tempfile
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

ext = ".xml"
output_queue = queue.Queue()  # 创建队列用于线程间通信
total_cnt = 0

def process_file(src_file, dst_file):
    output_queue.put(f"----------------------------------------------------------------------------------------------\n")
    output_queue.put(f"[src] {src_file}\n")
    output_queue.put(f"[dst] {dst_file}\n")
    tmp_file = dst_file + ext
    # 解密，得到临时文件
    subprocess.run(["_internal\\notepad++.exe", src_file, tmp_file], creationflags=subprocess.CREATE_NO_WINDOW)
    # 创建空的目标文件，避免 xcopy 弹窗卡住
    subprocess.run(f'cmd /c copy /b nul "{dst_file}"', creationflags=subprocess.CREATE_NO_WINDOW)
    # 拷贝并重命名目标文件
    subprocess.run(f'xcopy "{tmp_file}" "{dst_file}" /Y', creationflags=subprocess.CREATE_NO_WINDOW, shell=True)
    # 删除临时文件
    subprocess.run(["cmd", "/c", "rm", tmp_file], creationflags=subprocess.CREATE_NO_WINDOW)

    global total_cnt
    total_cnt += 1
    output_queue.put(f"[CNT]: {total_cnt}\n")

def process_directory(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)

    for entry in os.listdir(src_dir):
        src_entry = os.path.join(src_dir, entry)
        dst_entry = os.path.join(dst_dir, entry)

        if os.path.isdir(src_entry):
            process_directory(src_entry, dst_entry)
        elif os.path.isfile(src_entry):
            process_file(src_entry, dst_entry)

def thread_fn(src_dir, dst_dir):
    src_dir = os.path.normpath(src_dir)
    dst_dir = os.path.normpath(dst_dir)

    output_queue.put("开始解密\n")
    total_cnt = 0

    # 禁用按钮
    start_button.config(state=tk.DISABLED)

    # 清空目标目录
    output_queue.put(f"----------------------------------------------------------------------------------------------\n")
    output_queue.put(f"清空目标目录：{dst_dir}\n")
    subprocess.run(f'cmd /c rmdir /s /q "{dst_dir}"', creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.run(f'cmd /c mkdir "{dst_dir}"', creationflags=subprocess.CREATE_NO_WINDOW)

    process_directory(src_dir, dst_dir)

    # 启用按钮
    start_button.config(state=tk.NORMAL)

    output_queue.put(f"----------------------------------------------------------------------------------------------\n")
    output_queue.put("解密完成\n")

def start_threaded_processing():
    src_path = src_dir_entry_var.get()
    dst_path = dst_entry_var.get()

    # 清空控制台
    console_text.config(state=tk.NORMAL)
    console_text.delete("1.0", tk.END)
    console_text.config(state=tk.DISABLED)

    if not src_path or not dst_path:
        output_queue.put("请选择源和目标！\n")
        return

    # 启动后台线程
    threading.Thread(target=thread_fn, args=(src_path, dst_path), daemon=True).start()

def update_console():
    while not output_queue.empty():
        message = output_queue.get()
        console_text.config(state=tk.NORMAL)
        console_text.insert(tk.END, message)
        console_text.see(tk.END)
        console_text.config(state=tk.DISABLED)

    root.after(100, update_console)  # 每 100ms 检查队列一次

# Tkinter GUI 设置
root = tk.Tk()
root.title("killer")
root.minsize(600, 600)
root.geometry("800x600")

# 设置窗口图标
root.iconbitmap("./_internal/LockedIcon.ico")

frame = tk.Frame(root)
frame.pack(anchor="w", padx=20, pady=20, fill=tk.BOTH, expand=True)

src_dir_entry_var = tk.StringVar()
dir_frame = tk.Frame(frame, bg="#f0f0f0")
dir_frame.pack(pady=5, fill=tk.X)
tk.Button(dir_frame, text="源目录", command=lambda: src_dir_entry_var.set(filedialog.askdirectory()), bg="#4CAF50", fg="white").pack(side=tk.LEFT)
tk.Entry(dir_frame, textvariable=src_dir_entry_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)

dst_entry_var = tk.StringVar()
dst_frame = tk.Frame(frame, bg="#f0f0f0")
dst_frame.pack(pady=5, fill=tk.X)
tk.Button(dst_frame, text="目标目录", command=lambda: dst_entry_var.set(filedialog.askdirectory()), bg="#4CAF50", fg="white").pack(side=tk.LEFT)
tk.Entry(dst_frame, textvariable=dst_entry_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)

# 控制台输出框和滚动条
console_frame = tk.Frame(frame)
console_frame.pack(pady=10, fill=tk.BOTH, expand=True)

console_text = tk.Text(console_frame, height=15, wrap=tk.WORD, bg="black", fg="white", state=tk.DISABLED)
console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(console_frame, command=console_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

console_text.config(yscrollcommand=scrollbar.set)

# 开始处理按钮
start_button = tk.Button(frame, text="开始解密", command=start_threaded_processing, bg="#2196F3", fg="white", font=("Arial", 18))
start_button.pack(pady=10)

# 定时刷新控制台
root.after(100, update_console)

# 启动主循环
root.mainloop()
