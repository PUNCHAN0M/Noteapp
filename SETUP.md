path : .vscode/tasks.json

````
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Docker Compose Up",
      "type": "shell",
      "command": "docker compose up -d",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": [],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "detail": "รัน Docker Compose แบบ detached"
    },
    {
      "label": "Run Python App",
      "type": "shell",
      "command": "python",
      "args": [
        ".\\psunote\\noteapp.py"
      ],
      "group": "none",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      },
      "problemMatcher": [],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "detail": "รันแอปพลิเคชัน Python โน้ต"
    },
    {
      "label": "Setup and Run All",
      "type": "shell",
      "command": "",
      "dependsOn": [
        "Docker Compose Up",
        "Run Python App"
      ],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      },
      "detail": "รันทั้ง Docker และ Python App"
    }
  ]
}
```
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
   cd psunote
````

การรันโปรเจกต์
วิธีที่ 1: ใช้ VS Code Tasks (แนะนำ)
โปรเจกต์นี้มีการตั้งค่า tasks.json ไว้แล้ว เพื่อความสะดวกในการรัน

เปิดโปรเจกต์ใน Visual Studio Code
กด Ctrl + Shift + P แล้วพิมพ์ "Tasks: Run Build Task"
เลือกหนึ่งในตัวเลือก:
Docker Compose Up – รัน container ต่าง ๆ ด้วย Docker
Run Python App – รันแอป Python (noteapp.py)
Setup and Run All – รันทั้ง Docker และ Python App ตามลำดับ
