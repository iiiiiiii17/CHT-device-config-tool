import sys
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import filedialog

import os
import sys
import urllib.request
import subprocess
from tkinter import ttk
import shutil  
import time

APP_NAME = "設備設定工具"
APP_VERSION = "0.9.9"
VERSION_URL = "https://raw.githubusercontent.com/iiiiiiii17/CHT-device-config-tool/refs/heads/main/version.txt"

# 判斷程式是否被打包成 exe
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).parent

file_path = base_path / "null"

# ------------------ GUI ------------------ #
root = tk.Tk()
root.title(f"{APP_NAME} v{APP_VERSION}")
root.geometry("850x500")

# 選擇檔案按鈕獨立第一排
choose_file_frame = tk.Frame(root)
choose_file_frame.pack(fill="x", pady=5)
current_file_label = tk.Label(choose_file_frame, text=f"目前檔案: {file_path.name}", anchor="w")
current_file_label.pack(side="left", padx=10)
# 舊按鈕 frame 保留原本按鈕
button_frame = tk.Frame(root)
button_frame.pack(fill="x", pady=5)


# 搜尋區
frame = tk.Frame(root)
frame.pack(fill="x", pady=5)

# tk.Label(frame, text="Hostname：").pack(side="left", padx=5)
# hostname_var = tk.StringVar()
# hostname_entry = tk.Entry(frame, textvariable=hostname_var, width=15)
# hostname_entry.pack(side="left", padx=5)
tk.Label(frame, text="Hostname：").pack(side="left", padx=5)
hostname_prefix_var = tk.StringVar()
hostname_prefix_entry = tk.Entry(frame, textvariable=hostname_prefix_var, width=10)
hostname_prefix_entry.pack(side="left", padx=5)

tk.Label(frame, text="流水號：").pack(side="left", padx=5)
hostname_suffix_var = tk.StringVar()
hostname_suffix_entry = tk.Entry(frame, textvariable=hostname_suffix_var, width=10)
hostname_suffix_entry.pack(side="left", padx=5)

tk.Label(frame, text="管理IP：").pack(side="left", padx=5)
mgmt_ip_var = tk.StringVar()
mgmt_ip_entry = tk.Entry(frame, textvariable=mgmt_ip_var, width=15)
mgmt_ip_entry.pack(side="left", padx=5)

tk.Label(frame, text="遮罩：").pack(side="left", padx=5)
mask_var = tk.StringVar()
mask_entry = tk.Entry(frame, textvariable=mask_var, width=15)
mask_entry.pack(side="left", padx=5)

# 文字區
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("微軟正黑體", 12))
text_area.pack(expand=True, fill='both')
text_area.config(state=tk.DISABLED)

# ------------------ 功能 ------------------ #

def load_file():
    """顯示完整檔案"""
    text_area.config(state=tk.NORMAL)
    text_area.delete('1.0', tk.END)

    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                text_area.insert(tk.END, line)
    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設備1.txt")

    text_area.config(state=tk.DISABLED)
current_file_label.config(text=f"目前檔案: {file_path.name}")

def get_hostname():
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip().lower().startswith("hostname"):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        full_hostname = parts[1]
                        if '-' in full_hostname:
                            prefix, suffix = full_hostname.split('-', 1)
                            hostname_prefix_var.set(prefix)
                            hostname_suffix_var.set(suffix)
                        return
        messagebox.showinfo("提示", "找不到 hostname")
    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設備1.txt")

# def modify_hostname():
#     """一鍵修改 hostname"""
#     new_hostname = hostname_var.get().strip()

#     if not new_hostname:
#         messagebox.showwarning("警告", "請輸入新的 hostname")
#         return

#     try:
#         lines = []
#         found = False

#         with file_path.open("r", encoding="utf-8") as f:
#             for line in f:
#                 if line.strip().lower().startswith("hostname"):
#                     indent = line[:len(line) - len(line.lstrip())]
#                     lines.append(f"{indent}hostname {new_hostname}\n")
#                     found = True
#                 else:
#                     lines.append(line)

#         if not found:
#             messagebox.showinfo("提示", "檔案內沒有 hostname 設定")
#             return

#         # 寫回檔案
#         with file_path.open("w", encoding="utf-8") as f:
#             f.writelines(lines)

#         messagebox.showinfo("成功", "Hostname 修改完成！")
#         load_file()

#     except FileNotFoundError:
#         messagebox.showerror("錯誤", "找不到設備1.txt")


