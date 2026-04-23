import customtkinter as ctk
import zlib
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Cấu hình giao diện
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AESApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AES-128 CBC Tool - Lab 5")
        self.geometry("700x550")

        # Tạo Tabview để tách biệt Mã hóa và Giải mã
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tabview.add("Mã hóa (Encrypt)")
        self.tabview.add("Giải mã (Decrypt)")

        self.setup_encrypt_tab()
        self.setup_decrypt_tab()

    def setup_encrypt_tab(self):
        # --- Giao diện Tab Mã hóa ---
        tab = self.tabview.tab("Mã hóa (Encrypt)")

        ctk.CTkLabel(tab, text="Văn bản gốc (Plaintext):").pack(pady=5)
        self.enc_input = ctk.CTkTextbox(tab, height=100, width=500)
        self.enc_input.pack(pady=5)

        self.btn_encrypt = ctk.CTkButton(tab, text="Thực hiện Mã hóa", command=self.encrypt_action)
        self.btn_encrypt.pack(pady=10)

        ctk.CTkLabel(tab, text="Kết quả (Key | IV | Ciphertext):").pack(pady=5)
        self.enc_output = ctk.CTkTextbox(tab, height=150, width=500)
        self.enc_output.pack(pady=5)

    def setup_decrypt_tab(self):
        # --- Giao diện Tab Giải mã ---
        tab = self.tabview.tab("Giải mã (Decrypt)")

        ctk.CTkLabel(tab, text="Nhập Key (Hex):").pack(pady=2)
        self.dec_key = ctk.CTkEntry(tab, width=500)
        self.dec_key.pack(pady=2)

        ctk.CTkLabel(tab, text="Nhập IV (Hex):").pack(pady=2)
        self.dec_iv = ctk.CTkEntry(tab, width=500)
        self.dec_iv.pack(pady=2)

        ctk.CTkLabel(tab, text="Nhập Ciphertext (Hex):").pack(pady=2)
        self.dec_input = ctk.CTkTextbox(tab, height=80, width=500)
        self.dec_input.pack(pady=2)

        self.btn_decrypt = ctk.CTkButton(tab, text="Thực hiện Giải mã", command=self.decrypt_action, fg_color="green")
        self.btn_decrypt.pack(pady=10)

        ctk.CTkLabel(tab, text="Văn bản đã giải mã:").pack(pady=2)
        self.dec_output = ctk.CTkTextbox(tab, height=80, width=500)
        self.dec_output.pack(pady=2)

    def encrypt_action(self):
        try:
            plaintext = self.enc_input.get("1.0", "end-1c").encode('utf-8')
            if not plaintext: return

            # Sinh Key/IV ngẫu nhiên
            key = get_random_bytes(16)
            iv = get_random_bytes(16)

            # Nén, Padding và Mã hóa
            compressed = zlib.compress(plaintext)
            padded = pad(compressed, AES.block_size)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            ciphertext = cipher.encrypt(padded)

            # Hiển thị kết quả
            result = (f"KEY: {binascii.hexlify(key).decode()}\n\n"
                      f"IV : {binascii.hexlify(iv).decode()}\n\n"
                      f"CIPHERTEXT: {binascii.hexlify(ciphertext).decode()}")
            
            self.enc_output.delete("1.0", "end")
            self.enc_output.insert("1.0", result)
        except Exception as e:
            self.show_error(f"Lỗi mã hóa: {e}")

    def decrypt_action(self):
        try:
            # Lấy dữ liệu từ giao diện
            key = binascii.unhexlify(self.dec_key.get().strip())
            iv = binascii.unhexlify(self.dec_iv.get().strip())
            ciphertext = binascii.unhexlify(self.dec_input.get("1.0", "end-1c").strip())

            # Giải mã, Gỡ padding và Giải nén
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_padded = cipher.decrypt(ciphertext)
            decrypted_compressed = unpad(decrypted_padded, AES.block_size)
            final_data = zlib.decompress(decrypted_compressed)

            self.dec_output.delete("1.0", "end")
            self.dec_output.insert("1.0", final_data.decode('utf-8'))
        except Exception as e:
            self.show_error(f"Lỗi giải mã: {e}\nVui lòng kiểm tra lại Key/IV hoặc bản mã.")

    def show_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Lỗi")
        ctk.CTkLabel(error_window, text=message, padx=20, pady=20).pack()

if __name__ == "__main__":
    app = AESApp()
    app.mainloop()