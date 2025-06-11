import os
from collections import defaultdict

# Paths
base_dir = '/workspace/OIDv6_dataset/multidata'
splits = ['train', 'validation', 'test']

# Initialize counters
class_counts = {split: defaultdict(int) for split in splits}

# Sınıf isimlerini oku
items_file = '/workspace/items.txt'
with open(items_file, 'r') as f:
    target_classes = [line.strip() for line in f.readlines() if line.strip()]

# Her split için görselleri tarayıp hangi sınıfların kaç adet örneği olduğunu bul
for split in splits:
    labels_dir = os.path.join(base_dir, split, 'labels')
    if not os.path.exists(labels_dir):
        print(f"{labels_dir} bulunamadı, atlanıyor!")
        continue

    for label_file in os.listdir(labels_dir):
        label_path = os.path.join(labels_dir, label_file)
        if not label_file.endswith('.txt'):
            continue

        with open(label_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                class_id = int(line.strip().split()[0])
                if class_id < len(target_classes):
                    class_name = target_classes[class_id]
                    class_counts[split][class_name] += 1

# Sonuçları yazdır
for split in splits:
    print(f"\n=== {split.upper()} SPLIT ===")
    for class_name in target_classes:
        count = class_counts[split].get(class_name, 0)
        print(f"{class_name}: {count} görsel")

print("\n✅ Dataset analizi tamamlandı!")