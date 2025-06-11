FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y libgl1-mesa-glx \
    python3-pip \
    python3-dev \
    python3-venv \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libsm6 \
    libxrender1 \
    libxext6 \
    nano
RUN pip3 install --upgrade pip
RUN pip install fastapi uvicorn pillow torch torchvision pandas opencv-python requests ultralytics
WORKDIR /app
COPY best.pt .
COPY app.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

