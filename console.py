import argparse
import os
from archiver import create_archive_folder, unarchive_folder
from archiver import ArchivedObjectsNotFoundError


#TODO: (user friendly interface) научиться вызывать программу без прописывания "py ...."
def _execute_archive_command(archiveFolderName, archivedObjectNames):
    working_directory = fr'{os.getcwd()}'
    if archivedObjectNames[0] in '*':
        archivedObjectNames = [object_name for object_name in
                               os.listdir(working_directory)]
    try:
        create_archive_folder(working_directory, archiveFolderName,
                              archivedObjectNames)
    except ArchivedObjectsNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    except FileExistsError:
        print(fr'Архивированный файл с именем {archiveFolderName} уже создан')
    else:
        print(
            f'Файлы/Каталоги {archivedObjectNames} успешно заархивированы в папку {archiveFolderName}')


def _execute_unarchive_command(archiveFolder_path, destination):
    def is_archiveFolderName_in_working_directory():
        return os.path.exists(os.path.join(os.getcwd(), archiveFolder_path))

    if is_archiveFolderName_in_working_directory():
        archiveFolder_path = os.path.join(os.getcwd(), archiveFolder_path)

    if destination == '':
        destination = os.path.split(archiveFolder_path)[0]
    try:
        unarchive_folder(archiveFolder_path, destination)
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    else:
        print(
            f'Папка {os.path.split(archiveFolder_path)[1]} успешно разархивирована в {destination}')


def main():
    parser = argparse.ArgumentParser(description=
                                     'Свой архиватор, написанный с '
                                     'использование алгоритма Хаффмана')
    # Команда архивирования
    subparsers = parser.add_subparsers(dest="command",
                                       help="Доступные команды")
    archive_parser = subparsers.add_parser('archive',
                                           help="Архивировать файлы/папки")
    archive_parser.add_argument("archiveFolderName", type=str,
                                help="Название папки, куда будут архивироваться файлы/папки")
    archive_parser.add_argument("archivedObjectNames", type=str, nargs='+',
                                help="Файлы/папки, которые будут архивироваться")

    # Команда разархивирования
    unarchive_parser = subparsers.add_parser('unarchive',
                                             help='Разархивировать файлы')
    unarchive_parser.add_argument('archiveFolderPath', type=str,
                                  help='Путь до папки, которую надо разархивировать')
    unarchive_parser.add_argument('--destination', type=str, default='',
                                  help='Место, куда ты будешь разархивировать файл')

    args = parser.parse_args()
    if args.command == 'archive':
        _execute_archive_command(args.archiveFolderName,
                                 args.archivedObjectNames)
    elif args.command == 'unarchive':
        _execute_unarchive_command(args.archiveFolderPath, args.destination)
    else:
        pass


if __name__ == "__main__":
    main()
