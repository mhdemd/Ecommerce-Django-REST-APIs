# استفاده از تصویر پایه Python
FROM python:3.10

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی کردن فایل‌های مورد نیاز
COPY requirements.txt /app/
COPY . /app/

# نصب وابستگی‌ها
RUN pip install --no-cache-dir -r requirements.txt

# اجرای سرور Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
