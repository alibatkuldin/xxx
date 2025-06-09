import hashlib

def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Читаем файл блоками, чтобы можно было обрабатывать большие файлы
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print("Файл не найден. Пожалуйста, проверьте путь к файлу.")
        return None

if __name__ == "__main__":
    file_path = 'Automotive_Report.pdf'
    hash_sum = calculate_file_hash(file_path)
    if hash_sum:
        print(f"Хэш-сумма файла: {hash_sum}")
