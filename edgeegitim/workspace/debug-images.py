import os
import yaml
import pandas as pd

dataset_root = "/workspace/workspace/OIDv6_dataset"
yaml_path = os.path.join(dataset_root, "datasets/data_edge.yaml")
classdesc_path = os.path.join(dataset_root, "metadata/class-descriptions-boxable.csv")
csv_path = os.path.join(dataset_root, "boxes/oidv6-train-annotations-bbox.csv")
image_dir = os.path.join(dataset_root, "multidata/train")

# 1. data_edge.yaml -> names
with open(yaml_path, "r") as f:
    data_yaml = yaml.safe_load(f)
names = data_yaml["names"]
name2id = {name: i for i, name in names.items()}

# 2. LabelName -> class name eşlemesi
classdesc = pd.read_csv(classdesc_path, header=None, names=["LabelName", "ClassName"])
matched = {}
for name in name2id:
    match = classdesc[classdesc["ClassName"].str.lower() == name.lower()]
    if not match.empty:
        matched[match["LabelName"].values[0]] = name
class_map = matched

# 3. Etiket CSV'sini yükle
df = pd.read_csv(csv_path)
df = df[df["LabelName"].isin(class_map.keys())]

# 4. İlk 50 satırdaki görsellerin varlığı kontrol edilsin
missing_images = []
for _, row in df.head(50).iterrows():
    img_id = row["ImageID"]
    img_file = os.path.join(image_dir, f"{img_id}.jpg")
    if not os.path.exists(img_file):
        missing_images.append(img_file)

# 5. Eksik görselleri yazdır
print("❌ Eksik görseller:")
for path in missing_images:
    print(path)
