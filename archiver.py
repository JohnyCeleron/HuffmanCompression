import os
import json
import Huffman
import bitarray


class FileCatalogsNotFoundError(Exception):
    def __str__(self):
        return "No such file/catalog in working directory"

def create_archive_folder(working_directory, name, archived_objects):
    if os.path.exists(f'{working_directory}/{name}'):
        raise FileExistsError("An archived folder with this name has already "
                              "been created in the current directory")

    if any(not (os.path.exists(os.path.join(working_directory, object)))
            for object in archived_objects):
        raise FileCatalogsNotFoundError
    # TODO: написать обработку несуществующих файлов и каталогов

    archive_folder = os.path.join(f'{working_directory}', name)
    decoding_meta_file = os.path.join(archive_folder, 'decoding_meta.json')
    binary_archive_file = os.path.join(archive_folder, 'binary_archive.bin')
    os.makedirs(archive_folder)

    decoding_json_dict = dict()
    decoding_json_dict['empty_catalogs'] = dict()
    decoding_json_dict['file_paths'] = dict()

    for object_name in archived_objects:
        object_path = os.path.join(working_directory, object_name)
        for fileCatalog in _get_fileCatalogs(object_path):
            relPath = os.path.relpath(fileCatalog, working_directory)
            if fileCatalog.endswith('.txt'):
                _archive_txt(relPath,
                             working_directory,
                             decoding_json_dict,
                             binary_archive_file)
            elif os.path.isdir(fileCatalog):
                _archive_catalog(relPath, decoding_json_dict)
            else:
                raise ValueError('Unknown format type for archive file')
    _save_meta(decoding_meta_file, decoding_json_dict)


def unarchive_folder(archive_folder_path, destination):
    if not (os.path.exists(archive_folder_path)):
        raise FileNotFoundError("No such archive folder")
    archive_folder_name = os.path.split(archive_folder_path)[1]
    decoding_meta_file = os.path.join(archive_folder_path, 'decoding_meta.json')
    decoding_meta = _get_meta(decoding_meta_file)
    binary_archive_file = os.path.join(archive_folder_path,
                                       'binary_archive.bin')
    unarchive_folder_path = os.path.join(destination,
                                         archive_folder_name + '(Unzip)')
    os.makedirs(unarchive_folder_path)
    number_bits = 0

    for empty_catalog in decoding_meta['empty_catalogs'].keys():
        full_path_catalog = os.path.join(unarchive_folder_path, empty_catalog)
        if not (os.path.exists(full_path_catalog)):
            os.makedirs(full_path_catalog)

    for path in decoding_meta['file_paths'].keys():
        binary_code = bitarray.bitarray()
        full_path_file = os.path.join(unarchive_folder_path, path)
        with open(binary_archive_file, 'rb') as f:
            binary_code.fromfile(f)
        binary_code = binary_code.to01()[
                      number_bits: number_bits +
                                   decoding_meta['file_paths'][path][
                                       'count_bits']]
        number_bits += decoding_meta['file_paths'][path]['count_bits_in_file']
        decoded_text = Huffman.decode(binary_code,
                                      decoding_meta['file_paths'][path][
                                          'decoding_table'],
                                      path)
        if not (os.path.exists(os.path.join(os.path.split(full_path_file)[0]))):
            os.makedirs(os.path.join(os.path.split(full_path_file)[0]))
        with open(full_path_file, 'w+', encoding='utf-8') as f:
            f.write(decoded_text)
        creation_time = decoding_meta['file_paths'][path]['creation_time']
        modification_time = decoding_meta['file_paths'][path][
            'modification_time']
        os.utime(full_path_file, times=(creation_time, modification_time))


def _archive_catalog(catalog,
                     decoding_json_dict):
    decoding_json_dict['empty_catalogs'][catalog] = dict()


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
    decoding_json_dict['file_paths'][fileName]['count_bits_in_file'] = len(
        bit_array) + \
                                                                       (8 - len(
                                                                           bit_array) % 8) % 8
    decoding_json_dict['file_paths'][fileName]['creation_time'] = \
        os.stat(full_path).st_ctime
    decoding_json_dict['file_paths'][fileName]['modification_time'] = \
        os.stat(full_path).st_mtime

    with open(binary_archive_file, 'ab') as f:
        bit_array.tofile(f)


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


def _get_fileCatalogs(path):
    if not (os.path.isdir(path)) or len(os.listdir(path)) == 0:
        yield path
        return
    for root, _, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)
