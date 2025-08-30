FROM python:3.11-slim

# Install deps for geopandas
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app and naturalearth data
COPY . .

CMD ["python", "wireframe.py"]

