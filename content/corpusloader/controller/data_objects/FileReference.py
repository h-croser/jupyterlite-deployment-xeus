from os.path import join, relpath, dirname, basename
from tempfile import NamedTemporaryFile
from zipfile import ZipFile


class FileReference:
    """
    A general purpose object to hold information regarding a specific file in the file system.
    Folder structure is preserved as a path-like string
    """
    def __init__(self, root_directory: str, directory_path: str, filename: str):
        """
        :param root_directory: the directory from which all files are relative to. This is specified in the CorpusLoader constructor
        :param directory_path: the path to the parent directory of the file. This is not relative to the root_directory
        :param filename: the name and extension of the file, e.g. test.txt
        """
        self.root_directory: str = root_directory
        self.directory_path: str = directory_path
        self.filename: str = filename

    def __eq__(self, other):
        if not isinstance(other, FileReference):
            return False
        return self.get_full_path() == other.get_full_path()

    def __hash__(self):
        return hash(self.get_full_path())

    def __str__(self):
        return self.get_full_path()

    def __repr__(self):
        return self.get_full_path()

    def resolve_real_file_path(self) -> str:
        """
        Provides a real addressable path to the file contents. If the FileReference object is an instance of
        ZipFileReference, the file is extracted, placed in a temporary file, and the temporary file path will be provided
        :return: the full addressable path of the file
        """
        return self.get_full_path()

    def get_full_path(self) -> str:
        """
        :return: the joined directory_path and filename to form the full path of the file
        """
        return join(self.directory_path, self.filename)

    def get_directory_path(self):
        return self.directory_path

    def get_filename(self) -> str:
        return self.filename

    def get_extension(self) -> str:
        if '.' not in self.filename:
            return ''
        return self.filename.split('.')[-1]

    def get_relative_path(self):
        """
        :return: the full path of the file relative to the root_directory
        """
        return relpath(self.get_full_path(), self.root_directory)

    def is_zipped(self) -> bool:
        """
        If True, the file is contained within a zip archive. In this case, the path returned by get_full_path()
        is not a real addressable path, just a string representation of where the file is located. A real addressable
        path can be obtained from resolve_real_file_path()
        :return: True if FileReference object is an instance of ZipFileReference, False otherwise
        """
        return False


class ZipFileReference(FileReference):
    @staticmethod
    def get_zip_internal_file_refs(root_directory: str, zip_file_path: str) -> list[FileReference]:
        """
        Accepts a zip file and the root_directory for files and provides a list of FileReference objects that correspond
        to the zipped files within the zip archive.
        :param root_directory: the directory from which all files are relative to. This is specified in the CorpusLoader constructor
        :param zip_file_path: the path to the zip archive that holds the files to be listed.
        :return: a list of FileReference objects corresponding to the files within the zip archive
        """
        with ZipFile(zip_file_path) as zip_f:
            info_list = zip_f.infolist()

        file_refs: list[FileReference] = []
        for info in info_list:
            if info.is_dir():
                continue
            internal_directory: str = dirname(info.filename)
            filename: str = basename(info.filename)
            zip_ref: FileReference = ZipFileReference(root_directory, zip_file_path, internal_directory, filename)
            file_refs.append(zip_ref)

        return file_refs

    def __init__(self, root_directory: str, zip_file_path: str, internal_directory: str, filename: str):
        """
        :param root_directory: the directory from which all files are relative to. This is specified in the CorpusLoader constructor
        :param zip_file_path: the path to the zip file that holds this zipped file. This is not relative to the root_directory
        :param internal_directory: the path within the zip file to this zipped file
        :param filename: the name and extension of the file, e.g. test.txt
        """
        super().__init__(root_directory, zip_file_path, filename)
        self.internal_directory: str = internal_directory

        self.zip_file = None

    def get_full_path(self) -> str:
        """
        :return: the joined directory_path, internal_directory, and filename to form the full addressable path of the file
        """
        return join(self.directory_path, self.internal_directory, self.filename)

    def is_zipped(self) -> bool:
        """
        If True, the file is contained within a zip archive. In this case, the path returned by get_full_path()
        is not a real addressable path, just a string representation of where the file is located. A real addressable
        path can be obtained from resolve_real_file_path()
        :return: True as FileReference object is an instance of ZipFileReference
        """
        return True

    def resolve_real_file_path(self) -> str:
        """
        Provides a real addressable path to the file contents. The zipped file is extracted,
        placed in a temporary file, and the temporary file path is provided
        :return: the full addressable path of the file
        """
        internal_path = join(self.internal_directory, self.filename)
        zip_file = ZipFile(self.directory_path)
        with zip_file.open(internal_path, force_zip64=True) as zip_f:
            file_content = zip_f.read()
        with NamedTemporaryFile(delete=False) as temp_f:
            temp_f.write(file_content)
            filepath = temp_f.name

        return filepath
