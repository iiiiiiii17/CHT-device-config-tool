import sys
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import urllib.request
import subprocess
import shutil
import time
import threading  # 引入執行緒模組

APP_NAME = "設備設定工具"
APP_VERSION = "0.9.0"
VERSION_URL = "https://raw.githubusercontent.com/iiiiiiii17/CHT-device-config-tool/refs/heads/main/version.txt"

# --- 統一路徑處理 ---
if getattr(sys, 'frozen', False):
    BASE_PATH = Path(sys._MEIPASS)
    EXE_DIR = Path(sys.executable).parent
else:
    BASE_PATH = Path(__file__).parent
    EXE_DIR = Path(__file__).parent

file_path = BASE_PATH / "null"

# ------------------ GUI ------------------ #
root = tk.Tk()
root.title(f"{APP_NAME} v{APP_VERSION}")
root.geometry("850x550") # 稍微加高一點放按鈕

# 設定視窗圖示
try:
    icon_path = BASE_PATH / "cht_logo.ico"
    if icon_path.exists():
        root.iconbitmap(str(icon_path))
except Exception as e:
    print(f"無法載入圖示: {e}")

# 選擇檔案區域
choose_file_frame = tk.Frame(root)
choose_file_frame.pack(fill="x", pady=5)
current_file_label = tk.Label(choose_file_frame, text=f"目前檔案: {file_path.name}", anchor="w")
current_file_label.pack(side="left", padx=10)

# 功能按鈕區域
button_frame = tk.Frame(root)
button_frame.pack(fill="x", pady=5)

# 搜尋與輸入區域
frame = tk.Frame(root)
frame.pack(fill="x", pady=5)

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

# 文字顯示區
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("微軟正黑體", 12))
text_area.pack(expand=True, fill='both', padx=10, pady=5)
text_area.config(state=tk.DISABLED)

# 狀態列 (用來顯示更新進度)
status_var = tk.StringVar(value="就緒")
status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# ------------------ 功能函式 ------------------ #

def load_file():
    text_area.config(state=tk.NORMAL)
    text_area.delete('1.0', tk.END)
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                text_area.insert(tk.END, line)
    except FileNotFoundError:
        messagebox.showerror("錯誤", "找不到設備檔案")
    text_area.config(state=tk.DISABLED)

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
    except Exception: pass

def get_management_ip():
    target_prefixes = ["ip address default-management", "ip address inband-default"]
    try:
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip().lower()
                for prefix in target_prefixes:
                    if clean_line.startswith(prefix):
                        parts = line.strip().split()
                        prefix_len = len(prefix.split())
                        if len(parts) >= prefix_len + 2:
                            mgmt_ip_var.set(parts[prefix_len])
                            mask_var.set(parts[prefix_len + 1])
                            return
    except Exception: pass

def modify_all():
    new_ip = mgmt_ip_var.get().strip()
    new_mask = mask_var.get().strip()
    prefix = hostname_prefix_var.get().strip()
    suffix = hostname_suffix_var.get().strip()
    new_hostname = f"{prefix}-{suffix}" if (prefix or suffix) else ""

    if not new_hostname and not new_ip:
        messagebox.showwarning("警告", "請輸入要修改的內容")
        return

    target_prefixes = ["ip address default-management", "ip address inband-default"]
    try:
        lines = []
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                lower_line = stripped.lower()
                # 修改 hostname
                if lower_line.startswith("hostname") and new_hostname:
                    indent = line[:len(line) - len(line.lstrip())]
                    lines.append(f"{indent}hostname {new_hostname}\n")
                    continue
                # 修改 IP
                modified_ip = False
                for p_text in target_prefixes:
                    if lower_line.startswith(p_text) and new_ip:
                        parts = stripped.split()
                        p_len = len(p_text.split())
                        old_mask = parts[p_len + 1] if len(parts) > p_len + 1 else ""
                        mask = new_mask if new_mask else old_mask
                        indent = line[:len(line) - len(line.lstrip())]
                        lines.append(f"{indent}{p_text} {new_ip} {mask}\n")
                        modified_ip = True
                        break
                if not modified_ip:
                    lines.append(line)

        with file_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)
        messagebox.showinfo("成功", "修改完成！")
        load_file()
    except Exception as e:
        messagebox.showerror("錯誤", f"修改失敗: {e}")

