from configparser import ConfigParser
import subprocess
import os
import zipfile
import logging
from logging.handlers import RotatingFileHandler
import shutil


class CustomZip:
    zipfile = None

    def __init__(self, zipname):
        self.zipf = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)

    def zipanything(self, anything):
        if os.path.isdir(anything):
            self.zipdir(anything)
        elif os.path.isfile(anything):
            self.ziponefile(anything)

    def zipdir(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                self.zipf.write(os.path.join(root, file))

    def ziponefile(self, path):
        self.zipf.write(path)

    def close(self):
        self.zipf.close()


class CustomLog:
    log = None

    def __init__(self, level=logging.INFO, name='default_log'):
        self.log = logging.getLogger(name)
        self.log.setLevel(level)
        self.formatter = logging.Formatter('[ %(asctime)s | %(name)s | %(levelname)s ] > %(message)s')

    def set_prod_log(self, logpath = './logs/prod.log'):
        prod_handler = RotatingFileHandler(logpath, 'a', 1000000, 1)
        prod_handler.setFormatter(self.formatter)
        prod_handler.setLevel(logging.DEBUG)
        self.log.addHandler(prod_handler)

    def set_err_log(self, logpath = './logs/error.log'):
        err_handler = RotatingFileHandler(logpath, 'a', 1000000, 1)
        err_handler.setFormatter(self.formatter)
        err_handler.setLevel(logging.ERROR)
        self.log.addHandler(err_handler)

    def set_stream_log(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        self.log.addHandler(stream_handler)


class BorgHelper():
    def __init__(self, borg_ini_path, logger):
        configObject = ConfigParser()
        configObject.read(borg_ini_path)

        app_info = configObject["APP"]
        borg_info = configObject["BORG"]

        self.repo = borg_info['repo_path']
        self.passphrase = borg_info['passphrase']
        self.dir_list = borg_info['dir_list']
        self.db_list = borg_info['db_list']
        self.logger = logger

    def create_repo(self):
        if os.path.exists(self.repo):
            directory = os.listdir(self.repo)
            if len(directory) > 0:
                raise Exception(f"Le répertoire {self.repo} existe déjà et il n'est pas vide.")
        file = None
        try:
            os.putenv("BORG_PASSPHRASE", self.passphrase)
            res = subprocess.check_output(['borg', 'init', '--encryption=repokey', self.repo], stderr=subprocess.STDOUT)
            self.logger.info(f'Create borg repo: {res}')
        except Exception as err:
            self.logger.error(f'Error {err}')
        else:
            self.logger.info(f'[+] {self.repo} created.')
        finally:
            if file:
                file.close()

    @classmethod
    def compress(cls, type, path):
        my_zip = CustomZip("{}.zip".format(path))
        if type == 'mysql' or type == 'psql':
            my_zip.ziponefile(path)
            my_zip.close()
            os.remove(path)
        else:
            my_zip.zipdir(path)
            my_zip.close()
            shutil.rmtree(path)

    def __repr__(self):
        '''
        Verification paramètres
        '''
        return f"{self.repo} - {self.passphrase} - {self.dir_list} - {self.db_list}"
