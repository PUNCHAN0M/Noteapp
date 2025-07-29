# 📝 PSU Note - Flask PostgreSQL CRUD Application

แอปพลิเคชันจัดการบันทึก (Note) และแท็ก (Tag) ที่พัฒนาด้วย Flask และ PostgreSQL พร้อมระบบ CRUD ที่สมบูรณ์

## ✨ ฟีเจอร์หลัก

### 🗂️ การจัดการ Notes

- **สร้าง** Note ใหม่พร้อม title, description และ tags
- **อ่าน** รายการ Notes ทั้งหมดพร้อมการแสดงผลที่สวยงาม
- **แก้ไข** Note ที่มีอยู่ (title, description, tags)
- **ลบ** Note ที่ไม่ต้องการ

### 🏷️ การจัดการ Tags

- **สร้าง** Tag ใหม่แยกต่างหาก
- **อ่าน** รายการ Tags ทั้งหมดพร้อมจำนวน Notes
- **แก้ไข** ชื่อ Tag ที่มีอยู่แล้ว
- **ลบ** Tag (จะลบออกจาก Notes ทั้งหมดที่ใช้งาน)
- **ความสัมพันธ์ Many-to-Many** ระหว่าง Notes และ Tags
- **สร้าง Tag อัตโนมัติ** เมื่อสร้าง Note ใหม่

### 📊 Dashboard

- แสดงจำนวน Notes และ Tags ทั้งหมด
- รายการ Notes เรียงตามวันที่อัปเดตล่าสุด
- การแสดงผลแบบ Card พร้อม metadata

### 🔍 ระบบค้นหา

- ค้นหาใน **title**, **description**, และ **tags**
- ค้นหาแบบ real-time ผ่าน URL parameters
- รองรับการค้นหาร่วมกับการกรอง tags

### 🏷️ Sidebar และการกรอง

- **Sidebar ด้านซ้าย** แสดง tags ทั้งหมด
- **คลิก tag** เพื่อกรอง Notes ที่มี tag นั้น
- แสดงจำนวน Notes ในแต่ละ tag
- ไฮไลท์ tag ที่เลือก

## 🏗️ โครงสร้างโปรเจกต์

```
dockerPosgres/
├── psunote/                # โฟลเดอร์แอปพลิเคชันหลัก
│   ├── noteapp.py          # แอปพลิเคชันหลัก Flask
│   ├── models.py           # โมเดลฐานข้อมูล (Note, Tag)
│   ├── forms.py            # ฟอร์ม WTForms
│   └── templates/          # เทมเพลต HTML
│       ├── base.html       # เทมเพลตหลัก
│       ├── index.html      # หน้า Dashboard
│       ├── notes-create.html   # ฟอร์มสร้าง Note
│       ├── notes-edit.html     # ฟอร์มแก้ไข Note
│       ├── tags-list.html      # รายการ Tags
│       ├── tags-create.html    # ฟอร์มสร้าง Tag
│       ├── tags-edit.html      # ฟอร์มแก้ไข Tag
│       └── tags-view.html      # แสดง Notes ตาม Tag
├── .vscode/                # VS Code configuration
│   └── tasks.json          # ตั้งค่า Tasks สำหรับ VS Code
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # PostgreSQL container
├── .gitignore             # Git ignore rules
├── README.md              # เอกสารนี้
└── SETUP.md               # คู่มือการตั้งค่าและรัน
```

## 🗄️ โครงสร้างฐานข้อมูล

### Table: `notes`

- `id` (Primary Key)
- `title` (String, ไม่ว่าง)
- `description` (Text)
- `created_date` (DateTime)
- `updated_date` (DateTime, อัปเดตอัตโนมัติ)

### Table: `tags`

- `id` (Primary Key)
- `name` (String, ไม่ว่าง)
- `created_date` (DateTime)

### Table: `note_tag` (Many-to-Many)

- `note_id` (Foreign Key → notes.id)
- `tag_id` (Foreign Key → tags.id)

## 🔧 การติดตั้งและรัน

### วิธีที่ 1: ใช้ VS Code Tasks (แนะนำ)

โปรเจกต์นี้มีการตั้งค่า VS Code Tasks ไว้แล้ว สำหรับรายละเอียดดู [SETUP.md](SETUP.md)

**ขั้นตอนย่อ:**

1. เปิดโปรเจกต์ใน VS Code
2. กด `Ctrl + Shift + P` และพิมพ์ `Tasks: Run Task`
3. เลือก `Setup and Run All` เพื่อรันทั้งระบบ

### วิธีที่ 2: รันแบบ Manual

#### 1. เตรียมความพร้อม

```bash
# Clone หรือ download โปรเจกต์
cd dockerPosgres

# สร้าง virtual environment (แนะนำ)
python -m venv .venv
.venv\Scripts\activate     # Windows
# หรือ
source .venv/bin/activate  # Linux/Mac
```

#### 2. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

#### 3. เริ่ม PostgreSQL Database

```bash
# ใน directory หลัก (dockerPosgres)
docker-compose up -d
```

#### 4. ตั้งค่าฐานข้อมูล

ตรวจสอบการเชื่อมต่อใน `psunote/noteapp.py`:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://pun:123456@localhost:5432/coedb"
```

#### 5. รันแอปพลิเคชัน

```bash
python psunote/noteapp.py
```

เปิดเบราว์เซอร์ไปที่: `http://localhost:5000`

