# AES-128 CBC Encryption & Secure Communication Tool (Lab 5 & 6.2)

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
SV thực hiện:
    Nông Ngôn Hải MSV:1871020212
    Lã Đức Minh MSV:1871020401
Dự án này triển khai thuật toán mã hóa đối xứng **AES-128** ở chế độ **CBC (Cipher Block Chaining)**, kết hợp giao diện đồ họa (GUI) hiện đại và khả năng truyền nhận dữ liệu bảo mật qua Socket TCP giữa hai máy tính trong mạng LAN.

## 🚀 Tính năng chính

* **Mật mã học (Nội dung Lab 5):**
    * Thực thi thuật toán **AES-128** (Khóa 16 byte).
    * Chế độ hoạt động **CBC** giúp tăng cường bảo mật bằng cách XOR khối bản rõ với bản mã của khối trước đó.
    * Công thức mã hóa: $C_{0}=AES\_Encrypt(P_{0}\oplus IV)$ và $C_{i}=AES\_Encrypt(P_{i}\oplus C_{i-1})$.
    * Cơ chế đệm dữ liệu **PKCS#7 Padding**.
* **Truyền tin qua Socket (Nội dung Lab 6.2):**
    * Kiến trúc **P2P (Peer-to-Peer)**: Một ứng dụng đóng vai trò cả Client (Gửi) và Server (Nhận).
    * **Kênh đôi (Dual-channel):** Tách biệt Port 5001 (Trao đổi Khóa/IV) và Port 5000 (Truyền Dữ liệu mã hóa).
    * Tích hợp nén dữ liệu **zlib** để tối ưu dung lượng truyền tải.
    * Hỗ trợ truyền cả tin nhắn văn bản và tệp tin.

## 🛠 Thông số kỹ thuật

| Tham số | Giá trị cấu hình |
| :--- | :--- |
| **Địa chỉ IP Server** | `10.139.123.174` (IPv4 thực tế) |
| **Cổng dữ liệu (Data Port)** | `5000` |
| **Cổng khóa (Key Port)** | `5001` |
| **Thuật toán mã hóa** | `AES-128-CBC` |
| **Cơ chế đệm** | `PKCS#7` |
| **Độ dài IV** | `16 bytes` (Random per session) |
