import datetime
import json
import os
import sys
from sys import platform

from bitarray import bitarray

from src import Huffman
from src.setter_time import setter_time_by_platform


class ArchivedObjectsNotFoundError(Exception):
    def __str__(self):
        return "No such file/catalog in working directory"


def create_archive_folder(working_directory, archiver_name, archived_objects):
    if os.path.exists(os.path.join(working_directory, archiver_name)):
        raise FileExistsError("An archived folder with this name has already "
                              "been created in the current directory")

    if any(not (os.path.exists(os.path.join(working_directory, object)))
           for object in archived_objects):
        raise ArchivedObjectsNotFoundError
    _has_unknown_extension_files(working_directory, archived_objects)

    archive_folder = os.path.join(f'{working_directory}', archiver_name)
    decoding_meta_file = os.path.join(archive_folder, 'decoding_meta.json')
    os.makedirs(archive_folder)
    decoding_json_dict = _create_decoding_json_dict()
    binary_archive_file = os.path.join(archive_folder, 'binary_archive.bin')

    for object_name in archived_objects:
        if object_name == archiver_name:
            pass
        object_path = os.path.join(working_directory, object_name)
        _archive_files(binary_archive_file, decoding_json_dict, object_path,
                       working_directory)
        _archive_catalogs(decoding_json_dict, object_path, working_directory)
    _save_meta(decoding_meta_file, decoding_json_dict)


def _has_unknown_extension_files(working_directory, archived_objects):
    files = (archive_object for archive_object in archived_objects if
             os.path.isfile(os.path.join(working_directory, archive_object)))
    AVAILABLE_EXTENSIONS = ['.txt']
    for file in files:
        _, extension = os.path.splitext(file)
        if extension not in AVAILABLE_EXTENSIONS:
            raise ValueError(f'Unknown extension for archive file {file}')


def _create_decoding_json_dict():
    decoding_json_dict = dict()
    decoding_json_dict['file_paths'] = dict()
    decoding_json_dict['catalogs'] = dict()
    return decoding_json_dict


def _archive_catalogs(decoding_json_dict, object_path, working_directory):
    for catalog_path in _get_catalogs(object_path):
        relPath = os.path.relpath(catalog_path, working_directory)
        _archive_catalog(working_directory, relPath, decoding_json_dict)


def _archive_files(binary_archive_file, decoding_json_dict, object_path,
                   working_directory):
    for file_path in _get_files(object_path):
        relPath = os.path.relpath(file_path, working_directory)
        if file_path.endswith('.txt'):
            _archive_txt(relPath,
                         working_directory,
                         decoding_json_dict,
                         binary_archive_file)


def unarchive_folder(archive_folder_path, destination):
    if not (os.path.exists(archive_folder_path)):
        raise FileNotFoundError("No such archive folder")
    if not (os.path.exists(os.path.join(archive_folder_path, 'binary_archive.bin'))) and \
            not (os.path.exists(os.path.join(archive_folder_path, 'decoding_meta.json'))):
        raise FileNotFoundError("It isn't archive folder")
    archive_folder_name = os.path.split(archive_folder_path)[1]
    unarchive_folder_path = _get_unarchive_folder_path(archive_folder_name,
                                                       destination)
    os.makedirs(unarchive_folder_path)
    _create_catalogs(archive_folder_path, unarchive_folder_path)
    _create_files(archive_folder_path, unarchive_folder_path)
    try:
        _set_time_for_files(archive_folder_path, unarchive_folder_path)
        _set_times_for_catalogs(archive_folder_path, unarchive_folder_path)
    except OSError as e:
        print(e)


