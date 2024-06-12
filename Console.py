import argparse
import os
from Archiver import create_archive_folder, unarchive_folder


def _execute_archive_command(name, fileNames):
    working_directory = fr'{os.getcwd()}'
    try:
        create_archive_folder(working_directory, name, fileNames)
        print(f'Файлы {fileNames} успешно заархивированы в папку {name}')
    except FileExistsError as e:
        print(e)
    except ValueError as e:
        print(e)


def _execute_unarchive_command(archiveFolder, destination):
    working_directory = os.getcwd()
    archiveFolder_path = os.path.join(working_directory, archiveFolder)
    try:
        unarchive_folder(archiveFolder_path, destination)
        print(f'Папка {archiveFolder} успешно разархивирована в {destination}')
    except ValueError as e:
        print(e)


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
                                  help='Место, куда ты будешь разархивировать файл',
                                  default=os.getcwd())

    args = parser.parse_args()
    if args.command == 'archive':
        _execute_archive_command(args.name, args.fileNames)
    elif args.command == 'unarchive':
        _execute_unarchive_command(args.archiveFolder, args.destination)
    else:
        pass


if __name__ == "__main__":
    main()
    #print(os.getcwd())
    #with open('C:\\Users\\asus\\OneDrive\\Рабочий стол\\MyArchiver\\tex2.txt.txt', 'r+', encoding='utf-8') as f:
         #pass
