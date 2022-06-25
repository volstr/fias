import re
import zipfile

import xmltodict


def rows_from_xml(archive: zipfile.ZipFile, file_name: str):
    file = archive.open(file_name)
    tags = ''
    while True:
        data = file.read(10000)
        if not data:
            break
        try:
            str_data = data.decode(encoding='utf-8')
        except UnicodeDecodeError:
            data += file.read(1)
            str_data = data.decode(encoding='utf-8')
        # Читаем блоками, поэтому пытаемся воссоздать изначальную последовательность
        tags += str_data
        # Находим все теги "<...>"
        result = re.compile(r"(?:<).*?(?:>)").findall(tags)
        # Удаляем все найденные теги
        tags = re.sub(r'\<[^>]*\>', '', tags)

        for i in result:
            # Нас интересуют только одиночные теги с атрибутами (<.../>)
            # if re.compile(r"<(.*?)/>").findall(i):
            if re.compile(r'<(.*?)"(.*?)/>').findall(i):
                obj = xmltodict.parse(i, dict_constructor=dict)
                yield obj[list(obj.keys())[0]]
