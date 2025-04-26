from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import os
import psutil
import platform


class DiskAnalyzer:
    def __init__(self, platform: str = platform.system()) -> None:
        self.platform: str = platform
        self.disks: list = []

    def get_disks_info(self) -> list:
        """Повертає інфу про диски;
        Повертає Всю, Зайняту, Вільну, пам'ять і у відсотках;
        Повертає тип диску, права, и шифрування
        """
        match self.platform.lower():
            case "windows":
                for partition in psutil.disk_partitions():
                    try:
                        self.disks.append(
                            [
                                partition.device,
                                f"{(usage := psutil.disk_usage(partition.mountpoint)).total / (1e+9):.2f} GB",
                                f"{usage.used / (1e+9):.2f} GB",
                                f"{usage.free / (1e+9):.2f} GB",
                                usage.percent,
                                partition.fstype,
                                partition.opts,
                            ]
                        )
                    except OSError:
                        continue
            case "linux":
                for partition in psutil.disk_partitions():
                    # Додайте сюди всі інші директорії для ігнорування
                    if partition.fstype in ["tmpfs", "devtmpfs", "squashfs", "vfat"]:
                        continue
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        self.disks.append(
                            [
                                partition.device,
                                f"{usage.total / (1e+9):.2f} GB",
                                f"{usage.used / (1e+9):.2f} GB",
                                f"{usage.free / (1e+9):.2f} GB",
                                usage.percent,
                                partition.fstype,
                                partition.opts,
                            ]
                        )
                    except OSError:
                        continue
            case _:
                raise Exception("System not supported !")
        return self.disks

    @staticmethod
    def scan_directory(
        directory, extensions=None, detail_level=1, debug=False
    ) -> tuple:
        """
        Сканує директорії i рахує кількість файлів, розмір та різні розширення.

        :param directory: Шлях до директорії сканування
        :param extensions: Список розширень, що цікавлять. Якщо None, рахує всі.
        :param detail_level: Рівень деталізаціі (1 - тільки розширення, 2 - деталі по директоріям).
        :return: Словник з кількістю файлів i розміром по розширенням i директоріям.
        """
        file_stats = defaultdict(lambda: {"count": 0, "size": 0})  # Для розширень
        directory_stats = defaultdict(lambda: {"count": 0, "size": 0})  # Для директорій

        # Головна функція обробки
        def process_dir(dir_path):
            local_stats = defaultdict(lambda: {"count": 0, "size": 0})
            try:
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        if debug:
                            print(file)
                        try:
                            _, ext = os.path.splitext(file)
                            ext = ext.lower()
                            file_path = os.path.join(root, file)
                            size = os.path.getsize(file_path)

                            if not extensions or ext in extensions:
                                local_stats[ext]["count"] += 1
                                local_stats[ext]["size"] += size

                                if detail_level == 2:
                                    directory_stats[root]["count"] += 1
                                    directory_stats[root]["size"] += size
                        except Exception as e:
                            print(f"Помилка обробки файлу {file}: {e}")
            except Exception as e:
                print(f"Помилка обробки директорії {dir_path}: {e}")
            return local_stats

        # Обробляємо піддиректорії паралельно
        with ThreadPoolExecutor() as executor:
            future_to_dir = {
                executor.submit(process_dir, os.path.join(directory, subdir)): subdir
                for subdir in next(os.walk(directory))[1]
            }
            for future in future_to_dir:
                try:
                    result = future.result()
                    for ext, stats in result.items():
                        file_stats[ext]["count"] += stats["count"]
                        file_stats[ext]["size"] += stats["size"]
                except Exception as e:
                    print(f"Помилка: {e}")

        # Обробляємо файли в кореневій директорії
        try:
            for file in next(os.walk(directory))[2]:
                if debug:
                    print(file)
                try:
                    _, ext = os.path.splitext(file)
                    ext = ext.lower()
                    file_path = os.path.join(directory, file)
                    size = os.path.getsize(file_path)

                    if not extensions or ext in extensions:
                        file_stats[ext]["count"] += 1
                        file_stats[ext]["size"] += size

                        if detail_level == 2:
                            directory_stats[directory]["count"] += 1
                            directory_stats[directory]["size"] += size
                except Exception as e:
                    print(f"Помилка обробки файлу {file}: {e}")
        except Exception as e:
            print(f"Помилка обробки кореневої директорії {directory}: {e}")

        return file_stats, directory_stats if detail_level == 2 else file_stats

    # Повертає всю інфу у словнику, для більш зручного користування в майбутньому
    def get_info(self, directory, extensions, detail_level, debug) -> dict:
        file_stats, directory_stats = self.scan_directory(
            directory, extensions, detail_level, debug
        )

        dict_of_exts = {
            ext: [stats["count"], stats["size"]] for ext, stats in file_stats.items()
        }
        dict_of_dirs = {
            ext: [stats["count"], stats["size"]]
            for ext, stats in directory_stats.items()
        }

        disks_info = self.get_disks_info()

        return {
            "total-sum": sum([count["count"] for _, count in directory_stats.items()]),
            "total-weight": sum(
                [count["size"] for _, count in directory_stats.items()]
            ),
            "dicts": dict_of_dirs,
            "exts": dict_of_exts,
            "disks-info": disks_info,
        }
