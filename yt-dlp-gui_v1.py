import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk
import subprocess
import threading
import re
import os  # 確保有 import os

#PROGRESS_BAR_POS = 15 #指定progress_bar位置

# 定義 Format 類別
class Format
    def __init__(self, fmt_id, ext, res, info, is_audio=False)
        self.fmt_id = fmt_id
        self.ext = ext
        self.res = res
        self.info = info
        self.is_audio = is_audio

    @classmethod
    def parse_line(cls, line)
        tokens = line.split()
        if not tokens or not tokens[0].isdigit()
            return None
        if audio in line.lower()
            return cls(tokens[0], tokens[1], ,  .join(tokens[2]), is_audio=True)
        else
            return cls(tokens[0], tokens[1], tokens[2],  .join(tokens[3]), is_audio=False)

    def to_video_tuple(self)
        return (self.fmt_id, self.ext, self.res, self.info)

    def to_audio_tuple(self)
        return (self.fmt_id, self.ext, self.info)

# 選擇下載路徑
def select_download_path()
    folder_selected = filedialog.askdirectory()
    if folder_selected
        download_path.set(folder_selected)

# 列出格式
def list_formats()
    url = url_entry.get()
    if not url
        messagebox.showerror(Error, Please enter a URL)
        return
    try
        result = subprocess.run([yt-dlp, -F, url], capture_output=True, text=True, check=True)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, result.stdout)

        for child in video_treeview.get_children()
            video_treeview.delete(child)
        for child in audio_treeview.get_children()
            audio_treeview.delete(child)

        for line in result.stdout.splitlines()
            fmt_obj = Format.parse_line(line)
            if fmt_obj
                if fmt_obj.is_audio
                    audio_treeview.insert(, tk.END, values=fmt_obj.to_audio_tuple())
                else
                    video_treeview.insert(, tk.END, values=fmt_obj.to_video_tuple())
    except subprocess.CalledProcessError as e
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, e.stderr)

def toggle_selection(event)
    # 當使用者點擊選取的項目時，取消選取；否則正常選取 
    tree = event.widget
    row_id = tree.identify_row(event.y)

    # 若點擊在標頭 (heading) 或空白處，則不處理
    region = tree.identify(region, event.x, event.y)
    if region not in (cell, tree)
        return

    # 若該行已被選取，則取消選取
    if row_id in tree.selection()
        tree.selection_remove(row_id)
        return break


# 設定格式
def set_format_from_selection()
    global video_code, audio_code, video_res
    video_sel = video_treeview.selection()
    audio_sel = audio_treeview.selection()

    video_code = video_treeview.item(video_sel[0])['values'][0] if video_sel else None
    audio_code = audio_treeview.item(audio_sel[0])['values'][0] if audio_sel else None
    video_res = video_treeview.item(video_sel[0])['values'][2] if video_sel else   # 抓取解析度

    if not video_code and not audio_code
        messagebox.showerror(Error, Please select at least one format from the table)
        return

    combined = f{video_code}+{audio_code} if video_code and audio_code else str(video_code or audio_code)
    selected_format_label.config(text=f {combined}, Res {video_res})

def clear_format()
    global video_code, audio_code
    for child in video_treeview.selection()
        video_treeview.selection_remove(child)
    for child in audio_treeview.selection()
        audio_treeview.selection_remove(child)
    video_code = None
    audio_code = None
    video_res = 
    selected_format_label.config(text=none)
    

def download_video()
    url = url_entry.get()
    if not url
        messagebox.showerror(Error, Please enter URL)
        return
    # 檢查是否已選擇格式
    if not video_code and not audio_code
        messagebox.showerror(Error, Please select a format code)
        return

    # 根據選擇建立格式字串
    fmt = f{video_code}+{audio_code} if video_code and audio_code else str(video_code or audio_code)

    output_text.delete(1.0, tk.END)
    progress_bar['value'] = 0
    progress_bar.grid(row=PROGRESS_BAR_POS, column=0, columnspan=3, padx=5, pady=10)
    download_status_label.config(text=Downloading...)
    thread = threading.Thread(target=download_video_thread, args=(url, fmt))
    thread.start()

