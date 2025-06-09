import subprocess
import os
import time

FOLDERS = ["DCIM", "Pictures", "Movies", "Download", "Music", "Audiobooks"]
BACKUP_PATH = "./data"

def run_adb_command(cmd):
   result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
   if result.returncode != 0:
       print(f"❌ Ошибка: {' '.join(cmd)}")
       print(result.stderr.strip())
   return result.stdout.strip()

def check_device():
   print("проверка подключения устройства")
   output = run_adb_command(["adb", "devices"])
   if "device" in output and not "unauthorized" in output:
       print("устройство подключено.")
       return True
   elif "unauthorized" in output:
       print("Нужно разрешить откладку")
   else:
       print("устройство не найдено")
   return False

def create_folders():
   for folder in FOLDERS:
       path = os.path.join(BACKUP_PATH, folder)
       os.makedirs(path, exist_ok=True)

def backup_folders():
   for folder in FOLDERS:
       print(f"Копирование {folder}...")
       run_adb_command(["adb", "pull", f"/sdcard/{folder}/", f"{BACKUP_PATH}/{folder}/"])
       print(f"{folder} Готово!\n")

def main():
   if not check_device():
       return
   print("создание папок")
   create_folders()
   print("начинаем бэкап\n")
   backup_folders()
   print("все данные скопированы в ./data")

if __name__ == "__main__":
   main()

