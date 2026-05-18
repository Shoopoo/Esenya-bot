FROM python:3.11-slim

WORKDIR /app

# Копируем только список зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки с флагом --no-cache-dir (это экономит ОЗУ при сборке!)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

CMD ["python", "Esenya.py"]