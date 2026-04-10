# 1. Base image use karein (Lightweight Python)
FROM python:3.9-slim

# 2. Environment variables set karein 
# (Python output ko buffer nahi karega, logs turant dikhenge)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Working directory banayein
WORKDIR /app

# 4. Pehle requirements copy karein (Caching ke liye)
# Taki agar code badle par libraries nahi, toh ye step skip ho jaye
COPY requirements.txt .

# 5. Dependencies install karein
RUN pip install --no-cache-dir -r requirements.txt

# 6. Pura code copy karein
COPY . .

# 7. Security Fix: Non-root user banayein
# (Production mein root user se container chalana dangerous hota hai)
RUN useradd -m myuser && chown -R myuser /app
USER myuser

# 8. Port expose karein (Aapne 8080 kaha tha)
EXPOSE 8080

# 9. App run karein
CMD ["python", "app.py"]