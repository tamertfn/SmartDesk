import yaml
import os

# Dosya yolları
yaml_path = "/workspace/workspace/OIDv6_dataset/datasets/data_edge.yaml"
label_txt_path = "/workspace/workspace/runs/detect/train8/weights/label.txt"

# YAML dosyasını oku
with open(yaml_path, "r") as f:
    data_yaml = yaml.safe_load(f)
names = data_yaml["names"]

# label.txt dosyasını oluştur
os.makedirs(os.path.dirname(label_txt_path), exist_ok=True)
with open(label_txt_path, "w") as f:
    for i in range(len(names)):
        f.write(f"{names[i]}\n")

print(f"✅ label.txt oluşturuldu: {label_txt_path}")
