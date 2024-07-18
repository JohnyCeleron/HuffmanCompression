import os
import json
import Huffman
import bitarray
from sys import platform
import subprocess
import sys
import asyncio
import datetime


class ArchivedObjectsNotFoundError(Exception):
    def __str__(self):
        return "No such file/catalog in working directory"


def create_archive_folder(working_directory, name, archived_objects):
    if os.path.exists(f'{working_directory}/{name}'):
        raise FileExistsError("An archived folder with this name has already "
                              "been created in the current directory")

    if any(not (os.path.exists(os.path.join(working_directory, object)))
           for object in archived_objects):
        raise ArchivedObjectsNotFoundError

    archive_folder = os.path.join(f'{working_directory}', name)
    decoding_meta_file = os.path.join(archive_folder, 'decoding_meta.json')
    binary_archive_file = os.path.join(archive_folder, 'binary_archive.bin')
    os.makedirs(archive_folder)

    decoding_json_dict = dict()
    decoding_json_dict['empty_catalogs'] = dict()
    decoding_json_dict['file_paths'] = dict()
    decoding_json_dict['catalogs'] = dict()

    for object_name in archived_objects:
        if object_name == name:
            continue
        object_path = os.path.join(working_directory, object_name)
        for file_path in _get_files(object_path):
            relPath = os.path.relpath(file_path, working_directory)
            if file_path.endswith('.txt'):
                _archive_txt(relPath,
                             working_directory,
                             decoding_json_dict,
                             binary_archive_file)
            else:
                raise ValueError(
                    f'Unknown format type for archive file {file_path}')

        for catalog_path in _get_catalogs(object_path):
            relPath = os.path.relpath(catalog_path, working_directory)
            _archive_catalog(working_directory, relPath, decoding_json_dict)

    _save_meta(decoding_meta_file, decoding_json_dict)


def unarchive_folder(archive_folder_path, destination):
    if not (os.path.exists(archive_folder_path)):
        raise FileNotFoundError("No such archive folder")
    archive_folder_name = os.path.split(archive_folder_path)[1]
    unarchive_folder_path = _get_unarchive_folder_path(archive_folder_name,
                                                       destination)
    os.makedirs(unarchive_folder_path)
    _create_catalogs(archive_folder_path, unarchive_folder_path)
    _create_files(archive_folder_path, unarchive_folder_path)
    _set_times_for_catalogs(archive_folder_path, unarchive_folder_path)


def _create_files(archive_folder_path, unarchive_folder_path):
    decoding_meta_file = os.path.join(archive_folder_path, 'decoding_meta.json')
    decoding_meta = _get_meta(decoding_meta_file)
    number_bits = 0
    for file_path in decoding_meta['file_paths'].keys():
        binary_code = bitarray.bitarray()
        full_path_file = os.path.join(unarchive_folder_path, file_path)
        binary_archive_file = os.path.join(archive_folder_path,
                                           'binary_archive.bin')
        with open(binary_archive_file, 'rb') as f:
            binary_code.fromfile(f)
        count_bits = decoding_meta['file_paths'][file_path]['count_bits']
        count_bits_in_file = decoding_meta['file_paths'][file_path][
            'count_bits_in_file']
        decoding_table = decoding_meta['file_paths'][file_path][
            'decoding_table']
        creation_time = decoding_meta['file_paths'][file_path]['creation_time']
        modification_time = decoding_meta['file_paths'][file_path][
            'modification_time']

        binary_code = binary_code.to01()[number_bits: number_bits + count_bits]
        number_bits += count_bits_in_file
        decoded_text = Huffman.decode(binary_code, decoding_table, file_path)

        if not (os.path.exists(os.path.join(os.path.split(full_path_file)[0]))):
            os.makedirs(os.path.join(os.path.split(full_path_file)[0]))
        with open(full_path_file, 'w+', encoding='utf-8') as f:
            f.write(decoded_text)

        try:
            _set_creation_time_file(full_path_file, creation_time)
            _set_modification_time_file(full_path_file, modification_time)
        except OSError as e:
            print(e)


def _set_modification_time_file(path_file, modification_time):
    path_file = os.path.join(os.getcwd(), path_file) \
        if 'pytest' in sys.modules else path_file

    if platform == 'win32':
        command = f"powershell (Get-ChildItem \'{path_file}\').LastWriteTime=\'{modification_time}\'"
    elif platform == 'darwin':
        command = f'SetFile -m "{modification_time}" "{path_file}"'
    else:
        raise OSError(f'Для данной операционной системы не получилось выставить время каталога/файла {path_file}')
    subprocess.run(command, shell=True)


def _set_creation_time_file(path_file, creation_time):
    path_file = os.path.join(os.getcwd(), path_file) \
        if 'pytest' in sys.modules else path_file
    # При тестировании path_file - это относительный путь, а не полный путь

    if platform == 'win32':
        command = f"powershell (Get-ChildItem \'{path_file}\').CreationTime=\'{creation_time}\'"
    elif platform == 'darwin':
        command = f'SetFile -d "{creation_time}" "{path_file}"'
    else:
        raise OSError(f'Для данной операционной системы не получилось выставить время каталога/файла {path_file}')
    subprocess.run(command, shell=True)


