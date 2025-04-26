import os
import platform
import subprocess
from math import ceil

from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from DiskUsageAnalyzer import DiskAnalyzer


class DiskUsageApp:
    def __init__(self, bars=10, directory=None, mode=7, extensions=None):
        self.console = Console()
        self.bars = bars
        self.directory = directory or os.getcwd()
        self.start_directory = self.directory
        self.platform = platform.system().lower()
        self.extensions = extensions or []
        self.mode = mode
        self.analyzer = DiskAnalyzer(self.platform)
        self.info = None
        #
        self.modes = {
            0: self.command_mode,
            1: self.show_general_info,
            2: self.show_disks_table,
            3: self.show_top_extensions,
            4: self.show_top_directories_by_size,
            5: self.show_top_directories_by_count,
            6: self.show_all_top,
            7: self.show_full_info,
            8: lambda: self.change_directory(full=False),
            9: self.change_bars,
            10: self.change_extensions,
        }
        self.clear_command = "cls" if self.platform == "windows" else "clear"
        
        #
        with open('./menu_text.txt', 'r') as menu_text:
            self.menu_text = menu_text.read()
        #
        self.run()

    def run(self):
        self.console.input("Натисніть Enter щоб почати: (Консоль буде очищено!) ")
        self.clear_screen()
        self.change_directory(full=True)

        while True:
            self.display_menu()
            self.handle_mode()

            self.console.print()
            self.wait_for_continue()
            self.clear_screen()

    def clear_screen(self):
        os.system(self.clear_command)

    def wait_for_continue(self):
        if self.platform == "windows":
            os.system("pause")
        else:
            self.console.input("Натисніть Enter щоб продовжити...")

    def change_directory(self, full=False):
        prompt = "[green]Введіть шлях директорії (Enter для кореневої директорії): " if full else \
                 "[green]Введіть шлях в директорії '/шлях у папці' (Enter для кореневої директорії): "
        path = self.console.input(prompt).strip()

        if not path:
            if not full:
                self.directory = self.start_directory
        else:
            self.directory = os.path.join(self.directory, path) if not full else path

        os.chdir(self.directory)
        self.info = self.analyzer.get_info(
            directory=self.directory,
            extensions=self.extensions or None,
            detail_level=2,
            debug=False,
        )

    def change_bars(self):
        try:
            self.bars = int(self.console.input("[green]Введіть нову кількість позицій для діаграм: "))
        except ValueError:
            self.console.print("[red]Помилка: потрібно ввести число.")

    def change_extensions(self):
        ext_input = self.console.input("[green]Введіть розширення через кому (Enter для всіх): ")
        self.extensions = [e.strip() for e in ext_input.split(",") if e.strip()] or None
        self.refresh_info()

    def refresh_info(self):
        self.info = self.analyzer.get_info(
            directory=self.directory,
            extensions=self.extensions,
            detail_level=2,
            debug=False,
        )

    def display_menu(self):
        self.console.print(self.menu_text)
        try:
            self.mode = int(self.console.input("[green]Введіть потрібний варіант: "))
            self.clear_screen()
        except ValueError:
            exit(0)

    def handle_mode(self):
        func = self.modes.get(self.mode)
        if func:
            func()
        else:
            exit(0)

    def command_mode(self):
        self.console.print('[red]Enter "exit" to close')
        while (command := input(":")) != "exit":
            subprocess.run(command.split(' '), shell=True, cwd=self.directory)

    def show_general_info(self):
        self.console.rule("[red]Файли")
        total_files = self.info["total-sum"]
        total_size = self.info["total-weight"] / 1e9

        largest_dir_by_size = max(self.info["dicts"].items(), key=lambda x: x[1][1], default=None)
        largest_dir_by_count = max(self.info["dicts"].items(), key=lambda x: x[1][0], default=None)
        most_common_ext = max(self.info["exts"].items(), key=lambda x: x[1][0], default=None)

        self.console.print(f"[green]Директорія: {self.directory}")
        self.console.print(f"[green]Кількість файлів: {total_files}")
        self.console.print(f"[blue]Загальна вага: {total_size:.6f} GB\n")

        if largest_dir_by_size:
            self.console.print(f"[blue]Найбільша директорія за вагою: {largest_dir_by_size[0]} ({largest_dir_by_size[1][1] / 1e9:.6f} GB)")
        if largest_dir_by_count:
            self.console.print(f"[blue]Найбільша директорія за кількістю файлів: {largest_dir_by_count[0]} ({largest_dir_by_count[1][0]} файлів)")
        if most_common_ext:
            self.console.print(f"[blue]Найчастіше розширення: {most_common_ext[0]} ({most_common_ext[1][0]} файлів)")

    def show_disks_table(self):
        self.console.rule("[red]Диски")
        table = Table(title="Диски")
        headers = ["Назва", "Загальна пам'ять", "Зайнята пам'ять", "Вільна пам'ять", "Пам'ять (%)", "Формат", "Тип"]
        for header in headers:
            table.add_column(header)

        for disk in self.info["disks-info"]:
            table.add_row(*map(str, disk))

        self.console.print(table)

    def show_top_extensions(self):
        self.console.print("\n[green]Топ-x найчастіших розширень")
        sorted_exts = sorted(self.info["exts"].items(), key=lambda x: x[1][0], reverse=True)[:self.bars]
        self._show_progress(sorted_exts, lambda stat: stat[0], total=self.info["total-sum"], color="green")

    def show_top_directories_by_size(self):
        self.console.print("\n[green]Топ-x найбільших директорій за вагою (GB)")
        sorted_dirs = sorted(self.info["dicts"].items(), key=lambda x: x[1][1], reverse=True)[:self.bars]
        self._show_progress(sorted_dirs, lambda stat: stat[1] / 1e9, total=self.info["total-weight"], color="yellow")

    def show_top_directories_by_count(self):
        self.console.print("\n[green]Топ-x директорій за кількістю файлів")
        sorted_dirs = sorted(self.info["dicts"].items(), key=lambda x: x[1][0], reverse=True)[:self.bars]
        self._show_progress(sorted_dirs, lambda stat: stat[0], total=self.info["total-sum"], color="cyan")

    def show_all_top(self):
        self.show_top_extensions()
        self.wait_for_continue()
        self.show_top_directories_by_size()
        self.wait_for_continue()
        self.show_top_directories_by_count()

    def show_full_info(self):
        self.show_general_info()
        self.wait_for_continue()
        self.show_all_top()

    def _show_progress(self, data, value_func, total, color):
        with Progress(console=self.console) as progress:
            for label, stats in data:
                value = value_func(stats)
                percent = ceil((value if isinstance(value, int) else stats[0]) / total * 100)
                progress.add_task(f"[bold {color}]{label}: {value}[/bold {color}]", total=100, completed=percent)


if __name__ == "__main__":
    DiskUsageApp()