def download_video_thread(url, fmt)
    import os  # 確保有引入 os 模組
    base_folder = download_path.get()
    prefix = filename_prefix.get().strip()  # 檔名前綴
    res = video_res.strip()  # 解析度

    # 建立檔名模板，僅組合檔案名稱部分
    name_parts = []
    if prefix
        name_parts.append(prefix)
    if res
        name_parts.append(res)
    name_parts.append(%(title)s)
    file_name_template = _.join(name_parts) + .%(ext)s
    
    # 根據是否啟用 uploader 資料夾功能決定完整路徑
    if enable_uploader_folder_var.get()
        final_folder = os.path.join(base_folder, %(uploader)s)
    else
        final_folder = base_folder
    
    filename_template = os.path.join(final_folder, file_name_template)
    #print(Filename template, filename_template)  # 除錯用

    command = [yt-dlp, --newline, -f, fmt, url, -o, filename_template]

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in iter(proc.stdout.readline, )
        if not line
            break
        root.after(0, lambda l=line output_text.insert(tk.END, l))

        if Destination in line
            file_name = line.split(Destination)[1].strip()
            if not file_name.endswith(.part)
                # 更新下載記錄區
                root.after(0, lambda fn=file_name download_record_text.insert(tk.END, fn + n))
                # 更新最終下載路徑 Label
                root.after(0, lambda fn=file_name_template final_download_name_label.config(text=fn))

        m = re.search(r'[download]s+(d+(.d+))%', line)
        if m
            root.after(0, lambda p=float(m.group(1)) progress_bar.config(value=p))

    proc.stdout.close()
    proc.wait()
    root.after(0, lambda download_status_label.config(text=Download Complete))
    root.after(0, lambda progress_bar.config(value=0))
    root.after(0, lambda progress_bar.grid_remove())
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk

# 你原本的各項功能函式與定義...
# 例如：select_download_path, list_formats, toggle_selection, set_format_from_selection, clear_format, download_video, download_video_thread 等

# 建立主 GUI
root = tk.Tk()
root.title(yt-dlp GUI Downloader)
root.geometry(600x720)

# 設定主視窗的 grid 欄與列權重（使整體 layout 可隨視窗調整）
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

# 假設 row 2（Log）、row 3（Table區）及 row 14（下載紀錄區）希望隨視窗擴展
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=2)
root.rowconfigure(14, weight=1)

# === 影片 URL ===
tk.Label(root, text=Video URL).grid(row=0, column=0, padx=5, pady=5, sticky=w)
url_entry = tk.Entry(root, width=42)
url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=w)
url_entry.insert(0, httpswww.youtube.comwatchv=rTKqSmX9XhQ)
list_button = tk.Button(root, text=List Formats, command=list_formats)
list_button.grid(row=0, column=2, padx=5, pady=5, sticky=e)

# === 選擇下載路徑 ===
tk.Label(root, text=Download Path).grid(row=1, column=0, padx=5, pady=5, sticky=w)
download_path = tk.StringVar()
download_path_entry = tk.Entry(root, textvariable=download_path, width=42)
download_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky=w)
download_path_entry.insert(0, rCYT_Videos)
path_button = tk.Button(root, text=Browse, command=select_download_path)
path_button.grid(row=1, column=2, padx=5, pady=5, sticky=e)

# === 格式輸出區 (LOG) ===
output_text = scrolledtext.ScrolledText(root, width=80, height=5)
output_text.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=nsew)

# === 表格區域 (格式選擇) ===
table_frame = tk.Frame(root)
table_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=nsew)
# 設定 table_frame 裡面欄位的擴展性
table_frame.columnconfigure(0, weight=3)
table_frame.columnconfigure(1, weight=2)
# Video Formats 標籤
tk.Label(table_frame, text=Video Formats).grid(row=0, column=0, padx=5, pady=5, sticky=w)

# Video Treeview
video_treeview = ttk.Treeview(table_frame, columns=(ID, Ext, Res, Info), show=headings, selectmode=browse, height=6)
video_treeview.heading(ID, text=ID)
video_treeview.heading(Ext, text=Ext)
video_treeview.heading(Res, text=Res)
video_treeview.heading(Info, text=Info)
video_treeview.column(ID, width=5, anchor=center)
video_treeview.column(Ext, width=5, anchor=center)
video_treeview.column(Res, width=10, anchor=center)
video_treeview.column(Info, width=110, anchor=w)
video_treeview.grid(row=1, column=0, padx=5, pady=5, sticky=nsew)  # 使用 sticky=nsew 讓內容填滿

# Audio Formats 標籤
tk.Label(table_frame, text=Audio Formats).grid(row=0, column=1, padx=5, pady=5, sticky=w)

