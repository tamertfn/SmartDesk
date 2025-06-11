import os
import yaml
import pandas as pd

# Kök dizin
dataset_root = "/workspace/workspace/OIDv6_dataset"
yaml_path = os.path.join(dataset_root, "datasets/data_edge.yaml")
classdesc_path = os.path.join(dataset_root, "metadata/class-descriptions-boxable.csv")
box_files = {
    "train": os.path.join(dataset_root, "boxes/oidv6-train-annotations-bbox.csv"),
    "validation": os.path.join(dataset_root, "boxes/validation-annotations-bbox.csv"),
    "test": os.path.join(dataset_root, "boxes/test-annotations-bbox.csv"),
}
image_roots = {
    "train": os.path.join(dataset_root, "multidata/train"),
    "validation": os.path.join(dataset_root, "multidata/validation"),
    "test": os.path.join(dataset_root, "multidata/test"),
}
output_images = {s: os.path.join(dataset_root, f"images/{s}") for s in box_files}
output_labels = {s: os.path.join(dataset_root, f"labels/{s}") for s in box_files}
for d in list(output_images.values()) + list(output_labels.values()):
    os.makedirs(d, exist_ok=True)

# YAML'den sınıfları al
with open(yaml_path, "r") as f:
    data_yaml = yaml.safe_load(f)
names = data_yaml["names"]
name2id = {name: i for i, name in names.items()}

# class-descriptions-boxable.csv'den case-insensitive eşleşme
classdesc = pd.read_csv(classdesc_path, header=None, names=["LabelName", "ClassName"])
matched = {}
for name in name2id:
    match = classdesc[classdesc["ClassName"].str.lower() == name.lower()]
    if not match.empty:
        matched[match["LabelName"].values[0]] = name
class_map = matched  # LabelName → class name

# Etiketleri oluştur
for split, csv_path in box_files.items():
    df = pd.read_csv(csv_path)
    df = df[df["LabelName"].isin(class_map.keys())]
    image_dir = image_roots[split]

    for _, row in df.iterrows():
        img_id = row["ImageID"]
        class_name = class_map[row["LabelName"]]
        class_id = name2id[class_name]
        x_min, x_max = row["XMin"], row["XMax"]
        y_min, y_max = row["YMin"], row["YMax"]
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        width = x_max - x_min
        height = y_max - y_min

        img_file = os.path.join(image_dir, f"{img_id}.jpg")
        out_img = os.path.join(output_images[split], f"{img_id}.jpg")
        label_file = os.path.join(output_labels[split], f"{img_id}.txt")

        if os.path.exists(img_file):
            if not os.path.exists(out_img):
                os.system(f"cp '{img_file}' '{out_img}'")
            with open(label_file, "a") as f:
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
