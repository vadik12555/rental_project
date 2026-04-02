# Используем стабильный образ Python
FROM python:3.11-bookworm

# Настройки для корректной работы логов
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Обновляем pip через быстрое зеркало
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# Копируем файл зависимостей
COPY requirements.txt /code/

# Устанавливаем библиотеки через зеркало (чтобы не было ReadTimeout)
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Копируем всё остальное
COPY . /code/