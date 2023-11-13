import os
import requests
import threading
from urllib.parse import urlparse
from tkinter import filedialog, Text, Button, Toplevel, Tk, ttk, Entry, StringVar, Label, messagebox
import re
import mimetypes
import errno

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("下载器")

        self.download_path = StringVar()

        self.path_label = Label(master, text="下载路径：")
        self.path_label.grid(row=0, column=0)

        self.path_entry = Entry(master, textvariable=self.download_path, width=50)
        self.path_entry.grid(row=0, column=1)

        self.path_button = Button(master, text="选择路径", command=self.choose_path)
        self.path_button.grid(row=0, column=2)

        self.input_label = Label(master, text="输入链接：")
        self.input_label.grid(row=1, column=0)

        self.input_text = Text(master, width=60, height=10)
        self.input_text.grid(row=1, column=1, columnspan=2)

        self.start_button = Button(master, text="开始", command=self.start_download)
        self.start_button.grid(row=2, column=0)

        # self.pause_button = Button(master, text="暂停", command=self.pause_download)
        # self.pause_button.grid(row=2, column=1)
        #
        # self.stop_button = Button(master, text="停止", command=self.stop_download)
        # self.stop_button.grid(row=2, column=2)

        self.progress_label = Label(master, text="下载进度：")
        self.progress_label.grid(row=3, column=0)

        self.progress = ttk.Progressbar(master, length=200)
        self.progress.grid(row=3, column=1, columnspan=2)

    def choose_path(self):
        self.download_path.set(filedialog.askdirectory())

    def start_download(self):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', self.input_text.get(1.0, "end"))
        for url in urls:
            threading.Thread(target=self.download_file, args=(url, self.download_path.get())).start()

    def pause_download(self):
        # 未实现
        pass

    def stop_download(self):
        # 未实现
        pass

    def download_file(self, url, download_dir):
        path = urlparse(url).path
        filename = os.path.basename(path)
        if filename == "":
            response = requests.head(url)
            if 'Content-Type' in response.headers:
                content_type = response.headers['Content-Type']
                ext = mimetypes.guess_extension(content_type)
                filename = "downloaded_file" + (ext if ext else "")
        file_path = os.path.join(download_dir, filename)
        if os.path.exists(file_path):
            if not messagebox.askyesno("文件已存在~", f"文件 '{filename}' 已存在，链接：'{url}'。是否替换？"):
                return
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    print(f"Failed to create directory due to {str(exc)}~")
                    return
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content_length', 0))
            block_size = 1024
            with open(file_path, 'wb') as f:
                for data in r.iter_content(block_size):
                    f.write(data)
                    self.progress['value'] += len(data)
                self.progress['maximum'] = total_size

root = Tk()
app = App(root)
root.mainloop()