## 📚 วิธีใช้งาน

### 🆕 สร้าง Note ใหม่

1. คลิก **"สร้าง Note"** ใน Navigation Bar
2. กรอก **Title** (จำเป็น)
3. กรอก **Description** (ไม่จำเป็น)
4. กรอก **Tags** คั่นด้วยจุลภาค เช่น: `python, flask, web development`
5. คลิก **"บันทึก"**

### ✏️ แก้ไข Note

1. คลิกปุ่ม **✏️ (แก้ไข)** ในรายการ Note
2. แก้ไขข้อมูลที่ต้องการ
3. สามารถเพิ่ม/ลบ Tags ได้
4. คลิก **"บันทึกการเปลี่ยนแปลง"**

### 🗑️ ลบ Note

1. คลิกปุ่ม **🗑️ (ลบ)** ในรายการ Note
2. ยืนยันการลบ

### 🏷️ สร้าง Tag

1. คลิก **"สร้าง Tag"** ใน Navigation Bar
2. กรอกชื่อ Tag
3. คลิก **"สร้าง Tag"**

### ✏️ แก้ไข Tag

1. ไปที่หน้า **"จัดการ Tags"**
2. คลิกปุ่ม **✏️ (แก้ไข)** ใน Tag ที่ต้องการ
3. แก้ไขชื่อ Tag
4. คลิก **"บันทึกการเปลี่ยนแปลง"**

### 🗑️ ลบ Tag

1. ไปที่หน้า **"จัดการ Tags"**
2. คลิกปุ่ม **🗑️ (ลบ)** ใน Tag ที่ต้องการ
3. ยืนยันการลบ (Tag จะถูกเอาออกจาก Notes ทั้งหมดที่ใช้งาน)

### 🔍 ค้นหา

1. ใช้ช่องค้นหาใน Navigation Bar
2. ระบบจะค้นหาใน title, description และ tags
3. กด Enter หรือคลิกปุ่มค้นหา

### 🏷️ กรองตาม Tag

1. ใช้ Sidebar ด้านซ้าย
2. คลิก Tag ที่ต้องการ
3. ระบบจะแสดงเฉพาะ Notes ที่มี Tag นั้น

## 🛠️ เทคโนโลยีที่ใช้

- **Backend:** Flask (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Forms:** Flask-WTF, WTForms
- **Frontend:** Bootstrap 5, Bootstrap Icons
- **Container:** Docker (สำหรับ PostgreSQL)

## 📋 Dependencies (requirements.txt)

```
blinker==1.9.0
click==8.2.1
colorama==0.4.6
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
greenlet==3.2.3
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
psycopg2-binary==2.9.10
SQLAlchemy==2.0.41
typing_extensions==4.14.1
Werkzeug==3.1.3
WTForms==3.2.1
WTForms-SQLAlchemy==0.4.2
```

## 🔧 การปรับแต่ง

### เปลี่ยน Database Connection

แก้ไขใน `psunote/noteapp.py`:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://username:password@host:port/database"
```

### เปลี่ยน Secret Key

แก้ไขใน `psunote/noteapp.py`:

```python
app.config["SECRET_KEY"] = "your-secret-key-here"
```

### ปรับแต่ง UI

- แก้ไขไฟล์ในโฟลเดอร์ `psunote/templates/`
- ปรับ CSS ใน `base.html`
- เพิ่ม JavaScript ตามต้องการ

### ปรับแต่ง VS Code Tasks

แก้ไขไฟล์ `.vscode/tasks.json` เพื่อเปลี่ยนคำสั่งหรือเพิ่ม Task ใหม่

## 🐛 การแก้ไขปัญหาเบื้องต้น

### 1. Database Connection Error

- ตรวจสอบว่า PostgreSQL ทำงานอยู่: `docker-compose ps`
- ตรวจสอบ connection string ใน `psunote/noteapp.py`
- รีสตาร์ท PostgreSQL: `docker-compose restart postgresql`

### 2. Import Error

- ตรวจสอบ virtual environment: `pip list`
- ติดตั้ง dependencies: `pip install -r requirements.txt`
- ตรวจสอบว่าอยู่ในโฟลเดอร์ที่ถูกต้อง

### 3. Template Not Found

- ตรวจสอบโครงสร้างโฟลเดอร์ `psunote/templates/`
- ตรวจสอบชื่อไฟล์ template ใน routes

### 4. AttributeError กับ Tags

- ปัญหานี้แก้ไขแล้วใน version ปัจจุบัน
- ถ้ายังพบปัญหา ให้ตรวจสอบไฟล์ `psunote/forms.py` และ `psunote/noteapp.py`

### 5. VS Code Tasks ไม่ทำงาน

- ตรวจสอบว่าเปิดโปรเจกต์ในโฟลเดอร์ `dockerPosgres` (ไม่ใช่ subfolder)
- ตรวจสอบไฟล์ `.vscode/tasks.json`
- รีสตาร์ท VS Code

---

**พัฒนาโดย:** PUNCHAN0M  
**Repository:** [Noteapp](https://github.com/PUNCHAN0M/Noteapp)  
**วันที่อัปเดต:** 29 กรกฎาคม 2025