def copy_all_content():
    """一鍵複製全部設定到剪貼簿"""
    text_area.config(state=tk.NORMAL)
    content = text_area.get("1.0", tk.END).strip()

    if not content:
        messagebox.showwarning("警告", "沒有內容可以複製")
        text_area.config(state=tk.DISABLED)
        return

    root.clipboard_clear()
    root.clipboard_append(content)
    root.update()  # 確保剪貼簿更新

    text_area.config(state=tk.DISABLED)
    messagebox.showinfo("成功", "已複製到剪貼簿！")        

def get_management_ip():
    # 定義所有可能的關鍵字前綴
    target_prefixes = [
        "ip address default-management",
        "ip address inband-default"
    ]
    
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip().lower()
                
                # 檢查目前這一行是否以任一關鍵字開頭
                for prefix in target_prefixes:
                    if clean_line.startswith(prefix):
                        parts = line.strip().split()
                        
                        # 核心邏輯：計算前綴長度來動態抓取 IP
                        # 例如 "ip address inband-default" 有 3 個單字，IP 就會在 parts[3]
                        prefix_len = len(prefix.split())
                        
                        if len(parts) >= prefix_len + 2:
                            mgmt_ip_var.set(parts[prefix_len])     # IP 位址
                            mask_var.set(parts[prefix_len + 1])   # 遮罩
                            return # 找到就結束函式
                            
            messagebox.showinfo("提示", "找不到管理 IP 或 Inband IP 設定")
        
    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設定檔案")

# def modify_management_ip():
#     new_ip = mgmt_ip_var.get().strip()

#     if not new_ip:
#         messagebox.showwarning("警告", "請輸入新的管理IP")
#         return

#     try:
#         lines = []
#         found = False

#         with file_path.open("r", encoding="utf-8") as f:
#             for line in f:
#                 if line.strip().lower().startswith("ip address default-management"):
#                     parts = line.strip().split()
#                     if len(parts) >= 5:
#                         mask = parts[4]  # 保留原本遮罩
#                         indent = line[:len(line) - len(line.lstrip())]
#                         lines.append(f"{indent}ip address default-management {new_ip} {mask}\n")
#                         found = True
#                     else:
#                         lines.append(line)
#                 else:
#                     lines.append(line)

#         if not found:
#             messagebox.showinfo("提示", "檔案內沒有管理IP設定")
#             return

#         with file_path.open("w", encoding="utf-8") as f:
#             f.writelines(lines)

#         messagebox.showinfo("成功", "管理IP修改完成！")
#         load_file()

#     except FileNotFoundError:
#         messagebox.showerror("錯誤", "找不到設備1.txt")       

def modify_all():
    """同時修改 hostname + 管理IP"""

    new_ip = mgmt_ip_var.get().strip()
    new_mask = mask_var.get().strip()
    prefix = hostname_prefix_var.get().strip()
    suffix = hostname_suffix_var.get().strip()

    # hostname 組合邏輯
    if prefix or suffix:
        new_hostname = f"{prefix}-{suffix}"
    else:
        new_hostname = ""

    if not new_hostname and not new_ip:
        messagebox.showwarning("警告", "請輸入要修改的內容")
        return

    target_prefixes = [
        "ip address default-management",
        "ip address inband-default"
    ]

    try:
        lines = []
        hostname_found = False
        ip_found = False

        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                lower_line = stripped.lower()

                # =====================
                # 修改 hostname
                # =====================
                if lower_line.startswith("hostname") and new_hostname:
                    indent = line[:len(line) - len(line.lstrip())]
                    lines.append(f"{indent}hostname {new_hostname}\n")
                    hostname_found = True
                    continue

                # =====================
                # 修改 管理IP（動態 prefix）
                # =====================
                modified = False

                for prefix_text in target_prefixes:
                    if lower_line.startswith(prefix_text) and new_ip:

                        parts = stripped.split()
                        prefix_len = len(prefix_text.split())

                        if len(parts) > prefix_len:

                            # 取得原本遮罩（若沒輸入新遮罩）
                            old_mask = parts[prefix_len + 1] if len(parts) > prefix_len + 1 else ""
                            mask = new_mask if new_mask else old_mask

                            indent = line[:len(line) - len(line.lstrip())]
                            lines.append(
                                f"{indent}{prefix_text} {new_ip} {mask}\n"
                            )

                            ip_found = True
                            modified = True
                            break

                if modified:
                    continue

                # 其他行原樣保留
                lines.append(line)

        if not hostname_found and new_hostname:
            messagebox.showinfo("提示", "找不到 hostname 設定")

        if not ip_found and new_ip:
            messagebox.showinfo("提示", "找不到 管理IP 設定")

        with file_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)

        messagebox.showinfo("成功", "修改完成！")
        load_file()

    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設定檔")


