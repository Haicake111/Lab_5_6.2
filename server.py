import socket
import struct
import threading
import zlib
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from Crypto.Cipher import AES
import platform

# --- CẤU HÌNH GIAO DIỆN CHUNG ---
ctk.set_appearance_mode("Dark")  # Ép buộc dùng chế độ tối
ctk.set_default_color_theme("blue")  # Chủ đề màu xanh

class SecureP2PApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ chính
        self.title("SECURE P2P - Advanced Encryption Communication")
        self.geometry("1100x650")
        
        # Đặt icon cho ứng dụng (nếu có file .ico)
        # if platform.system() == "Windows":
        #     self.iconbitmap("icon.ico")

        # Quản lý Key cho Server
        self.key_store = {}

        # Trạng thái Server (dùng để cập nhật GUI)
        self.server_running = False

        # --- CẤU HÌNH LƯỚI CHÍNH (GRID) ---
        self.grid_columnconfigure(1, weight=1)  # Cột nội dung chính giãn nở
        self.grid_rowconfigure(0, weight=1)    # Hàng chính giãn nở hoàn toàn

        # ---------------- SIDEBAR (THANH BÊN) ----------------
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1a1c24")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Khoảng trống co giãn

        # Logo/Tiêu đề chính
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SECURE P2P", 
                                      font=ctk.CTkFont(size=22, weight="bold"), text_color="#3b8ed0")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # Mục MENU
        self.menu_label = ctk.CTkLabel(self.sidebar_frame, text="🛡️ GIAO DIỆN", 
                                      font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="gray")
        self.menu_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.btn_receive_tab = ctk.CTkButton(self.sidebar_frame, text="Nhận Dữ Liệu", 
                                            fg_color="transparent", text_color="#ffffff", border_width=0,
                                            hover_color="#2c2f3c", anchor="w",
                                            command=self.show_receive_frame)
        self.btn_receive_tab.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.btn_send_tab = ctk.CTkButton(self.sidebar_frame, text="Gửi Dữ Liệu", 
                                         fg_color="transparent", text_color="#ffffff", border_width=0,
                                         hover_color="#2c2f3c", anchor="w",
                                         command=self.show_send_frame)
        self.btn_send_tab.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Mục CẤU HÌNH
        self.config_label = ctk.CTkLabel(self.sidebar_frame, text="⚙️ CẤU HÌNH", 
                                       font=ctk.CTkFont(size=14, weight="bold"), anchor="w", text_color="gray")
        self.config_label.grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")

        self.btn_key_mgr = ctk.CTkButton(self.sidebar_frame, text="Quản lý Khóa", 
                                        fg_color="transparent", text_color="#ffffff", anchor="w", hover_color="#2c2f3c")
        self.btn_key_mgr.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        self.btn_history = ctk.CTkButton(self.sidebar_frame, text="Lịch sử", 
                                       fg_color="transparent", text_color="#ffffff", anchor="w", hover_color="#2c2f3c")
        self.btn_history.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

        # Dòng trạng thái nhỏ ở cuối sidebar
        self.port_status_label = ctk.CTkLabel(self.sidebar_frame, text="🖥️ Server: Port 5000, 5001 🔒", 
                                             font=ctk.CTkFont(size=11), text_color="gray")
        self.port_status_label.grid(row=9, column=0, pady=20)


        # ---------------- MAIN CONTENT AREA (VÙNG NỘI DUNG CHÍNH) ----------------
        self.main_label = ctk.CTkLabel(self, text="Hệ thống P2P An Toàn", font=ctk.CTkFont(size=24, weight="bold"))
        self.main_label.grid(row=0, column=1, padx=30, pady=(30, 10), sticky="nw")

        # Container chứa các "view" khác nhau (Nhận/Gửi)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, padx=30, pady=(80, 30), sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Khởi tạo các View
        self.setup_receive_view()
        self.setup_send_view()

        # Mặc định hiện tab Nhận
        self.show_receive_frame()

    # ================= VIEW 1: RECEIVE (NHẬN DỮ LIỆU) =================
    def setup_receive_view(self):
        self.receive_view = ctk.CTkFrame(self.container, fg_color="#1e2129", corner_radius=15, border_width=1, border_color="#2c2f3c")
        
        # Tiêu đề View
        header_frame = ctk.CTkFrame(self.receive_view, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="NHẬN DỮ LIỆU (SERVER)", 
                     font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(side="left")

        self.server_status_badge = ctk.CTkLabel(header_frame, text="OFFLINE", 
                                                fg_color="#e74c3c", text_color="white", 
                                                corner_radius=20, width=80, font=ctk.CTkFont(size=11, weight="bold"))
        self.server_status_badge.pack(side="right", padx=10)

        # Thanh điều khiển Server
        control_frame = ctk.CTkFrame(self.receive_view, fg_color="transparent")
        control_frame.pack(fill="x", padx=25, pady=10)

        self.btn_toggle_server = ctk.CTkButton(control_frame, text="KHỞI CHẠY SERVER", 
                                               fg_color="#2ecc71", hover_color="#27ae60",
                                               font=ctk.CTkFont(weight="bold"),
                                               command=self.toggle_server_action)
        self.btn_toggle_server.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_stop_server = ctk.CTkButton(control_frame, text="DỪNG SERVER", 
                                              fg_color="#e74c3c", hover_color="#c0392b",
                                              font=ctk.CTkFont(weight="bold"), state="disabled",
                                              command=self.toggle_server_action)
        self.btn_stop_server.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Khu vực Log
        ctk.CTkLabel(self.receive_view, text="Nhật ký hoạt động:", 
                     font=ctk.CTkFont(size=13), text_color="gray", anchor="w").pack(fill="x", padx=25, pady=(15, 5))

        self.log_area = ctk.CTkTextbox(self.receive_view, fg_color="#14161b", 
                                       text_color="#2ecc71", # Màu xanh lá cây kiểu hacker
                                       font=ctk.CTkFont(family="Consolas", size=12), 
                                       corner_radius=10, border_width=1, border_color="#2c2f3c")
        self.log_area.pack(padx=25, pady=(0, 25), fill="both", expand=True)

    # ================= VIEW 2: SEND (GỬI DỮ LIỆU) =================
    def setup_send_view(self):
        self.send_view = ctk.CTkFrame(self.container, fg_color="#1e2129", corner_radius=15, border_width=1, border_color="#2c2f3c")
        
        # Tiêu đề View
        ctk.CTkLabel(self.send_view, text="GỬI DỮ LIỆU ĐẾN PEER (CLIENT)", 
                     font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", padx=25, pady=(20, 20))

        # --- Khu vực nhập IP ---
        ip_frame = ctk.CTkFrame(self.send_view, fg_color="transparent")
        ip_frame.pack(fill="x", padx=25, pady=10)
        
        ctk.CTkLabel(ip_frame, text="Địa chỉ IP máy nhận:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.ip_entry = ctk.CTkEntry(ip_frame, placeholder_text="Ví dụ: 192.168.1.50", 
                                     height=40, fg_color="#14161b", border_color="#2c2f3c")
        self.ip_entry.pack(fill="x")

        # --- Khu vực Tin nhắn ---
        msg_frame = ctk.CTkFrame(self.send_view, fg_color="transparent")
        msg_frame.pack(fill="x", padx=25, pady=15)

        ctk.CTkLabel(msg_frame, text="Nội dung tin nhắn văn bản:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.msg_text = ctk.CTkTextbox(msg_frame, height=120, fg_color="#14161b", border_width=1, border_color="#2c2f3c")
        self.msg_text.pack(fill="x", pady=(0, 10))
        
        self.btn_send_msg = ctk.CTkButton(msg_frame, text="Gửi Tin Nhắn Mã Hóa", 
                                         fg_color="#3b8ed0", hover_color="#2c7dc0",
                                         font=ctk.CTkFont(weight="bold"), height=40,
                                         command=lambda: self.send_action(0))
        self.btn_send_msg.pack(fill="x")

        # Phân cách
        ctk.CTkLabel(self.send_view, text="──────── HOẶC GỬI TỆP TIN ────────", 
                     text_color="gray", font=ctk.CTkFont(size=12)).pack(pady=20)

        # --- Khu vực Tệp tin ---
        file_frame = ctk.CTkFrame(self.send_view, fg_color="#14161b", corner_radius=10, border_width=1, border_color="#2c2f3c")
        file_frame.pack(fill="x", padx=25, pady=(0, 25))

        file_controls = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_controls.pack(fill="x", padx=15, pady=15)

        self.btn_select_file = ctk.CTkButton(file_controls, text="Chọn Tệp Tin...", 
                                             fg_color="#2c2f3c", hover_color="#3a3e4d",
                                             text_color="white", font=ctk.CTkFont(size=12),
                                             width=120,
                                             command=self.select_file_action)
        self.btn_select_file.pack(side="left")

        self.target_file_label = ctk.CTkLabel(file_controls, text="Chưa chọn tệp nào.", 
                                               text_color="gray", anchor="w", font=ctk.CTkFont(size=12))
        self.target_file_label.pack(side="left", padx=15, fill="x", expand=True)

        self.btn_send_file = ctk.CTkButton(file_frame, text="Gửi Tệp Tin Đã Chọn (AES-GCM)", 
                                           fg_color="#8e44ad", hover_color="#732d91",
                                           font=ctk.CTkFont(weight="bold"), height=40,
                                           state="disabled", # Khóa đến khi chọn file
                                           command=lambda: self.send_action(1))
        self.btn_send_file.pack(fill="x", padx=15, pady=(0, 15))


    # ================= LOGIC ĐIỀU HƯỚNG CÁC VIEW =================
    def show_receive_frame(self):
        # Cập nhật màu nút sidebar
        self.btn_receive_tab.configure(fg_color="#3b8ed0", text_color="white", font=ctk.CTkFont(weight="bold"))
        self.btn_send_tab.configure(fg_color="transparent", text_color="#ffffff", font=ctk.CTkFont(weight="normal"))
        
        # Chuyển đổi view
        self.send_view.grid_forget()
        self.receive_view.grid(row=0, column=0, sticky="nsew")
        self.main_label.configure(text="Quản lý Nhận Dữ Liệu")

    def show_send_frame(self):
        # Cập nhật màu nút sidebar
        self.btn_send_tab.configure(fg_color="#3b8ed0", text_color="white", font=ctk.CTkFont(weight="bold"))
        self.btn_receive_tab.configure(fg_color="transparent", text_color="#ffffff", font=ctk.CTkFont(weight="normal"))
        
        # Chuyển đổi view
        self.receive_view.grid_forget()
        self.send_view.grid(row=0, column=0, sticky="nsew")
        self.main_label.configure(text="Bảng Gửi Dữ Liệu")


    # ================= LOGIC XỬ LÝ (MẠNG & MÃ HÓA) =================
    # --- Phần SERVER (RECEIVER) ---
    def log(self, message):
        self.log_area.insert("end", f"> {message}\n")
        self.log_area.see("end")

    def toggle_server_action(self):
        # Logic này chỉ mang tính demo bật tắt giao diện, cần tích hợp code mạng cũ vào đây
        if not self.server_running:
            # Bật Server
            self.server_running = True
            self.btn_toggle_server.configure(state="disabled", text="SERVER ĐANG HOẠT ĐỘNG...")
            self.btn_stop_server.configure(state="normal")
            self.server_status_badge.configure(text="ONLINE", fg_color="#2ecc71")
            
            # Khởi chạy các luồng nền (Thread)
            threading.Thread(target=self.start_key_channel, daemon=True).start()
            threading.Thread(target=self.start_data_channel, daemon=True).start()
            
            self.log("--- Bắt đầu lắng nghe TCP Port 5000 (Data) & 5001 (Key) ---")
            self.log("Hệ thống mã hóa AES-GCM đã sẵn sàng.")
        else:
            # Dừng Server (Để đơn giản, demo này không tắt thread, chỉ cập nhật GUI)
            self.server_running = False
            self.btn_toggle_server.configure(state="normal", text="KHỞI CHẠY SERVER")
            self.btn_stop_server.configure(state="disabled")
            self.server_status_badge.configure(text="OFFLINE", fg_color="#e74c3c")
            self.log("--- Đã dừng yêu cầu lắng nghe Server ---")

    # (Giữ nguyên logic start_key_channel, start_data_channel, handle_incoming_data từ code cũ của bạn)
    def start_key_channel(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Tránh lỗi Port busy
            sock.bind(('0.0.0.0', 5001))
            sock.listen(5)
            while self.server_running:
                conn, addr = sock.accept()
                config_data = conn.recv(44)
                if len(config_data) == 44:
                    self.key_store[addr[0]] = {'key': config_data[:32], 'nonce': config_data[32:]}
                    self.log(f"🔑 Đã nhận Key & Nonce bảo mật từ: {addr[0]}")
                conn.close()
            sock.close()
        except Exception as e:
            if self.server_running: self.log(f"Lỗi Key Channel: {e}")

    def start_data_channel(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', 5000))
            sock.listen(5)
            while self.server_running:
                conn, addr = sock.accept()
                threading.Thread(target=self.handle_incoming_data, args=(conn, addr), daemon=True).start()
            sock.close()
        except Exception as e:
            if self.server_running: self.log(f"Lỗi Data Channel: {e}")

    def handle_incoming_data(self, conn, addr):
        try:
            if addr[0] not in self.key_store:
                self.log(f"⚠️ Từ chối kết nối từ {addr[0]}: Chưa trao đổi khóa!")
                return

            self.log(f"📩 Đang nhận dữ liệu mã hóa từ {addr[0]}...")
            header = conn.recv(6)
            if not header: return
            d_type, c_len, t_len = struct.unpack('!BIB', header)
            
            tag = conn.recv(t_len)
            ciphertext = b""
            while len(ciphertext) < c_len:
                chunk = conn.recv(min(c_len - len(ciphertext), 8192))
                if not chunk: break
                ciphertext += chunk

            # Giải mã AES-GCM
            conf = self.key_store[addr[0]]
            cipher = AES.new(conf['key'], AES.MODE_GCM, nonce=conf['nonce'])
            decrypted = zlib.decompress(cipher.decrypt_and_verify(ciphertext, tag))

            if d_type == 0:
                self.log(f"💬 TIN NHẮN TỪ [{addr[0]}]: {decrypted.decode('utf-8')}")
            else:
                fname = f"rec_{addr[0].replace('.','_')}_{os.urandom(2).hex()}.dat"
                with open(fname, "wb") as f: f.write(decrypted)
                self.log(f"📁 Đã nhận TỆP TIN từ {addr[0]}, lưu thành: {fname}")

        except Exception as e:
            self.log(f"🛑 Lỗi giải mã/xử lý từ {addr[0]}: {e}")
        finally:
            conn.close()


    # --- Phần CLIENT (SENDER) ---
    def select_file_action(self):
        p = filedialog.askopenfilename()
        if p:
            self.target_file_path = p
            filename = os.path.basename(p)
            self.target_file_label.configure(text=filename, text_color="#3b8ed0")
            self.btn_send_file.configure(state="normal") # Bật nút gửi file

    def send_action(self, d_type):
        dest_ip = self.ip_entry.get().strip()
        if not dest_ip:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập IP máy nhận!")
            return

        # Chuẩn bị nội dung
        if d_type == 0:
            msg_content = self.msg_text.get("1.0", "end-1c").strip()
            if not msg_content: return
            content = msg_content.encode('utf-8')
        else:
            if not hasattr(self, 'target_file_path') or not self.target_file_path: return
            try:
                with open(self.target_file_path, "rb") as f: content = f.read()
            except Exception as e:
                messagebox.showerror("Lỗi tệp", f"Không thể đọc tệp: {e}")
                return
        
        if not content: return

        # Tạo luồng gửi để không làm đơ giao diện
        self.btn_send_msg.configure(state="disabled", text="Đang gửi...")
        self.btn_send_file.configure(state="disabled")
        threading.Thread(target=self.threaded_send, args=(dest_ip, d_type, content), daemon=True).start()

    def threaded_send(self, dest_ip, d_type, content):
        success = False
        error_msg = ""
        try:
            # 1. Tạo và gửi khóa (Key Exchange)
            k, n = os.urandom(32), os.urandom(12)
            ks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ks.settimeout(5) # Timeout tránh đơ
            ks.connect((dest_ip, 5001))
            ks.sendall(k + n)
            ks.close()

            # 2. Nén và Mã hóa AES-GCM
            comp = zlib.compress(content)
            cp = AES.new(k, AES.MODE_GCM, nonce=n)
            ctx, tag = cp.encrypt_and_digest(comp)

            # 3. Gửi dữ liệu mã hóa
            ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ds.connect((dest_ip, 5000))
            # Header: Type(1B), CipherLen(4B), TagLen(1B)
            ds.sendall(struct.pack('!BIB', d_type, len(ctx), len(tag)) + tag + ctx)
            ds.close()
            success = True
        except socket.timeout:
            error_msg = "Kết nối đến máy nhận bị quá thời gian (Timeout). IP đúng không?"
        except Exception as e:
            error_msg = str(e)

        # Cập nhật GUI về luồng chính
        self.after(0, lambda: self.send_finished_gui_update(success, error_msg))

    def send_finished_gui_update(self, success, error_msg):
        self.btn_send_msg.configure(state="normal", text="Gửi Tin Nhắn Mã Hóa")
        if hasattr(self, 'target_file_path'): self.btn_send_file.configure(state="normal")
        
        if success:
            messagebox.showinfo("Thành công", "Dữ liệu đã được gửi và mã hóa an toàn đến Peer!")
            self.msg_text.delete("1.0", "end") # Xóa tin nhắn cũ
        else:
            messagebox.showerror("Lỗi kết nối/mạng", f"Không thể gửi dữ liệu:\n{error_msg}")

if __name__ == "__main__":
    app = SecureP2PApp()
    app.mainloop()