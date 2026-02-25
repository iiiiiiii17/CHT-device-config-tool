import sys
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext, messagebox

# 判斷程式是否被打包成 exe
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).parent

file_path = base_path / "設備1.txt"

# ------------------ GUI ------------------ #
root = tk.Tk()
root.title("設備設定工具")
root.geometry("850x500")
button_frame = tk.Frame(root)
button_frame.pack(fill="x", pady=5)

# 搜尋區
frame = tk.Frame(root)
frame.pack(fill="x", pady=5)

tk.Label(frame, text="Hostname：").pack(side="left", padx=5)
hostname_var = tk.StringVar()
hostname_entry = tk.Entry(frame, textvariable=hostname_var, width=15)
hostname_entry.pack(side="left", padx=5)

tk.Label(frame, text="管理IP：").pack(side="left", padx=5)
mgmt_ip_var = tk.StringVar()
mgmt_ip_entry = tk.Entry(frame, textvariable=mgmt_ip_var, width=15)
mgmt_ip_entry.pack(side="left", padx=5)

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


def get_hostname():
    """讀取 hostname 值"""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip().lower().startswith("hostname"):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        hostname_var.set(parts[1])
                        return
        messagebox.showinfo("提示", "找不到 hostname")
    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設備1.txt")


def modify_hostname():
    """一鍵修改 hostname"""
    new_hostname = hostname_var.get().strip()

    if not new_hostname:
        messagebox.showwarning("警告", "請輸入新的 hostname")
        return

    try:
        lines = []
        found = False

        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip().lower().startswith("hostname"):
                    indent = line[:len(line) - len(line.lstrip())]
                    lines.append(f"{indent}hostname {new_hostname}\n")
                    found = True
                else:
                    lines.append(line)

        if not found:
            messagebox.showinfo("提示", "檔案內沒有 hostname 設定")
            return

        # 寫回檔案
        with file_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)

        messagebox.showinfo("成功", "Hostname 修改完成！")
        load_file()

    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設備1.txt")

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
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip().lower().startswith("ip address default-management"):
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        mgmt_ip_var.set(parts[3])  # 第4個欄位是IP
                        return
        messagebox.showinfo("提示", "找不到管理IP設定")
    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設備1.txt")
def modify_management_ip():
    new_ip = mgmt_ip_var.get().strip()

    if not new_ip:
        messagebox.showwarning("警告", "請輸入新的管理IP")
        return

    try:
        lines = []
        found = False

        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip().lower().startswith("ip address default-management"):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        mask = parts[4]  # 保留原本遮罩
                        indent = line[:len(line) - len(line.lstrip())]
                        lines.append(f"{indent}ip address default-management {new_ip} {mask}\n")
                        found = True
                    else:
                        lines.append(line)
                else:
                    lines.append(line)

        if not found:
            messagebox.showinfo("提示", "檔案內沒有管理IP設定")
            return

        with file_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)

        messagebox.showinfo("成功", "管理IP修改完成！")
        load_file()

    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設備1.txt")       

# ------------------ 按鈕 ------------------ #

tk.Button(button_frame, text="讀檔", width=12, command=load_file).pack(side="left", padx=5)
tk.Button(button_frame, text="讀取Hostname", width=12, command=get_hostname).pack(side="left", padx=5)
tk.Button(button_frame, text="修改Hostname", width=12, command=modify_hostname).pack(side="left", padx=5)
tk.Button(button_frame, text="讀取管理IP", width=12, command=get_management_ip).pack(side="left", padx=5)
tk.Button(button_frame, text="修改管理IP", width=12, command=modify_management_ip).pack(side="left", padx=5)

tk.Button(button_frame, text="一鍵複製", width=12, command=copy_all_content).pack(side="left", padx=5)


# 啟動
root.mainloop()