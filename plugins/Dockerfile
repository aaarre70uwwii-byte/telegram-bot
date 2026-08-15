FROM python:3.10-slim

# 1. نثبت ffmpeg عشان pytgcalls يشغل الاغاني
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 2. نحدد مجلد الشغل
WORKDIR /app

# 3. ننسخ requirements ونثبته اول عشان الكاش
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. ننسخ باقي الملفات
COPY . .

# 5. امر التشغيل
CMD ["python", "main.py"]
