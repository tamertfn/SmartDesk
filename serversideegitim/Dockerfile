# Dockerfile: YOLOv8 + OpenImages ortamı (manuel kütüphane kurulumu)

# Base image: CUDA destekli Ubuntu
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Ortamı güncelle ve temel araçları yükle
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    wget \
    unzip \
    git \
    nano \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean

# Pip güncelle
RUN pip3 install --upgrade pip

# Gerekli Python paketlerini kur
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip3 install ultralytics openimages tqdm
RUN pip3 install requests numpy pandas progressbar2 opencv-contrib-python awscli

# Çalışma dizini
WORKDIR /workspace

# Şu anda bulunduğun dizindeki tüm dosyaları container'a kopyala
COPY . /workspace

# Varsayılan komut
CMD ["/bin/bash"]
