import string
import random
import re
import requests
import io
import faker


# TODO:
# user agent randomizer
def genRnd(characters_n, population=string.ascii_letters+ string.digits, characters_n_variation=0):
    assert characters_n > characters_n_variation

    v = characters_n + random.randint(-characters_n_variation, characters_n_variation)

    s = random.choices(population, k=v)

    return ''.join(s)


class Diesi:
    def __init__(self, host):
        self.base = f'http://{host}'
        self.sess = requests.Session()
        self.sess.headers.update({'User-Agent': 'checker'})

    def login(self, username, password):
        URL = self.base + '/login.php'

        data = {
            'username': username,
            'password': password
        }

        return self.sess.post(URL, data=data)

    def login_checked(self, username: str, password: str) -> None:
        r = self.sess.post(f'{self.base}/login.php', data={
            'username': username,
            'password': password,
        })
        if username not in r.text:
            raise RuntimeError(f'API login error, content: {r.text}')

    def register(self, username, password):
        URL = self.base + '/register.php'

        data = {
            'username': username,
            'password': password
        }

        return self.sess.post(URL, data=data)

    def register_checked(self, username: str, password: str) -> None:
        r = self.sess.post(f'{self.base}/register.php', data={
            'username': username,
            'password': password,
        })
        if username not in r.text:
            raise RuntimeError(f'API register error, content: {r.text}')

    def logout(self):
        URL = self.base + '/logout.php'

        return self.sess.get(URL)

    def write(self, title, body):
        URL = self.base + '/write.php'

        data = {
            'title': title,
            'body': body
        }

        return self.sess.post(URL, data = data)

    def list(self):
        URL = self.base + '/list.php'

        return self.sess.get(URL)

    def read(self, id):
        URL = self.base + '/read.php'
        data = {
            'id' : id
        }
        return self.sess.get(URL, params=data)

    def hsm_import_key(self, key: bytes) -> int:
        r = self.sess.post(f'{self.base}/settings.php', files={
            'key': io.BytesIO(key),
        })
        key_id_match = re.search(r'Imported key ID: <b>([1-9][0-9]*)</b>', r.text)
        if key_id_match is None:
            raise RuntimeError(f'API HSM import key error, content: {r.text}')
        return int(key_id_match.group(1))

    def hsm_import_item(self, item: bytes) -> int:
        r = self.sess.post(f'{self.base}/write_secret.php', files={
            'document': io.BytesIO(item),
        })
        item_id_match = re.search(r'Item ID: <b>([1-9][0-9]*)</b>', r.text)
        if item_id_match is None:
            raise RuntimeError(f'API HSM import item error, content: {r.text}')
        return int(item_id_match.group(1))

    def hsm_get_item(self, item_id: int, share_token: bytes) -> bytes:
        r = self.sess.post(f'{self.base}/read_secret.php', data={
            'item_id': item_id,
        }, files={
            'share_token': io.BytesIO(share_token),
        })
        if r.status_code == 500:
            raise RuntimeError(f'API HSM get item error: {r.text.strip()}')
        r.raise_for_status()
        return r.content
