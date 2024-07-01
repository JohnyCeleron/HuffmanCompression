import argparse
import os
from archiver import create_archive_folder, unarchive_folder


def _execute_archive_command(name, fileNames):
    working_directory = fr'{os.getcwd()}'
    try:
        create_archive_folder(working_directory, name, fileNames)
    except FileExistsError as e:
        print(e)
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    else:
        print(f'Файлы {fileNames} успешно заархивированы в папку {name}')


def _execute_unarchive_command(archiveFolder_path, destination):
    try:
        unarchive_folder(archiveFolder_path, destination)
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    else:
        print(f'Папка {os.path.split(archiveFolder_path)[1]} успешно разархивирована в {destination}')


def main():
    parser = argparse.ArgumentParser(description=
                                     'Свой архиватор, написанный с '
                                     'использование алгоритма Хаффмана')
    # Команда архивирования
    subparsers = parser.add_subparsers(dest="command",
                                       help="Доступные команды")
    archive_parser = subparsers.add_parser('archive',
                                           help="Архивировать файлы")
    archive_parser.add_argument("name", type=str,
                                help="Название архивированного файла")
    archive_parser.add_argument("fileNames", type=str, nargs='+',
                                help="Файлы, которые будут архивироваться")

    # Команда разархивирования
    unarchive_parser = subparsers.add_parser('unarchive',
                                             help='Разархивировать файлы')
    unarchive_parser.add_argument('archiveFolder', type=str,
                                  help='Название папки, которую надо разархивировать')
    unarchive_parser.add_argument('destination', type=str,
                                  help='Место, куда ты будешь разархивировать файл')

    args = parser.parse_args()
    if args.command == 'archive':
        _execute_archive_command(args.name, args.fileNames)
    elif args.command == 'unarchive':
        _execute_unarchive_command(args.archiveFolder, args.destination)
    else:
        pass


if __name__ == "__main__":
    main()