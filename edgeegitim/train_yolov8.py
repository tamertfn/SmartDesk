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
        "--type_data", "train",
        "--classes"
    ] + classes + [
        "--limit", "700",
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
        print("Train İndirme sırasında hata oluştu:")
        print(err.stderr)
    except Exception as err:
        print(f"Beklenmeyen hata: {err}")

        # Komutu oluştur
    command = [
        "oidv6", "downloader", language,
        "--dataset", dataset_dir,
        "--type_data", "validation",
        "--classes"
    ] + classes + [
        "--limit", "200",
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
        print("Valid İndirme sırasında hata oluştu:")
        print(err.stderr)
    except Exception as err:
        print(f"Beklenmeyen hata: {err}")

        # Komutu oluştur
    command = [
        "oidv6", "downloader", language,
        "--dataset", dataset_dir,
        "--type_data", "test",
        "--classes"
    ] + classes + [
        "--limit", "100",
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
        print("Test İndirme sırasında hata oluştu:")
        print(err.stderr)
    except Exception as err:
        print(f"Beklenmeyen hata: {err}")

if __name__ == "__main__":
    main()