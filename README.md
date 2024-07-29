# Собственный архиватор, основанный на алгоритме сжатия Хаффмана
Автор: Попов Михаил (LDG200@yandex.ru)


__Описание__:
Данное консольное приложение позволяет архивировать и разархивировать текстовые файлы и папки

__Инструкция__:
1. Перед использование архиватора надо перейти в тот каталог (который будем называть рабочим), где будут хранится файлы и каталоги, которые мы хотим заархивировать
2. Для того, чтобы каждый раз не прописывать **длинный путь до исполняемого .py файла**, а писать просто `HUFFMAN` в консоли, надо добавить путь до каталога с этим проектом в PATH:
    * `C:<path>\HuffmanCompression` - это тот путь, который надо добавить в PATH
    * В командной строке пишем `set path=%path%;C:<path>\HuffmanCompression` - эта команда добавляет наш путь в PATH (Это команда работает на windows) (Можно ещё вручную добавить наш путь в PATH)

__Команды__: 
* archive [archive_folder_name] [archive_objects]
    * `archive` - архивировать файлы / каталоги
    * `archive_folder_name` - имя папки, в которую мы хотим заархивировать файлы / каталоги
    * `archive_objects` - файлы / каталоги, которые мы хотим заархивировать в рабочей директории (Если archive_objects = '*', то архивироваться будут все файлы/каталоги в рабочей директории)
    ```sh
    HUFFMAN archive MYZIP text1.txt folder text2.txt
    ```
    ```sh
    HUFFMAN archive MYZIP *
    ```
* unarchive [archive_folder] --destination [destination]
    * `unarchive` - разархивировать папку
    * `archive_folder` - имя или путь заархивированной папки. Если указано **просто имя**, то в рабочей директории ищется папка с именем `archive_folder`
    * `destination` - путь, куда будет разархивироваться папка. По умолчанию папка будет разархивироваться в той директории, где была определена архивированная папка `archive_folder`
    ```sh
    HUFFMAN unarchive MYZIP --destination "C:<destination path>"
    ```
    ```sh
    HUFFMAN unarchive MYZIP
    ```
    ```sh
    HUFFMAN unarchive "C:<archive folder path>"
    ```
__Подробности реализации:__
В папке `src` находятся модули, отвечающие за логику приложения:
* `Huffman.py` отвечает за алгоритм сжатия файлов
* `console.py` отвечает за взаимодействие с консолью
* `setter_time.py` устанавливает время для папок и файлов
* `archiver.py` содержит логику архиватора
На модули `Huffman.py` и `archiver.py` написаны тесты, которые можно найти в папке `tests`. Покрытие по строкам составляет около 94 %:

| Name           | Stmts | Miss | Cover |
|----------------|-------|------|-------|
| Huffman.py     | 93    | 4    | 96%   |
| archiver.py    | 178   | 9    | 95%   |
| setter_time.py | 31    | 5    | 84%   |
| Total          | 302   | 18   | 94%   |
