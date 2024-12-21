import platform
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from math import ceil
import os
import subprocess

from DiskUsageAnalyzer import DiskAnalyzer


class Main:
    def __init__(
        self,
        bars: int = 10,
        directory: str = os.getcwd(),
        mode: int = 7,
        extensions: list = [],
    ):
        self.d_bars = bars
        self.directory = directory
        self.start_dir = directory
        self.platform = platform.system().lower()
        self.console = Console()
        self.infos = DiskAnalyzer(self.platform)
        self.extensions = extensions
        self.info: ...
        self.mode = mode
        #
        self.run()

    def run(self):
        self.console.print(
            "Натисніть Enter щоб почати: (Консоль буде очищено !) ", end=""
        )
        #
        input("")
        #
        self.clear()
        self.enter_path(part=False)
        #
        while True:
            self.get_mode()
            #
            match self.mode:
                case 0:
                    self.console.print('[red]Enter "exit" to close')
                    while (inp := input(":")) != "exit":
                        subprocess.run(inp, shell=True, cwd=self.directory, text=True)
                case 1:
                    self.mode_1()
                case 2:
                    self.mode_2()
                case 3:
                    self.mode_3(self.d_bars)
                case 4:
                    self.mode_4(self.d_bars)
                case 5:
                    self.mode_5(self.d_bars)
                case 6:
                    self.mode_3(self.d_bars)
                    self.wait()
                    self.mode_4(self.d_bars)
                    self.wait()
                    self.mode_5(self.d_bars)
                case 7:
                    self.mode_1()
                    self.wait()
                    self.mode_2()
                    self.wait()
                    self.mode_3(self.d_bars)
                    self.wait()
                    self.mode_4(self.d_bars)
                    self.wait()
                    self.mode_5(self.d_bars)
                case 8:
                    self.enter_path(part=True)
                case 9:
                    self.enter_bars()
                case 10:
                    self.console.print(
                        "[green]Введіть розширення через кому (Enter для всіх): ",
                        end="",
                    )
                    self.extensions = input("").replace(" ", "").split(",") or None
                    print(self.extensions)
                    self.info = self.infos.get_info(
                        directory=self.directory,
                        extensions=self.extensions,
                        detail_level=2,
                        debug=False,
                    )
                case _:
                    break
            #
            print()
            self.wait()
            self.clear()

    def wait(self):
        if self.platform == "windows":
            os.system("pause")
        else:
            self.console.print("Натисніть Ентер щоб продовжити ", end="")
            input(":")

    def clear(self):
        if self.platform == "windows":
            os.system("cls")
            # os.system("mode con: cols=130 lines=30")
        else:
            # os.system("stty cols 130 rows 30")
            os.system("clear")

    def enter_path(self, part=False):
        if part:
            self.console.print(
                "[green]Введіть шлях в директорії '/шлях у папці' (Enter для кореневої директорії): ",
                end="",
            )
            dir = input("") or None
            if dir is None:
                self.directory = self.start_dir
            else:
                self.directory += dir
            os.chdir(self.directory)
            self.info = self.infos.get_info(
                directory=self.directory,
                extensions=self.extensions,
                detail_level=2,
                debug=False,
            )
        else:
            self.console.print(
                "[green]Введіть шлях директорії (Enter для кореневої директорії): ",
                end="",
            )

            self.directory = input("") or self.directory
            self.start_dir = self.directory
            self.info = self.infos.get_info(
                directory=self.directory,
                extensions=self.extensions,
                detail_level=2,
                debug=False,
            )

    def enter_bars(self):
        self.console.print(
            "[green]Введіть нову кількість позицій для діаграм: ", end=""
        )
        try:
            self.d_bars = int(input("") or 10)
        except ValueError:
            self.console.print(
                "[red]Помилка, не правильний тип значення (Має бути простим числом)"
            )

    def get_mode(self):
        self.console.print(
            """
0: Ввести команду;
1: Загальна інфа про диски;
2: Таблиця по дискам;
3: Топ-x найбільш часто зустрічаються розширень;
4: Топ-x найбільших директорій за вагою;
5: Топ-x директорій з найбільшими кількостями файлів;
6: Усі Топ-x;
7: Уся інфа; 
8: Зміна директорії;
9: Змінити кількість позицій діаграм (за замовч. 10);
10: Вибрати розширення для скану;
інш. або Літера: Вихід;
"""
        )
        self.console.print("[green]Введіть потрібний варіант: ", end="")
        try:
            self.mode = int(input("") or 7)
        except ValueError:
            exit(0)

    def mode_1(self):
        # Показуємо інформацію по файлам
        self.console.print(f'[red]{"Файли":-^130}')
        largest_by_size = max(
            self.info["dicts"].items(), key=lambda x: x[1][1], default=None
        )
        largest_by_count = max(
            self.info["dicts"].items(), key=lambda x: x[1][0], default=None
        )
        most_frequent_extension = max(
            self.info["exts"].items(), key=lambda x: x[1][0], default=None
        )

        self.console.print("[red]\n# Результати аналізу ↓")
        self.console.print(f"[green]--> Директорія аналізу: {self.directory}")
        self.console.print(f'[green]--> Кількість файлів: {self.info["total-sum"]}')
        self.console.print(
            f'[blue]--> Загальний вага файлів (GB): {self.info["total-weight"] / (1e+9):.6f} GB\n'
        )

        if largest_by_size:
            self.console.print("# Найбільша директорія за вагою ↓")
            self.console.print(
                f"[blue]--> Директорія: {largest_by_size[0]}, Вага: {largest_by_size[1][1] / (1e+9):.6f} GB\n"
            )

        if largest_by_count:
            self.console.print("# Найбільша директорія за кількістю файлів ↓")
            self.console.print(
                f"[blue]--> Директорія: {largest_by_count[0]}, Кількість файлів: {largest_by_count[1][0]}\n"
            )

        if most_frequent_extension:
            self.console.print("# Найчастіше розширення ↓")
            self.console.print(
                f"[blue]--> Розширення: {most_frequent_extension[0]}, Кількість файлів: {most_frequent_extension[1][0]}"
            )

    def mode_2(self):
        # ДИСКИ
        self.console.print(f'\n[red]{"Диски":-^130}')
        table = Table(title="Диски")
        table.add_column("Назва")
        table.add_column("Загальна пам'ять")
        table.add_column("Зайнята пам'ять")
        table.add_column("Вільна пам'ять")
        table.add_column("Пам'ять у відсотках")
        table.add_column("Формат диска")
        table.add_column("Тип (права)")

        for disk in self.info["disks-info"]:
            formatted_disk = [str(value) for value in disk]
            table.add_row(*formatted_disk)

        self.console.print(table)

    def mode_3(self, bars: int = 10):
        self.console.print("\n# Топ-x найбільш часто зустрічаються розширень ↓")
        sorted_exts = sorted(
            self.info["exts"].items(), key=lambda x: x[1][0], reverse=True
        )[:bars]

        with Progress(console=self.console) as progress:
            for ext, stats in sorted_exts:
                progress.add_task(
                    f"[bold green]{ext} : {stats[0]}[/bold green]",
                    total=100,
                    completed=ceil(stats[0] / self.info["total-sum"] * 100),
                )

    def mode_4(self, bars: int = 10):
        self.console.print("\n# Топ-x найбільших директорій за вагою ↓ (GB)")
        sorted_dirs = sorted(
            self.info["dicts"].items(), key=lambda x: x[1][1], reverse=True
        )[:bars]

        with Progress(console=self.console) as progress:
            for dir_path, stats in sorted_dirs:
                progress.add_task(
                    f"[bold yellow]{dir_path} : {stats[1] / (1e+9):.6f}[/bold yellow]",
                    total=100,
                    completed=ceil(stats[1] / self.info["total-weight"] * 100),
                )

    def mode_5(self, bars: int = 10) -> None:
        self.console.print("\n# Топ-x директорій з найбільшими кількостями файлів ↓")
        sorted_dirs_by_count = sorted(
            self.info["dicts"].items(), key=lambda x: x[1][0], reverse=True
        )[:bars]

        with Progress(console=self.console) as progress:
            for dir_path, stats in sorted_dirs_by_count:
                progress.add_task(
                    f"[bold cyan]{dir_path} : {stats[0]}[/bold cyan]",
                    total=100,
                    completed=ceil(stats[0] / self.info["total-sum"] * 100),
                )


if __name__ == "__main__":
    Console = Main()
    Console.run()