# Audio Treeview
audio_treeview = ttk.Treeview(table_frame, columns=(ID, Ext, Info), show=headings, selectmode=browse, height=6)
audio_treeview.heading(ID, text=ID)
audio_treeview.heading(Ext, text=Ext)
audio_treeview.heading(Info, text=Info)
audio_treeview.column(ID, width=5, anchor=center)
audio_treeview.column(Ext, width=5, anchor=center)
audio_treeview.column(Info, width=120, anchor=w)
audio_treeview.grid(row=1, column=1, padx=5, pady=5, sticky=nsew)  # 與 video_treeview 同行且填滿空間

# 讓 Treeview 支援「點擊已選取的項目取消選取」
video_treeview.bind(Button-1, toggle_selection)
audio_treeview.bind(Button-1, toggle_selection)

# === frame_row7 ===
frame_row7 = tk.Frame(root)
frame_row7.grid(row=7, column=0, columnspan=2, sticky=nsew, padx=10, pady=10)
frame_row7.columnconfigure(0, weight=1)
frame_row7.columnconfigure(1, weight=1)
# === 選擇格式按鈕 ===
set_format_button = tk.Button(frame_row7, text=Set Format, command=set_format_from_selection)
set_format_button.grid(row=0, column=0, padx=5, pady=5, sticky=nsew)
clear_button = tk.Button(frame_row7, text=Clear, command=clear_format)
clear_button.grid(row=0, column=1, padx=5, pady=5, sticky=nsew)

# === 顯示選取的格式 ===
frame_row8 = tk.Frame(root)
frame_row8.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky=nsew)
frame_row8.columnconfigure(0, weight=1)
frame_row8.columnconfigure(1, weight=1)
selected_format0_label = tk.Label(frame_row8, text=Selected Format , font=(Arial, 12))
selected_format0_label.grid(row=0, column=0, padx=5, pady=5, sticky=e)
selected_format_label = tk.Label(frame_row8, text= none, font=(Arial, 12))
selected_format_label.grid(row=0, column=1, padx=5, pady=5, sticky=w)

# === 使用 Frame 獨立管理這部分的欄位 ===
frame = tk.Frame(root)
frame.grid(row=9, column=0, columnspan=4, sticky=nsew, padx=10, pady=10)
frame.columnconfigure(0, weight=1)  # Label
frame.columnconfigure(1, weight=2)  # Entry
frame.columnconfigure(2, weight=1)  # Checkbutton
frame.columnconfigure(3, weight=1)  # Button

# === Filename Prefix ===
tk.Label(frame, text=Filename Prefix).grid(row=0, column=0, padx=5, pady=5, sticky=e)
filename_prefix = tk.StringVar(value=)
filename_entry = tk.Entry(frame, textvariable=filename_prefix, width=15)
filename_entry.grid(row=0, column=1, padx=5, pady=5, sticky=w)

# === Checkbutton ===
enable_uploader_folder_var = tk.IntVar(value=1)
enable_uploader_folder_checkbutton = tk.Checkbutton(frame, text=new a folder for uploader, variable=enable_uploader_folder_var)
enable_uploader_folder_checkbutton.grid(row=0, column=2, padx=5, pady=5, sticky=w)

# === 下載按鈕 ===
download_button = tk.Button(frame, text=Download, command=download_video)
download_button.grid(row=0, column=3, padx=5, pady=5, sticky=e)

# === 下載狀態 ===
download_status_label = tk.Label(root, text=Download Status Idle, font=(Arial, 12))
download_status_label.grid(row=11, column=0, columnspan=3, padx=5, pady=5)

# === 最終下載路徑 Label ===
tk.Label(root, text=Last Final Download file name).grid(row=12, column=0, padx=5, pady=5, sticky=w)
final_download_name_label = tk.Label(root, text=, font=(Arial, 10))
final_download_name_label.grid(row=12, column=1, columnspan=2, padx=5, pady=5, sticky=w)

# === 下載紀錄區 ===
tk.Label(root, text=Download Record, font=(Arial, 9)).grid(row=13, column=0, padx=5, pady=5, sticky=w)
download_record_text = scrolledtext.ScrolledText(root, width=80, height=5)
download_record_text.grid(row=14, column=0, columnspan=3, padx=5, pady=5, sticky=nsew)

# === 進度條 (初始隱藏) ===
# 假設你有一個全域常數 PROGRESS_BAR_POS = 15
PROGRESS_BAR_POS = 15
progress_bar = ttk.Progressbar(root, orient=horizontal, length=590, mode=determinate)
progress_bar.grid(row=PROGRESS_BAR_POS, column=0, columnspan=3, padx=5, pady=10, sticky=ew)
progress_bar.grid_remove()

root.mainloop()