import os
import yaml
import pandas as pd

dataset_root = "/workspace/workspace/OIDv6_dataset"
yaml_file = os.path.join(dataset_root, "datasets/data_edge.yaml")
desc_file = os.path.join(dataset_root, "metadata/class-descriptions-boxable.csv")

splits = {
    "train": "oidv6-train-annotations-bbox.csv",
    "validation": "validation-annotations-bbox.csv",
    "test": "test-annotations-bbox.csv"
}

# Load class names from data_edge.yaml
with open(yaml_file, "r") as f:
    yaml_data = yaml.safe_load(f)
class_names = yaml_data["names"]
name2id = {v: k for k, v in class_names.items()}

# Load class description mapping
desc = pd.read_csv(desc_file, header=None, names=["LabelName", "ClassName"])
valid_classes = desc[desc["ClassName"].isin(class_names.values())]
labelname_to_name = dict(zip(valid_classes["LabelName"], valid_classes["ClassName"]))

# Process each split
for split, csv_file in splits.items():
    print(f"🔁 İşleniyor: {split}")
    csv_path = os.path.join(dataset_root, "boxes", csv_file)
    df = pd.read_csv(csv_path)
    df = df[df["LabelName"].isin(labelname_to_name.keys())]

    image_dir = os.path.join(dataset_root, "images", split)
    label_dir = os.path.join(dataset_root, "labels", split)
    os.makedirs(label_dir, exist_ok=True)

    image_ids = set(os.path.splitext(f)[0] for f in os.listdir(image_dir) if f.endswith(".jpg"))
    df = df[df["ImageID"].isin(image_ids)]

    for img_id, rows in df.groupby("ImageID"):
        label_path = os.path.join(label_dir, f"{img_id}.txt")
        with open(label_path, "w") as f:
            for _, row in rows.iterrows():
                class_name = labelname_to_name[row["LabelName"]]
                class_id = name2id[class_name]
                x_center = (row["XMin"] + row["XMax"]) / 2
                y_center = (row["YMin"] + row["YMax"]) / 2
                width = row["XMax"] - row["XMin"]
                height = row["YMax"] - row["YMin"]
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    print(f"✅ {split} tamamlandı: {len(df)} bbox işlendi")
