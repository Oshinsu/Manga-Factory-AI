FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Installation de ComfyUI
WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .

# Installation des requirements Python
RUN pip3 install --no-cache-dir \
    torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cu121

RUN pip3 install --no-cache-dir -r requirements.txt

# Installation des custom nodes pour manga
WORKDIR /app/custom_nodes
RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git
RUN git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
RUN git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# Installation des modèles de base
WORKDIR /app/models/checkpoints
RUN wget -q https://huggingface.co/Linaqruf/anything-v5.0/resolve/main/anything-v5-fp16.safetensors
RUN wget -q https://huggingface.co/hakurei/waifu-diffusion-v1-4/resolve/main/wd-1-4-anime_e2.ckpt

# Script de démarrage personnalisé
WORKDIR /app
COPY start_server.py .
COPY manga_api.py .

EXPOSE 7860

CMD ["python3", "start_server.py"]
