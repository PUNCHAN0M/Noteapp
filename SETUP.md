# PSUNote Application

แอปพลิเคชันโน้ตง่าย ๆ ที่ใช้ Python และ Docker สำหรับบริการเสริม (เช่น database)

---

## 🔧 การตั้งค่าเบื้องต้น (Setup)

1. **ติดตั้งโปรแกรมที่จำเป็น**

   - [Python 3.8+](https://www.python.org/downloads/)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - [Visual Studio Code](https://code.visualstudio.com/) (ไม่จำเป็น แต่แนะนำ)

2. **คลอนรีโพนี้**

   ```bash
   git clone <repository-url>
   cd dockerPosgres
   ```

3. **ติดตั้ง Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 การรันโปรเจกต์ (Running the Project)

### วิธีที่ 1: ใช้ VS Code Tasks (แนะนำ)

โปรเจกต์นี้มีการตั้งค่า `.vscode/tasks.json` ไว้แล้ว เพื่อความสะดวกในการรัน

**ขั้นตอนการรัน:**

1. **เปิดโปรเจกต์ใน Visual Studio Code**

2. **เรียกใช้ Task Menu:**

   - กด `Ctrl + Shift + P` (Windows/Linux) หรือ `Cmd + Shift + P` (Mac)
   - พิมพ์ `Tasks: Run Task`
   - กด Enter

3. **เลือก Task ที่ต้องการรัน:**

   **📋 Tasks ที่มีให้เลือก:**

   - **`Docker Compose Up`**

     - **กดอะไร:** เลือก "Docker Compose Up" จากรายการ
     - **รันอะไร:** รัน `docker compose up -d`
     - **อธิบาย:** เริ่มต้น PostgreSQL database container แบบ background
     - **เมื่อไหร่ใช้:** รันก่อนเสมอ เพื่อเตรียม database

   - **`Run Python App`**

     - **กดอะไร:** เลือก "Run Python App" จากรายการ
     - **รันอะไร:** รัน `python .\psunote\noteapp.py`
     - **อธิบาย:** เริ่มต้น Flask web application
     - **เมื่อไหร่ใช้:** หลังจากที่ Docker รันแล้ว

   - **`Setup and Run All`** ⭐ (แนะนำ)
     - **กดอะไร:** เลือก "Setup and Run All" จากรายการ
     - **รันอะไร:** รัน Docker Compose แล้วตามด้วย Python App ตามลำดับ
     - **อธิบาย:** รันทุกอย่างพร้อมกันแบบอัตโนมัติ
     - **เมื่อไหร่ใช้:** เมื่อต้องการเริ่มต้นทั้งระบบครั้งเดียว

**💡 Tips:**

- Task `Docker Compose Up` จะรันแบบ background ไม่บล็อค terminal
- Task `Run Python App` จะเปิด terminal แสดงผลการทำงาน
- หลังจากรันแล้ว เข้าเว็บได้ที่ `http://localhost:5000`

### วิธีที่ 2: รันด้วย Terminal แบบ Manual

```bash
# 1. รัน Docker PostgreSQL
docker compose up -d

# 2. ติดตั้ง Python dependencies (ครั้งแรกเท่านั้น)
pip install -r requirements.txt

# 3. รัน Python App
python psunote/noteapp.py
```