def choose_file():
    global file_path
    selected = filedialog.askopenfilename(
        title="選擇設備 Config",
        initialdir=EXE_DIR,
        filetypes=[("Config File", "*.txt"), ("All Files", "*.*")]
    )
    if selected:
        file_path = Path(selected)
        load_file()
        get_hostname()
        get_management_ip()
        current_file_label.config(text=f"目前檔案: {file_path.name}")

def copy_all_content():
    content = text_area.get("1.0", tk.END).strip()
    if content:
        root.clipboard_clear()
        root.clipboard_append(content)
        root.update()
        messagebox.showinfo("成功", "已複製到剪貼簿！")

# ------------------ 更新邏輯 (改為異步按鈕觸發) ------------------ #

def version_tuple(v):
    try:
        clean_v = "".join(c for c in v if c.isdigit() or c == '.')
        return tuple(map(int, clean_v.split(".")))
    except: return (0, 0, 0)

def check_for_update_task():
    """實際在背景跑的更新檢查任務"""
    status_var.set("正在檢查更新...")
    check_update_button.config(state=tk.DISABLED) # 防止重複點擊
    
    target_url = f"{VERSION_URL}?t={int(time.time())}"
    try:
        req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode("utf-8")
            lines = [l.strip() for l in raw_data.splitlines() if l.strip()]
            
        if len(lines) >= 2:
            latest_version = lines[0]
            download_url = lines[1]
            
            if version_tuple(latest_version) > version_tuple(APP_VERSION):
                status_var.set(f"發現新版本: v{latest_version}")
                # 切回主執行緒彈窗
                root.after(0, lambda: prompt_update(latest_version, download_url))
            else:
                status_var.set("目前已是最新版本")
                root.after(0, lambda: messagebox.showinfo("檢查更新", f"目前已是最新版本 (v{APP_VERSION})"))
        else:
            status_var.set("更新伺服器回傳格式錯誤")
    except Exception as e:
        status_var.set("檢查更新失敗")
        root.after(0, lambda: messagebox.showerror("錯誤", f"無法連線至更新伺服器: {e}"))
    finally:
        check_update_button.config(state=tk.NORMAL)

def prompt_update(ver, url):
    if messagebox.askyesno("發現新版本", f"最新版本：{ver}\n是否立即下載並自動覆蓋？"):
        threading.Thread(target=auto_update, args=(url,), daemon=True).start()

def auto_update(download_url):
    try:
        status_var.set("正在下載更新檔...")
        is_frozen = getattr(sys, 'frozen', False)
        current_exe_path = Path(sys.executable if is_frozen else __file__).resolve()
        temp_file = current_exe_path.with_suffix(current_exe_path.suffix + ".tmp")
        
        req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(temp_file, 'wb') as f:
                f.write(response.read())
        
        if is_frozen:
            status_var.set("下載完成，準備重啟...")
            cmd = (
                f'timeout /t 3 /nobreak && '
                f'del /f /q "{current_exe_path}" && '
                f'move /y "{temp_file}" "{current_exe_path}" && '
                f'start "" "{current_exe_path}"'
            )
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            root.after(0, root.destroy)
        else:
            messagebox.showinfo("開發模式", "下載完成 (開發環境不執行覆蓋)")
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("更新失敗", str(e)))

def start_update_thread():
    """按鈕點擊事件"""
    threading.Thread(target=check_for_update_task, daemon=True).start()

# ------------------ 按鈕配置 ------------------ #
choose_file_button = tk.Button(choose_file_frame, text="選擇檔案", command=choose_file, bg="#2196F3", fg="white", font=("微軟正黑體", 10, "bold"))
choose_file_button.pack(side="left", padx=5)

tk.Button(button_frame, text="讀檔(save)", width=12, command=load_file).pack(side="left", padx=5)
tk.Button(button_frame, text="執行修改", width=12, command=modify_all, bg="#4CAF50", fg="white").pack(side="left", padx=5)
tk.Button(button_frame, text="一鍵複製", width=12, command=copy_all_content).pack(side="left", padx=5)

# 放到最右邊或獨立出來的檢查更新按鈕
check_update_button = tk.Button(button_frame, text="檢查更新", width=12, command=start_update_thread)
check_update_button.pack(side="right", padx=10)

# 啟動時清理舊 tmp
def cleanup_tmp():
    try:
        is_frozen = getattr(sys, 'frozen', False)
        curr = Path(sys.executable if is_frozen else __file__).resolve()
        tmp = curr.with_suffix(curr.suffix + ".tmp")
        if tmp.exists(): tmp.unlink()
    except: pass

cleanup_tmp()
root.mainloop()