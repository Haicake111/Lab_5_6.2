import socket
import struct
import threading
import zlib
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from Crypto.Cipher import AES

class SecureP2PApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AES-GCM P2P Secure Communication")
        self.root.geometry("600x600")

        # Quản lý Key/Nonce cho Server
        self.key_store = {}

        # Giao diện Tab
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        self.setup_receive_tab()
        self.setup_send_tab()

    # ---------------- SERVER (RECEIVER) LOGIC ----------------
    def setup_receive_tab(self):
        self.receive_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.receive_frame, text="NHẬN DỮ LIỆU (SERVER)")

        tk.Label(self.receive_frame, text="Trạng thái Server:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.server_status = tk.Label(self.receive_frame, text="Đang tắt", fg="red")
        self.server_status.pack()

        self.btn_start_server = tk.Button(self.receive_frame, text="BẬT SERVER", command=self.toggle_server, bg="#c8e6c9")
        self.btn_start_server.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(self.receive_frame, wrap=tk.WORD, width=70, height=20)
        self.log_area.pack(padx=10, pady=10)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def toggle_server(self):
        self.btn_start_server.config(state=tk.DISABLED)
        self.server_status.config(text="Đang lắng nghe (Port 5000, 5001)...", fg="green")
        threading.Thread(target=self.start_key_channel, daemon=True).start()
        threading.Thread(target=self.start_data_channel, daemon=True).start()
        self.log("[*] Hệ thống Server đã sẵn sàng.")

    def start_key_channel(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 5001))
        sock.listen(5)
        while True:
            conn, addr = sock.accept()
            config_data = conn.recv(44)
            if len(config_data) == 44:
                self.key_store[addr[0]] = {'key': config_data[:32], 'nonce': config_data[32:]}
                self.log(f"[Key] Nhận khóa mới từ {addr[0]}")
            conn.close()

    def start_data_channel(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 5000))
        sock.listen(5)
        while True:
            conn, addr = sock.accept()
            threading.Thread(target=self.handle_incoming_data, args=(conn, addr), daemon=True).start()

    def handle_incoming_data(self, conn, addr):
        try:
            if addr[0] not in self.key_store:
                self.log(f"[Error] {addr[0]} chưa gửi khóa bảo mật!")
                return

            header = conn.recv(6)
            d_type, c_len, t_len = struct.unpack('!BIB', header)
            tag = conn.recv(t_len)
            
            ciphertext = b""
            while len(ciphertext) < c_len:
                chunk = conn.recv(min(c_len - len(ciphertext), 8192))
                if not chunk: break
                ciphertext += chunk

            conf = self.key_store[addr[0]]
            cipher = AES.new(conf['key'], AES.MODE_GCM, nonce=conf['nonce'])
            decrypted = zlib.decompress(cipher.decrypt_and_verify(ciphertext, tag))

            if d_type == 0:
                self.log(f"[{addr[0]}]: {decrypted.decode('utf-8')}")
            else:
                fname = f"rec_{addr[0].replace('.','_')}_{os.urandom(2).hex()}.dat"
                with open(fname, "wb") as f: f.write(decrypted)
                self.log(f"[File] Đã nhận tệp từ {addr[0]} -> {fname}")

        except Exception as e:
            self.log(f"[Lỗi] Giải mã thất bại: {e}")
        finally:
            conn.close()

    # ---------------- CLIENT (SENDER) LOGIC ----------------
    def setup_send_tab(self):
        self.send_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.send_frame, text="GỬI DỮ LIỆU (CLIENT)")

        tk.Label(self.send_frame, text="IP Máy nhận:").pack(pady=5)
        self.ip_entry = tk.Entry(self.send_frame)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack()

        tk.Label(self.send_frame, text="Nội dung tin nhắn:").pack(pady=5)
        self.msg_text = scrolledtext.ScrolledText(self.send_frame, height=5, width=60)
        self.msg_text.pack(padx=10)
        tk.Button(self.send_frame, text="Gửi Tin Nhắn", command=lambda: self.send_action(0), bg="#e1f5fe").pack(pady=5)

        tk.Label(self.send_frame, text="--- HOẶC ---").pack(pady=10)
        self.target_file = tk.StringVar(value="Chưa chọn file...")
        tk.Label(self.send_frame, textvariable=self.target_file, fg="blue").pack()
        tk.Button(self.send_frame, text="Chọn File", command=self.select_file).pack(pady=5)
        tk.Button(self.send_frame, text="Gửi File", command=lambda: self.send_action(1), bg="#fff9c4").pack(pady=5)

    def select_file(self):
        p = filedialog.askopenfilename()
        if p: self.target_file.set(p)

    def send_action(self, d_type):
        dest_ip = self.ip_entry.get()
        if d_type == 0:
            content = self.msg_text.get("1.0", tk.END).strip().encode('utf-8')
        else:
            if not os.path.exists(self.target_file.get()): return
            with open(self.target_file.get(), "rb") as f: content = f.read()
        
        if not content: return

        try:
            # Trao đổi khóa
            k, n = os.urandom(32), os.urandom(12)
            ks = socket.socket(socket.AF_INET, socket.SOCK_STREAM); ks.connect((dest_ip, 5001))
            ks.sendall(k + n); ks.close()

            # Mã hóa
            comp = zlib.compress(content)
            cp = AES.new(k, AES.MODE_GCM, nonce=n)
            ctx, tag = cp.encrypt_and_digest(comp)

            # Gửi dữ liệu
            ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM); ds.connect((dest_ip, 5000))
            ds.sendall(struct.pack('!BIB', d_type, len(ctx), len(tag)) + tag + ctx); ds.close()
            
            messagebox.showinfo("OK", "Đã gửi thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureP2PApp(root)
    root.mainloop()