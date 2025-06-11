import os
import re

def is_yolo_format(line):
    return re.match(r"^\d+(\.\d+)?\s+0\.\d+\s+0\.\d+\s+0\.\d+\s+0\.\d+$", line.strip()) is not None

def check_labels(directory):
    issues = []
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith(".txt"):
                continue
            with open(os.path.join(root, file)) as f:
                lines = f.readlines()
                for idx, line in enumerate(lines):
                    if not is_yolo_format(line):
                        issues.append((os.path.join(root, file), idx + 1, line.strip()))
    return issues

label_root = "OIDv6_dataset/multidata"  # Kendi dizinine göre güncelle
splits = ["train", "validation", "test"]

for split in splits:
    print(f"\n--- Checking: {split} ---")
    errors = check_labels(os.path.join(label_root, split))
    if not errors:
        print("✓ Tüm etiketler YOLO formatında.")
    else:
        for file, line_num, content in errors:
            print(f"❌ Hata: {file}, satır {line_num}: \"{content}\"")
