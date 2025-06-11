import os
import pandas as pd
from tqdm import tqdm

# Ana dizin
base_dir = '/workspace/OIDv6_dataset'
items_file = '/workspace/items.txt'  # Sadece istediğin sınıflar
class_desc_csv = os.path.join(base_dir, 'metadata/class-descriptions-boxable.csv')

# Train, Validation, Test için ayarlar
splits = {
    'train': {
        'images_dir': os.path.join(base_dir, 'multidata/train'),
        'labels_dir': os.path.join(base_dir, 'multidata/train/labels'),
        'csv_file': os.path.join(base_dir, 'boxes/oidv6-train-annotations-bbox.csv')
    },
    'validation': {
        'images_dir': os.path.join(base_dir, 'multidata/validation'),
        'labels_dir': os.path.join(base_dir, 'multidata/validation/labels'),
        'csv_file': os.path.join(base_dir, 'boxes/validation-annotations-bbox.csv')
    },
    'test': {
        'images_dir': os.path.join(base_dir, 'multidata/test'),
        'labels_dir': os.path.join(base_dir, 'multidata/test/labels'),
        'csv_file': os.path.join(base_dir, 'boxes/test-annotations-bbox.csv')
    }
}

# Labels klasörlerini oluştur
for split_info in splits.values():
    os.makedirs(split_info['labels_dir'], exist_ok=True)

# 1. Class descriptions'u oku
class_desc = pd.read_csv(class_desc_csv, header=None)
class_desc.columns = ['LabelName', 'ClassName']

# 2. items.txt dosyasını oku
with open(items_file, 'r') as f:
    target_classes = [line.strip() for line in f.readlines() if line.strip()]

# 3. items.txt'deki isimleri LabelName'e eşle
valid_labels = class_desc[class_desc['ClassName'].isin(target_classes)]

# LabelName -> class id haritası
labelname_to_id = {row.LabelName: idx for idx, row in enumerate(valid_labels.itertuples())}

print(f"{len(labelname_to_id)} adet sınıf eşleşti.")

# 4. Her split için işlemleri yap
for split_name, split_info in splits.items():
    print(f"\n{split_name.upper()} datası işleniyor...")

    if not os.path.exists(split_info['csv_file']):
        print(f"{split_info['csv_file']} bulunamadı, atlanıyor!")
        continue

    df = pd.read_csv(split_info['csv_file'])
    df = df[df['LabelName'].isin(labelname_to_id.keys())]

    for image_id, group in tqdm(df.groupby('ImageID')):
        label_path = os.path.join(split_info['labels_dir'], f"{image_id}.txt")
        with open(label_path, 'w') as f:
            for _, row in group.iterrows():
                class_id = labelname_to_id[row['LabelName']]
                x_min = row['XMin']
                x_max = row['XMax']
                y_min = row['YMin']
                y_max = row['YMax']

                x_center = (x_min + x_max) / 2
                y_center = (y_min + y_max) / 2
                width = x_max - x_min
                height = y_max - y_min

                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    print(f"✅ {split_name} için YOLO etiketleri oluşturuldu!")

print("\n✅ Tüm dataset hazır!")