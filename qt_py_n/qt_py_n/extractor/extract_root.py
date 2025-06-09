import subprocess
import os
import sys
import time
from datetime import datetime
from pathlib import Path


class AndroidForensicCollector:
    def __init__(self, output_dir="android_forensic_collection"):
        self.output_dir = Path(output_dir)
        self.device_id = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def setup_output_directory(self):
        dirs = [
            "filesystem",
            "logs",
            "system_info",
            "kernel",
            "dumpsys"
        ]
        for dir_name in dirs:
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)
        print(f"[+] Output directory created: {self.output_dir}")

    def check_adb_connection(self):
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if 'device' not in result.stdout:
                print("[-] No ADB devices found. Ensure device is connected with USB debugging enabled.")
                return False
            lines = result.stdout.strip().split('\n')[1:]
            for line in lines:
                if 'device' in line:
                    self.device_id = line.split()[0]
                    break
            result = subprocess.run(['adb', 'shell', 'su', '-c', 'id'], capture_output=True, text=True)
            if 'uid=0' not in result.stdout:
                print("[-] Root access not available. Ensure device is rooted and root access is granted.")
                return False
            print(f"[+] Connected to device: {self.device_id}")
            print("[+] Root access confirmed")
            return True
        except FileNotFoundError:
            print("[-] ADB not found in PATH. Please install Android SDK platform tools.")
            return False
        except Exception as e:
            print(f"[-] ADB connection error: {e}")
            return False

    def run_adb_command(self, command, output_file=None, use_root=True):
        if use_root:
            full_command = ['adb', 'shell', 'su', '-c', command]
        else:
            full_command = ['adb', 'shell', command]
        try:
            print(f"[*] Executing: {' '.join(full_command)}")
            result = subprocess.run(full_command, capture_output=True, text=True, timeout=300)
            if output_file:
                with open(output_file, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(result.stdout)
                    if result.stderr:
                        f.write(f"\n--- STDERR ---\n{result.stderr}")
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            print(f"[!] Command timed out: {command}")
            return None, "Command timed out"
        except Exception as e:
            print(f"[!] Command failed: {e}")
            return None, str(e)

    def collect_device_info(self):
        print("\n[+] Collecting device information...")
        info_commands = {
            'device_props.txt': 'getprop',
            'build_info.txt': 'cat /system/build.prop',
            'cpu_info.txt': 'cat /proc/cpuinfo',
            'memory_info.txt': 'cat /proc/meminfo',
            'mount_info.txt': 'cat /proc/mounts',
            'partition_info.txt': 'cat /proc/partitions',
            'uptime.txt': 'cat /proc/version && echo \"--- UPTIME ---\" && cat /proc/uptime'
        }
        for filename, command in info_commands.items():
            output_file = self.output_dir / "system_info" / filename
            self.run_adb_command(command, output_file)

    def collect_filesystem_structure(self):
        print("\n[+] Collecting filesystem structure...")
        directories = [
            '/system',
            '/data',
            '/vendor',
            '/sdcard',
            '/cache',
            '/proc',
            '/sys',
            '/dev',
            '/etc'
        ]
        for directory in directories:
            safe_name = directory.replace('/', '_').lstrip('_')
            output_file = self.output_dir / "filesystem" / f"{safe_name}_listing.txt"
            command = f'ls -laR {directory} 2>/dev/null || echo "Directory not accessible: {directory}"'
            self.run_adb_command(command, output_file)

    def collect_filesystem_data(self):
        print("\n[+] Collecting filesystem data (this may take a while)...")
        backup_dirs = [
            ('/system', 'system.tar'),
            ('/data', 'data.tar'),
            ('/vendor', 'vendor.tar'),
            ('/cache', 'cache.tar')
        ]
        for source_dir, tar_name in backup_dirs:
            print(f"[*] Backing up {source_dir}...")
            output_file = self.output_dir / "filesystem" / tar_name
            device_tar_path = f"/sdcard/{tar_name}"
            tar_command = f'tar -cf {device_tar_path} {source_dir} 2>/dev/null'
            stdout, stderr = self.run_adb_command(tar_command)
            try:
                subprocess.run(['adb', 'pull', device_tar_path, str(output_file)],
                               check=True, capture_output=True)
                print(f"[+] Successfully backed up {source_dir}")
                self.run_adb_command(f'rm {device_tar_path}')
            except subprocess.CalledProcessError as e:
                print(f"[!] Failed to pull {tar_name}: {e}")

    def collect_logs(self):
        print("\n[+] Collecting system logs...")
        log_commands = {
            'logcat_main.txt': 'logcat -d -v time',
            'logcat_radio.txt': 'logcat -d -b radio -v time',
            'logcat_events.txt': 'logcat -d -b events -v time',
            'logcat_system.txt': 'logcat -d -b system -v time',
            'dmesg.txt': 'dmesg',
            'last_kmsg.txt': 'cat /proc/last_kmsg 2>/dev/null || echo "last_kmsg not available"',
            'kernel_log.txt': 'cat /proc/kmsg 2>/dev/null | head -1000 || echo "kmsg not accessible"'
        }
        for filename, command in log_commands.items():
            output_file = self.output_dir / "logs" / filename
            self.run_adb_command(command, output_file)

    def collect_kernel_info(self):
        print("\n[+] Collecting kernel information...")
        kernel_commands = {
            'kernel_version.txt': 'uname -a',
            'kernel_modules.txt': 'cat /proc/modules',
            'interrupts.txt': 'cat /proc/interrupts',
            'iomem.txt': 'cat /proc/iomem',
            'ioports.txt': 'cat /proc/ioports',
            'cmdline.txt': 'cat /proc/cmdline',
            'crypto.txt': 'cat /proc/crypto',
            'filesystems.txt': 'cat /proc/filesystems'
        }
        for filename, command in kernel_commands.items():
            output_file = self.output_dir / "kernel" / filename
            self.run_adb_command(command, output_file)

    def collect_dumpsys_info(self):
        print("\n[+] Collecting dumpsys information...")
        dumpsys_services = [
            'activity', 'package', 'wifi', 'connectivity', 'telephony',
            'location', 'battery', 'power', 'account', 'user',
            'notification', 'input_method', 'window', 'media_session'
        ]
        output_file = self.output_dir / "dumpsys" / "dumpsys_all.txt"
        self.run_adb_command('dumpsys', output_file, use_root=False)
        for service in dumpsys_services:
            output_file = self.output_dir / "dumpsys" / f"dumpsys_{service}.txt"
            command = f'dumpsys {service}'
            self.run_adb_command(command, output_file, use_root=False)

    def create_collection_summary(self):
        summary_file = self.output_dir / "collection_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Android Forensic Collection Summary\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Device ID: {self.device_id}\n")
            f.write(f"Collection Timestamp: {self.timestamp}\n\n")
            for subdir in self.output_dir.iterdir():
                if subdir.is_dir():
                    file_count = len(list(subdir.glob('*')))
                    f.write(f"{subdir.name}: {file_count} files\n")
        print(f"[+] Collection summary saved to: {summary_file}")

    def run_full_collection(self):
        print(f"Android Forensic Data Collection Started - {self.timestamp}")
        print("=" * 60)
        if not self.check_adb_connection():
            sys.exit(1)
        self.setup_output_directory()
        try:
            self.collect_device_info()
            self.collect_filesystem_structure()
            self.collect_logs()
            self.collect_kernel_info()
            self.collect_dumpsys_info()
            collect_full_fs = input(
                "\n[?] Collect full filesystem data? This can take a long time and use significant storage (y/N): ")
            if collect_full_fs.lower() == 'y':
                self.collect_filesystem_data()
            self.create_collection_summary()
            print("\n" + "=" * 60)
            print(f"[+] Collection completed successfully!")
            print(f"[+] Data saved to: {self.output_dir}")
        except KeyboardInterrupt:
            print("\n[!] Collection interrupted by user")
        except Exception as e:
            print(f"\n[!] Collection failed: {e}")


def main():
    print("Android Forensic Data Collection Tool")
    print("Ensure your device is rooted and ADB debugging is enabled")
    print("=" * 60)
    output_dir = input("Enter output directory (press Enter for default 'android_forensic_collection'): ").strip()
    if not output_dir:
        output_dir = "android_forensic_collection"
    collector = AndroidForensicCollector(output_dir)
    collector.run_full_collection()


if __name__ == "__main__":
    main()
