import logging

import cryptocode
import random

from app_utilities.crypto_suite.ciphers import Ciphers
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import Algorithms, CipherModes, DatastoreKeyTypes


class CaesarCipherWorkout:
    def __init__(self, build_id, build=None):
        self.build_id = build_id
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=self.build_id)
        self.build = build if build else self.ds.get()
        self.build_type = 'WORKOUT'
        self.ciphertext = [
            'cHrJdEdTf0hyNgw5zF1M5Z0/ITEMcBZBhBQHzNBGBv7o3LvkYb+TjwOjO67FrkXtIIEdLXsqmXXRPagkIMrzEg==*svFn1+TLeh98KnWhiMMBDg==*FOt35Q8pYVsaTzhdpPjlFw==*aCJPMiRxEjwNQhrSlqysiw==',
            'qxHOa703kkPl/7lAcrkg7vO4ls2CeitgI3i6KdqrgvT2*Qci2czk/yYe/CAHdRyysRw==*UGU5zGXgsjpE1YmFEK/gOA==*QIHWApOhCNhdPii7zmwiQQ==',
            'gsER0I6djkzkcMWy4dXm6gMqQIEAWEaY6w5QZcs8JA==*VRgmiO52cs2rhXPyl/JQUA==*UYS5O0NR0PQ+oVHPgiuYlQ==*dcXm+LhIOogUMk6Ai3llUA==',
            'YwSEGVOsr6ETK9RkiDbW/T63YgwMlflejuAHb2D27uWUxxNM+8GyKQNYpvHPF61oAqF2MJx6vm23DlbQsKYDNt3rSozKme2M*Y5H9N0qglUGkPQogEXoWag==*rZYHlsmZHhrL3t/QXQappw==*HEwB7CCansYAnFfkyZp+Iw==',
            'T1qs1d3QeEhOtw0HnYa6Km/4u22C4HxnJo1U3PmmbK3P7RjX1sKQSK/tE21vAmPjeyZHsXkivOLaxnDepsBY*LxgEbXraHwGLcqqWTQ8nJw==*Wm5yQsNBFZexuKh0qNHXgQ==*nB3mcG1/YP3650woabP/rA==',
            'vi0vzFK0kdQxmQmQfNWJ8Z0EhalOWZIl*PLnhb4UJNEjsB77R4jfdpg==*iUAOTNTMla2BUC+Ptlwrxg==*XvNyPHdJbvpsEgpciCTO2A==',
            'pdLsU9mt8b8jAcks0PsVMXLLJ7TI*s3bL+SYzb8a7LO5A28vPpA==*+ngLia29sega2aCNcZVMNg==*5K72D0Sd/LjzFpTWNlT8WQ==',
            'EkqGEBmXlfyqIpRfs/H4arDRddhbyzSci9qiDL/rdxZly9Hf9dpvZT+E81zN/z/I6r+Igw==*n3JelIgumPF5/6U8QWSP5w==*ljH0w3Qew+A0MDHawnj7pg==*dJ0mPniIqx7H/vCq9AIvnQ==',
            '1I0XgyuMKjs1kPk1DQVii5j5jMqiFmfBnPsbGQTmA3Zw0WRGrgRzVk2uLuj3PbOao/O+DAR5j1a3BxWkoZuj/TiSr+/DB++R7A4=*5nK6m5wjd//mpcAme38eJA==*fE+KsmGL0kJr59cewvhw3g==*M4MO0kfYGYRftk9ly0SV5w==',
            'cQrxJ/jtxbAU6LRaMHFhcRitOAKdYk9I8lBtcJJMjdz1BbccFOnHdNBo8cnV4yiwFg4p1g==*t3wlFteyvKkMMu/sUxwFrA==*jpXTlFx/uROFEU4LRrKCcg==*xVdbwGW77gfK+RcVdAh/mw==',
            '5vSfmSSYgrAAVnx1eN/TAk2Gwr7J7bc/5Z2iz2Gdt5cYW8kayzPffBlwuk4zAu0MIQ==*runx4j1oS+EDmqQzTpffIQ==*PsieshpViBqbShXaWS8JoQ==*fNVQW0lGi295x2iXPTYu8g==',
            'yP4Wx01uE43qhDno6t7T3dhrAMttrQohjhD7qX1j2SGRcw==*AraEUK9HFWO9t1XnO5LPOA==*lVRy99cNGPQFulT0eKiOMA==*D5mbvsxKpugrICDLCO1iCw==',
            'xuesxMYtGNWZauNNcaT/WaethacFcQKse/VZyNNbmgnQrjApUxtez6cxYoCZZD/TdaSCUZNF+SKP90GppKnhmPUFTq+euW1YRR5k*WlwVeUOakP8HqXjX0nFEQQ==*+ofoLoHhqFBda7MbIispBg==*Key7If3+PxitkHopiRg/Jw==',
            'n0KJy+51I7tLri7d2/d8IYE8fLXdshDpW0sT0kZT3AZsUfPRg5s=*M4xt8Lgc6PlKESFNt+0UyA==*tcTzgpB3K85Wv79Nvwaa/g==*EJyW/6GQ9l8tVRamYxJl/g==',
            '8ky3P4KzaiapBKSegsOna7RFIIy0cRy/6ndP*Ib9X6xNjJOvD1dWKLBh71w==*30Tp8YFOpENL9TcLTSLKtA==*f19cK1e96JXNs5tnlg/VzQ==',
            'iGN3lzZ9siVuP6BiB/oyMUaTKwc1Xro=*7QBuorkbgqg8AG7VJKK48g==*xwr5VPY1MoqQDlk1KCxFuA==*5p3v7La7vgQZPI6sOZj6IQ==',
            'l2PhriCMAaLjzL6lw09krXdChsfRqGVs27N76PwLYsxDAy3+7ppNkJA+8MT4ATZ621UHQnSQC5tFwtSDtyY=*YlOQAhSxb349lOSqmbfqLA==*2UxT2+s+S9cxm5LD8r70Dw==*24TuHNvrMvvFYNjwGnFWdg==',
            '9SXrAaCYO5RVs1ZysuPKxg84Cuxvnv5p4lFVRDesi54tTdi8tqJ6ioSaig==*ig3XNhkzjep/z7LjKS9Bsg==*G0xLttPhJs5yianF+GeR5w==*zOBj+Xil7SnvdKiMWUYdTg==',
            '3cCIJcW3NtIDibjxejvNLWr2PomtFOr3ZdEc3m/+QScyfKQw5ISGT5QR6CD6VuBnwJrfgnFo*d1JrIY35CEXqKgxhICZ8UA==*YpWtqeEf9/GaTxpdvIb05g==*RnbmvSERZZvtBNhUIwnTvA=='
        ]

    def set(self):
        if self.build:
            assessment = self._get_assessment()
            if self.build['assessment']['questions'][0].get('key', None):
                # If the key exists in the first assessment question, we can assume the values
                # have already been set and return the object
                return self.build
            # Populate assessment questions
            decrypt_key = self.build['assessment']['key']
            count = len(self.build['assessment']['questions'])
            cipher_list = random.sample(self.ciphertext, k=count)
            # Questions haven't been set, generate random ciphers and update entity
            for idx, question in enumerate(self.build['assessment']['questions']):
                key = random.randrange(1, 25)
                message = cryptocode.decrypt(cipher_list[idx], decrypt_key)
                cipher = Ciphers(algorithm=Algorithms.CAESAR, message=message, mode=CipherModes.ENCRYPT, key=key).get()
                question['question'] = cipher['ciphertext']
                question['answer'] = cipher['plaintext']
                question['key'] = cipher['key']
            # Update the datastore entry
            self.ds.put(self.build)
            return self.build
        logging.error(f'No build found with build_id : {self.build_id}')
        return False

    def _get_assessment(self):
        if escape_room := self.build.get('escape_room', None):
            self.build_type = 'ESCAPE_ROOM'
            return self.build['escape_room']['puzzles']
        else:
            self.build_type = 'WORKOUT'
            return self.build['assessment']['questions']