def _create_files(archive_folder_path, unarchive_folder_path):
    decoding_meta_file = os.path.join(archive_folder_path, 'decoding_meta.json')
    decoding_meta = _get_meta(decoding_meta_file)
    binary_archive_file = os.path.join(archive_folder_path,
                                       'binary_archive.bin')

    number_bits = 0
    for file_path in decoding_meta['file_paths'].keys():
        binary_code = _get_binary_code_form_file(binary_archive_file)
        full_path_file = os.path.join(unarchive_folder_path, file_path)

        count_bits = decoding_meta['file_paths'][file_path]['count_bits']
        count_bits_in_file = decoding_meta['file_paths'][file_path][
            'count_bits_in_file']
        decoding_table = decoding_meta['file_paths'][file_path][
            'decoding_table']

        binary_code = binary_code.to01()[number_bits: number_bits + count_bits]
        number_bits += count_bits_in_file
        decoded_text = Huffman.decode(binary_code, decoding_table, file_path)

        if not (os.path.exists(os.path.join(os.path.split(full_path_file)[0]))):
            os.makedirs(os.path.join(os.path.split(full_path_file)[0]))
        with open(full_path_file, 'w+', encoding='utf-8') as f:
            f.write(decoded_text)


def _get_binary_code_form_file(binary_file):
    binary_code = bitarray()
    with open(binary_file, 'rb') as f:
        binary_code.fromfile(f)
    return binary_code


def _set_time_for_files(archive_folder_path, unarchive_folder_path):
    decoding_meta_file = os.path.join(archive_folder_path, 'decoding_meta.json')
    decoding_meta = _get_meta(decoding_meta_file)
    for file_path in decoding_meta['file_paths'].keys():
        full_path_file = os.path.join(unarchive_folder_path, file_path)
        full_path_file = os.path.join(os.getcwd(), full_path_file) \
            if 'pytest' in sys.modules else full_path_file
        # При тестировании path_file - это относительный путь, а не полный путь

        creation_time = decoding_meta['file_paths'][file_path]['creation_time']
        modification_time = decoding_meta['file_paths'][file_path][
            'modification_time']

        if platform not in setter_time_by_platform:
            raise OSError(
                "It was not possible to set the time of the files in this operating system")

        setter_time = setter_time_by_platform[platform]
        setter_time.set_file_time(full_path_file, creation_time,
                                  'creation_time')
        setter_time.set_file_time(full_path_file, modification_time,
                                  'modification_time')


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
        modification_time = decoding_meta['catalogs'][catalog][
            'modification_time']
        full_path_catalog = os.path.join(os.getcwd(), full_path_catalog) \
            if 'pytest' in sys.modules else full_path_catalog

        if platform not in setter_time_by_platform:
            raise OSError(
                'It was not possible to set the time of the catalogs in this operating system')

        setter_time = setter_time_by_platform[platform]
        setter_time.set_catalog_time(full_path_catalog, creation_time,
                                     'creation_time')
        setter_time.set_catalog_time(full_path_catalog, modification_time,
                                     'modification_time')


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
    full_path = os.path.join(working_directory, fileName)
    text = _get_text_from_file(full_path)
    encoding_table = Huffman.get_encoding_table(text)
    if fileName not in decoding_json_dict['file_paths']:
        decoding_json_dict['file_paths'][fileName] = dict()

    decoding_table = Huffman.swap_dictionary(encoding_table)
    decoding_json_dict['file_paths'][fileName][
        'decoding_table'] = decoding_table

    bit_array = bitarray(Huffman.encode(text, encoding_table, fileName))
    decoding_json_dict['file_paths'][fileName]['count_bits'] = len(bit_array)
    decoding_json_dict['file_paths'][fileName]['count_bits_in_file'] = \
        len(bit_array) + (8 - len(bit_array) % 8) % 8
    decoding_json_dict['file_paths'][fileName]['creation_time'] = \
        _get_creation_time(full_path)
    decoding_json_dict['file_paths'][fileName]['modification_time'] = \
        _get_modifation_time(full_path)

    with open(binary_archive_file, 'ab') as f:
        bit_array.tofile(f)


def _get_text_from_file(file_path):
    text = ''
    with open(file_path, 'r+', encoding='utf-8') as f:
        for line in f:
            text += line
    return text


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
