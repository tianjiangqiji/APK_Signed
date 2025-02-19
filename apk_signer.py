import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys


class APKSignerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("APK 签名工具")

        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.create_verify_section()
        self.create_sign_section()

    def create_verify_section(self):
        frame = ttk.LabelFrame(self.root, text="验证签名")
        frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(frame, text="选择APK", command=self.select_verify_apk).grid(row=0, column=0, padx=5)
        self.verify_apk_path = tk.StringVar()
        ttk.Entry(frame, textvariable=self.verify_apk_path, width=50).grid(row=0, column=1, padx=5)

        ttk.Button(frame, text="验证签名", command=self.verify_apk).grid(row=1, column=0, columnspan=2, pady=5)

        self.verify_result = tk.Text(frame, height=8, width=60)
        self.verify_result.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def create_sign_section(self):
        frame = ttk.LabelFrame(self.root, text="签名APK")
        frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(frame, text="选择签名文件", command=self.select_keystore).grid(row=0, column=0, padx=5)
        self.keystore_path = tk.StringVar()
        ttk.Entry(frame, textvariable=self.keystore_path, width=50).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Alias:").grid(row=1, column=0)
        self.alias = ttk.Entry(frame)
        self.alias.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(frame, text="Keystore密码:").grid(row=2, column=0)
        self.ks_pass = ttk.Entry(frame, show="*")
        self.ks_pass.grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(frame, text="Key密码:").grid(row=3, column=0)
        self.key_pass = ttk.Entry(frame, show="*")
        self.key_pass.grid(row=3, column=1, sticky="w", padx=5)

        ttk.Button(frame, text="选择待签名APK", command=self.select_input_apk).grid(row=4, column=0, padx=5)
        self.input_apk_path = tk.StringVar()
        ttk.Entry(frame, textvariable=self.input_apk_path, width=50).grid(row=4, column=1, padx=5)

        ttk.Button(frame, text="选择输出路径", command=self.select_output_path).grid(row=5, column=0, padx=5)
        self.output_path = tk.StringVar()
        ttk.Entry(frame, textvariable=self.output_path, width=50).grid(row=5, column=1, padx=5)

        ttk.Button(frame, text="开始签名", command=self.sign_apk).grid(row=6, column=0, columnspan=2, pady=5)

        self.sign_result = tk.Text(frame, height=8, width=60)
        self.sign_result.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def select_verify_apk(self):
        path = filedialog.askopenfilename(filetypes=[("APK files", "*.apk")])
        self.verify_apk_path.set(path)

    def select_keystore(self):
        path = filedialog.askopenfilename(filetypes=[("Keystore files", "*.keystore *.jks")])
        self.keystore_path.set(path)

    def select_input_apk(self):
        path = filedialog.askopenfilename(filetypes=[("APK files", "*.apk")])
        self.input_apk_path.set(path)

    def select_output_path(self):
        path = filedialog.asksaveasfilename(defaultextension=".apk", filetypes=[("APK files", "*.apk")])
        self.output_path.set(path)

    def verify_apk(self):
        apk_path = self.verify_apk_path.get()
        if not apk_path:
            messagebox.showerror("错误", "请先选择APK文件")
            return

        apksigner = os.path.join(self.base_dir, "apksigner.jar")
        cmd = f'java -jar "{apksigner}" verify -v "{apk_path}"'

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            self.verify_result.delete(1.0, tk.END)
            self.verify_result.insert(tk.END, result.stdout)
        except subprocess.CalledProcessError as e:
            self.verify_result.delete(1.0, tk.END)
            self.verify_result.insert(tk.END, f"错误:\n{e.stderr}")

    def sign_apk(self):
        required_fields = [
            (self.keystore_path.get(), "请选择签名文件"),
            (self.alias.get(), "请输入Alias"),
            (self.ks_pass.get(), "请输入Keystore密码"),
            (self.input_apk_path.get(), "请选择待签名APK"),
            (self.output_path.get(), "请选择输出路径")
        ]

        for field, msg in required_fields:
            if not field:
                messagebox.showerror("错误", msg)
                return

        apksigner = os.path.join(self.base_dir, "apksigner.jar")
        cmd = [
            'java', '-jar', apksigner, 'sign',
            '--ks', self.keystore_path.get(),
            '--ks-key-alias', self.alias.get(),
            '--ks-pass', f'pass:{self.ks_pass.get()}',
            '--key-pass', f'pass:{self.key_pass.get()}',
            '--out', self.output_path.get(),
            self.input_apk_path.get()
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            self.sign_result.delete(1.0, tk.END)
            self.sign_result.insert(tk.END, "签名成功！\n")
            self.sign_result.insert(tk.END, result.stdout)
        except subprocess.CalledProcessError as e:
            self.sign_result.delete(1.0, tk.END)
            self.sign_result.insert(tk.END, f"签名失败:\n{e.stderr}")


if __name__ == "__main__":
    root = tk.Tk()
    app = APKSignerApp(root)
    root.mainloop()