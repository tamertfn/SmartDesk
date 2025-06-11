import subprocess

def main():
    items_file = "items.txt"
    dataset_dir = "OIDv6_dataset"
    image_limit = 800  # 0 = limitsiz, istersen değiştir
    type_data = "all"  # train, validation, test, all
    language = "en"  # veya "ru"

    # items.txt dosyasını oku
    try:
        with open(items_file, "r") as f:
            classes = [line.strip() for line in f if line.strip()]
    except Exception as err:
        print(f"items.txt okunamadı: {err}")
        return

    # Sınıfları tek bir stringe dönüştür
    classes_str = " ".join([f'"{c}"' if " " in c else c for c in classes])

    # Komutu oluştur
    command = [
        "oidv6", "downloader", language,
        "--dataset", dataset_dir,
        "--type_data", type_data,
        "--classes"
    ] + classes + [
        "--limit", str(image_limit),
        "--multi_classes",
        "--yes"
    ]

    # Komutu yazdır (debug için)
    print("Çalıştırılan komut:")
    print(" ".join(command))

    # Komutu çalıştır
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as err:
        print("İndirme sırasında hata oluştu:")
        print(err.stderr)
    except Exception as err:
        print(f"Beklenmeyen hata: {err}")

if __name__ == "__main__":
    main()

    
#oidv6 downloader en --dataset OIDv6_dataset --type_data all --classes Laptop "Tablet computer" "Computer keyboard" "Computer monitor" "Computer mouse" Pen "Pencil case" "Pencil sharpener" Stapler Book "Mobile phone" Calculator "Adhesive tape" Headphones Flashlight Bottle Mug "Facial tissue holder" "Toilet paper" "Paper towel" Glasses Bowl Box Camera Watch Coin "Personal care" Cream Eraser Flute Fork "Kitchen knife" Spoon Glove IPod Necklace Ruler Scissors Screwdriver Snack Toothbrush "Drinking straw" --limit 800 --multi_classes --yes
