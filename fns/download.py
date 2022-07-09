import copy
import os
from typing import Dict, List
from urllib.parse import urlparse
from urllib.request import urlretrieve

import requests as requests

from core.log import import_log
from core.settings import settings


def get_str_file_size(size: int):
    size_metric = {
        1024 * 1024 * 1024 * 1024: 'ТБ',
        1024 * 1024 * 1024: 'ГБ',
        1024 * 1024: 'МБ',
        1024: 'КБ',
    }

    for key in size_metric:
        if size >= key:
            return f'{(size / key):.2f} {size_metric[key]}'
    return f'{size} Б'


def get_updates_file_list(version: int = None) -> List[Dict]:
    """
    Получить список обновлений, который нужен именно нам
    """
    url = settings.update.url
    data = []
    try:
        import_log.info(f'Текущая версия {version}')
        import_log.info(f'Проверка наличия обновлений базы {url}')
        response = requests.get(url)
        if response.ok:
            # Новые обновления всегда вверху
            data = list(response.json())
            if not version:
                # Если база пустая - возвращаем последнюю актуальную версию
                data = list(filter(lambda x: x['GarXMLFullURL'], data))
                version = 0

            data = list(filter(lambda x: x['VersionId'] > version and x['GarXMLDeltaURL'], data))
            if not version:
                data = data[0: 1]
            else:
                data.reverse()
            # log.debug(json.dumps(data, indent=4, ensure_ascii=False))
            import_log.info(f'Доступно файлов: {len(data)}')
        else:
            import_log.error(f'{response} {response.text}')
    except Exception as e:
        import_log.error(f'{e}')

    return data


def download_update(file_obj: Dict, delta: bool = True) -> Dict:
    """
    Скачать файлы обновлений или изначальный файл, если delta = False
    """
    file_info = dict()
    try:
        url = file_obj['GarXMLDeltaURL'] if delta else file_obj['GarXMLFullURL']
        local_filename = f"{file_obj['VersionId']}_{os.path.basename(urlparse(url).path)}"
        try:
            headers = {'Content-Length': 0}
            for _ in range(5):
                try:
                    import_log.info(f'Загрузка {url} > {local_filename}')
                    _, headers = urlretrieve(url, local_filename)
                    break
                except Exception as e:
                    import_log.error(f'Не удалось скачать файл {url}\n{e}')

            size = int(headers.get('Content-Length', 0))
            file_info = copy.deepcopy(file_obj)
            file_info['File'] = local_filename
            import_log.info(f'Загрузка файла завершена. Размер файла: {get_str_file_size(size)}')
        except Exception as e:
            # Если какой-то файл не скачали - попробуем это сделать в следующий раз.
            # Работаем с тем что смогли скачать
            import_log.error(f'{e}')
            try:
                os.remove(local_filename)
            except OSError as e:
                import_log.error(f'{e}')
                raise e
            raise e
    except Exception as e:
        import_log.error(f'{e}')

    return file_info