def _set_creation_time_catalog(catalog_path, creation_time):
    catalog_path = os.path.join(os.getcwd(), catalog_path) \
        if 'pytest' in sys.modules else catalog_path

    if platform == 'win32':
        command = f"powershell (Get-Item \'{catalog_path}\').CreationTime=\'{creation_time}\'"
    elif platform == 'darwin':
        command = f"" #TODO: написать для macos
    else:
        raise OSError(f'Для данной операционной системы не получилось выставить время каталога/файла {catalog_path}')
    subprocess.run(command, shell=True)
    relative_path = os.path.relpath(catalog_path, os.getcwd())
    print(f'{relative_path}', end='\r')


def _set_modification_time_catalog(catalog_path, modification_time):
    catalog_path = os.path.join(os.getcwd(), catalog_path) \
        if 'pytest' in sys.modules else catalog_path

    if platform == 'win32':
        command = f'powershell (Get-Item \'{catalog_path}\').LastWriteTime=\'{modification_time}\''
    elif platform == 'darwin':
        command = f"" #TODO: написать для macos
    else:
        raise OSError(f'Для данной операционной системы не получилось выставить время каталога/файла {catalog_path}')
    subprocess.run(command, shell=True)
    relative_path = os.path.relpath(catalog_path, os.getcwd())
    print(f'{relative_path}', end='\r')


def _create_catalogs(archive_folder_path, unarchive_folder_path):
    decoding_meta_file = os.path.join(archive_folder_path, 'decoding_meta.json')
    decoding_meta = _get_meta(decoding_meta_file)
    for catalog in decoding_meta['catalogs'].keys():
        full_path_catalog = os.path.join(unarchive_folder_path, catalog)
        if not (os.path.exists(full_path_catalog)):
            os.makedirs(full_path_catalog)


def _set_times_for_catalogs(archive_folder_path, unarchive_folder_path):
    decoding_meta_file = os.path.join(archive_folder_path, 'decoding_meta.json')
    decoding_meta = _get_meta(decoding_meta_file)
    for catalog in decoding_meta['catalogs'].keys():
        full_path_catalog = os.path.join(unarchive_folder_path, catalog)
        creation_time = decoding_meta['catalogs'][catalog]['creation_time']
        modification_time = decoding_meta['catalogs'][catalog]['modification_time']
        _set_creation_time_catalog(full_path_catalog, creation_time)
        _set_modification_time_catalog(full_path_catalog, modification_time)


def _get_unarchive_folder_path(archive_folder_name, destination):
    unarchive_folder_path = os.path.join(destination,
                                         archive_folder_name + '(Unzip)')
    count = 1
    while os.path.exists(unarchive_folder_path):
        unarchive_folder_path = os.path.join(destination,
                                             archive_folder_name + f'(Unzip{count})')
        count += 1
    return unarchive_folder_path


def _archive_catalog(working_directory, catalog, decoding_json_dict):
    decoding_json_dict['catalogs'][catalog] = dict()
    path = os.path.join(working_directory, catalog)
    decoding_json_dict['catalogs'][catalog]['creation_time'] \
        = _get_creation_time(path)
    decoding_json_dict['catalogs'][catalog]['modification_time'] \
        = _get_modifation_time(path)


def _archive_txt(fileName,
                 working_directory,
                 decoding_json_dict,
                 binary_archive_file):
    text = ''
    full_path = os.path.join(working_directory, fileName)
    with open(full_path, 'r+', encoding='utf-8') as f:
        for line in f:
            text += line
    encoding_table = Huffman.get_encoding_table(text)
    if fileName not in decoding_json_dict['file_paths']:
        decoding_json_dict['file_paths'][fileName] = dict()
    decoding_json_dict['file_paths'][fileName]['decoding_table'] = \
        Huffman.swap_dictionary(encoding_table)
    bit_array = bitarray.bitarray(
        Huffman.encode(text, encoding_table, fileName))

    decoding_json_dict['file_paths'][fileName]['count_bits'] = len(bit_array)
    decoding_json_dict['file_paths'][fileName]['count_bits_in_file'] = \
        len(bit_array) + (8 - len(bit_array) % 8) % 8
    decoding_json_dict['file_paths'][fileName]['creation_time'] = \
        _get_creation_time(full_path)
    decoding_json_dict['file_paths'][fileName]['modification_time'] = \
        _get_modifation_time(full_path)

    with open(binary_archive_file, 'ab') as f:
        bit_array.tofile(f)


def _get_creation_time(path):
    current_timestamp = os.stat(path).st_ctime
    return str(datetime.datetime.fromtimestamp(current_timestamp))


def _get_modifation_time(path):
    timestamp = os.stat(path).st_mtime
    return str(datetime.datetime.fromtimestamp(timestamp))


def _save_meta(json_file, meta):
    try:
        with open(json_file, 'w+', encoding='UTF-8') as f:
            json.dump(meta, indent=4, ensure_ascii=False, fp=f)
    except FileNotFoundError:
        print(f"No such json file {json_file}")


def _get_meta(json_file):
    try:
        with open(json_file, 'r+', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"No such json file {json_file}")


def _get_files(path):
    if not (os.path.isdir(path)):
        yield path
        return
    for root, dirs, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)


def _get_catalogs(path):
    if not (os.path.isdir(path)):
        return
    yield path
    for root, dirs, _ in os.walk(path):
        for dir in dirs:
            yield os.path.join(root, dir)