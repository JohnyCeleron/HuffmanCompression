import subprocess


TIME_TYPES = ['creation_time', 'modification_time']


class SetterTimeFactory:
    @classmethod
    def set_file_time(cls, path, time, time_type):
        if time_type not in TIME_TYPES:
            raise TypeError(f'Нельзя установить время типа {time_type} для файла')
        cls._set_file_time(path, time, time_type)

    @classmethod
    def set_catalog_time(cls, path, time, time_type):
        if time_type not in TIME_TYPES:
            raise TypeError(f'Нельзя установить время типа {time_type} для каталога')
        cls._set_catalog_time(path, time, time_type)


class WindowsSetterTime(SetterTimeFactory):
    @staticmethod
    def _set_file_time(path, time, time_type):
        command = {
            'creation_time': f"powershell (Get-ChildItem \'{path}\').CreationTime=\'{time}\'",
            'modification_time': f"powershell (Get-ChildItem \'{path}\').LastWriteTime=\'{time}\'"
        }
        subprocess.run(command[time_type], shell=True)

    @staticmethod
    def _set_catalog_time(path, time, time_type):
        command = {
            'creation_time': f"powershell (Get-Item \'{path}\').CreationTime=\'{time}\'",
            'modification_time': f'powershell (Get-Item \'{path}\').LastWriteTime=\'{time}\''
        }
        subprocess.run(command[time_type], shell=True)


class MacOSSetterTime(SetterTimeFactory):
    @staticmethod
    def _set_file_time(path, time, time_type):
        command = {
            'creation_time': f'SetFile -d "{time}" "{path}"',
            'modification_time': f'SetFile -m "{time}" "{path}"'
        }
        subprocess.run(command[time_type], shell=True)

    @staticmethod
    def _set_catalog_time(self, path, time, time_type):
        pass


setter_time_by_platform = {
    'win32': WindowsSetterTime,
    'darwin': MacOSSetterTime
}