# def choose_file():
#     global file_path
#     selected = filedialog.askopenfilename(
#         title="選擇設備 Config",
#         filetypes=[("Config File", "*.txt"), ("All Files", "*.*")]
#     )
#     if selected:
#         file_path = Path(selected)
#         load_file()
#         get_hostname()
#         get_management_ip()
#         current_file_label.config(text=f"目前檔案: {file_path.name}")
def choose_file():
    global file_path
    
    # 取得程式執行時的實際目錄 (如果是 exe，就是 exe 所在的資料夾)
    # 注意：這裡使用 Path(sys.executable).parent 是為了在打包後能回到 exe 旁邊
    # 如果是在開發環境，則使用 Path(__file__).parent
    current_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

    selected = filedialog.askopenfilename(
        title="選擇設備 Config",
        initialdir=current_dir,  # <--- 設定起始目錄
        filetypes=[("Config File", "*.txt"), ("All Files", "*.*")]
    )
    
    if selected:
        file_path = Path(selected)
        load_file()
        get_hostname()
        get_management_ip()
        current_file_label.config(text=f"目前檔案: {file_path.name}")


def version_tuple(v):
    try:
        # 只保留數字與點，過濾掉其餘字元
        clean_v = "".join(c for c in v if c.isdigit() or c == '.')
        return tuple(map(int, clean_v.split(".")))
    except Exception as e:
        print(f"版本號解析錯誤 ({v}): {e}")
        return (0, 0, 0)

def check_for_update():
    # 加上隨機參數避免 GitHub 快取
    target_url = f"{VERSION_URL}?t={int(time.time())}"
    print(f"[*] 正在檢查更新... URL: {target_url}")
    
    try:
        with urllib.request.urlopen(target_url, timeout=5) as response:
            # 讀取並解碼
            raw_data = response.read().decode("utf-8")
            # 關鍵修正：使用 splitlines 並過濾掉純空白的行
            lines = [line.strip() for line in raw_data.splitlines() if line.strip()]
            
        print(f"[*] 抓取到的行數: {len(lines)}")
        for i, content in enumerate(lines):
            print(f"    行 {i}: {content}")

        if len(lines) < 2:
            print("[!] 錯誤：雲端檔案格式不正確，行數不足 2 行。")
            return

        latest_version = lines[0]
        download_url = lines[1]
        
        print(f"[*] 雲端最新版本: {latest_version}")
        print(f"[*] 程式目前版本: {APP_VERSION}")

        # 比較版本 (確保使用你定義的 version_tuple)
        if version_tuple(latest_version) > version_tuple(APP_VERSION):
            print("[+] 偵測到新版本！")
            result = messagebox.askyesno(
                "發現新版本",
                f"目前版本：{APP_VERSION}\n"
                f"最新版本：{latest_version}\n\n"
                "是否立即下載更新並自動重啟？"
            )
            if result:
                auto_update(download_url)
        else:
            print("[-] 目前已是最新版本。")

    except Exception as e:
        print(f"[!] 檢查更新失敗: {e}")

# ------------------ 按鈕 ------------------ #
choose_file_button = tk.Button(
    choose_file_frame,
    text="選擇檔案",
    command=choose_file,
    bg="#2196F3",   # 藍色背景
    fg="white",
    font=("微軟正黑體", 11, "bold")
)
choose_file_button.pack(side="left", padx=5)

tk.Button(button_frame, text="讀檔(save)", width=12, command=load_file).pack(side="left", padx=5)
# tk.Button(button_frame, text="讀取Hostname", width=12, command=get_hostname).pack(side="left", padx=5)
#tk.Button(button_frame, text="修改Hostname", width=12, command=modify_hostname).pack(side="left", padx=5)
# tk.Button(button_frame, text="讀取管理IP", width=12, command=get_management_ip).pack(side="left", padx=5)
#tk.Button(button_frame, text="修改管理IP", width=12, command=modify_management_ip).pack(side="left", padx=5)
tk.Button(button_frame, text="修改", width=12, command=modify_all).pack(side="left", padx=5)
tk.Button(button_frame, text="一鍵複製", width=12, command=copy_all_content).pack(side="left", padx=5)
#k.Button(button_frame, text="選擇檔案", width=12, command=choose_file).pack(side="left", padx=5)


# 啟動
root.after(1000, check_for_update)
root.mainloop()