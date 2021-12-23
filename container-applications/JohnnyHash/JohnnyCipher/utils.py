import cryptocode
import random
from globals import ds_client, publish_status
from Ciphers.caesarcipher import CaesarCipher
from Ciphers.substitution_cipher import substitution_encrypt


class CaesarCipherBuilder:
    """
    Class to handle creation and validation of caesar ciphers and caesar
    cipher submissions. Actual cipher generation is handled by calling the
    Ciphers.caesarcipher.CaesarCipher class
    """
    def __init__(self, workout_id):
        self.workout_id = workout_id

    def set_ciphers(self):
        """
        Picks random ciphertext from clear_text list and enciphers it with a
        random Caesar cipher. The generated ciphers are added to the associated
        workout datastore entry.

        :arg: workout_id: type(str)
        :return: cipher_list: type(list)
        """
        key = ds_client.key('cybergym-workout', self.workout_id)
        workout = ds_client.get(key)

        result = []
        ciphertext = [
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

        decrypt_key = workout['assessment']['key']
        for pos in range(len(ciphertext)):
            key = random.randrange(1, 25)
            clear_text = cryptocode.decrypt(ciphertext[pos], decrypt_key)
            cipher_string = CaesarCipher(clear_text, offset=key).encoded

            cipher = {
                'key': key,
                'cipher': cipher_string,
            }
            result.append(cipher)

        # Selects 3 unique ciphers from list
        cipher_list = random.sample(result, k=3)

        workout['container_info']['cipher_one'] = cipher_list[0]
        workout['container_info']['cipher_two'] = cipher_list[1]
        workout['container_info']['cipher_three'] = cipher_list[2]

        ds_client.put(workout)
        return cipher_list

    def check_caesar(self, submission, check):
        """
        :arg submission: type(str); Plaintext cipher sent from student
        :arg check: type(int); Question number associated with submitted cipher
        :returns data: type(dict) of updated workout obj that is stored in Datastore
        """
        key = ds_client.key('cybergym-workout', self.workout_id)
        workout = ds_client.get(key)

        # data is a dict list that is passed back to page as JSON object
        status = workout['assessment']['questions']
        data = {
            'cipher1': {
                'cipher': workout['container_info']['cipher_one']['cipher'],
                'status': status[0]['complete']
            },
            'cipher2': {
                'cipher': workout['container_info']['cipher_two']['cipher'],
                'status': status[1]['complete']
            },
            'cipher3': {
                'cipher': workout['container_info']['cipher_three']['cipher'],
                'status': status[2]['complete']
            },
        }

        # Cipher list is what we compare submissions to
        cipher_list = []

        # Decode Stored Ciphers and append to a plaintext list
        decoded = workout['container_info']['cipher_one']['cipher']
        plaintext = CaesarCipher(decoded, offset=workout['container_info']['cipher_one']['key']).decoded
        cipher_list.append(plaintext)

        decoded2 = workout['container_info']['cipher_two']['cipher']
        plaintext2 = CaesarCipher(decoded2, offset=workout['container_info']['cipher_two']['key']).decoded
        cipher_list.append(plaintext2)

        decoded3 = workout['container_info']['cipher_three']['cipher']
        plaintext3 = CaesarCipher(decoded3, offset=workout['container_info']['cipher_three']['key']).decoded
        cipher_list.append(plaintext3)

        # Check if submission exists within cipher_list and update status and call publish_status if correct
        if check == 1 and submission in cipher_list:
            data['cipher1']['status'] = True
            workout_key = workout['assessment']['questions'][0]['key']
            publish_status(self.workout_id, workout_key)
        elif check == 2 and submission in cipher_list:
            data['cipher2']['status'] = True
            workout_key = workout['assessment']['questions'][1]['key']
            publish_status(self.workout_id, workout_key)
        elif check == 3 and submission in cipher_list:
            data['cipher3']['status'] = True
            workout_key = workout['assessment']['questions'][2]['key']
            publish_status(self.workout_id, workout_key)

        return data


class SubstitutionCipherBuilder:
    """
    Class to handle initiation and validation of substitution ciphers.
    The ciphers are created by calling Ciphers.substitution_cipher.substitution_encrypt.
    """
    def __init__(self, workout_id):
        self.workout_id = workout_id

    def set_sub_cipher(self):
        """
        arg: str(workout_id)
        :return:
        """
        key = ds_client.key('cybergym-workout', self.workout_id)
        workout = ds_client.get(key)

        # TODO: Randomly select message from list of messages
        message = "a/0TTGJzT7y6GncKO+bXA82HlWXbhyRf3O2tRtqMG+xq/zncd5aXG/Ku9vwsA4cXJzZN7aT7Qi" \
                   "1QAqUTQ9LNRlGfhw6noVXCVgLVKnoHX2E4p3TU4buuDNAhwsmBCjaPydmVDbXznR8BCeqtc7rb" \
                   "1WDB9DM/L8mKi+rJ2IyK3tubrh5lQxoicJaFTS3/3uNbdoF5oAQwK9qXLrCDFSeEuxH9x6fLx/" \
                   "jw1VPdZyiaMBqhCKJzIxXXrk1x3AjzsGHes4PN2HmwLHTPabatjpdc+7++HoX0WYS3uFDtlnqq" \
                   "/30VCtHVhj7/9/5G8kM+2SCr9uVnOFoUVac2k8lA9S654LJ/SvNxoJIAnnN8kmRB3hTHUy+hLz" \
                   "INSCi94HXzRKegF6l2cqDzIzax3AkEvMEDrnr9SyKl4kPbJUhpS9rsIHSR4VZ+ftTl6OyQyYcU" \
                   "8PISQ3LbMDlab3kRLQMyQLUE6P1W3dSb2d0E8FMzNJRVZG8qni31EJDdhEE1XoeN5KNuOqHlUg" \
                   "YnEQTnnnZQO7cpZHbJkig+*rMa79jvw3ZAdCPVmTXHlWg==*dr8W9+jtjlpUMx3aXteeQw==*O" \
                   "yOuE5XXG9jLU2HwvJchNw=="
        decrypt_key = workout['assessment']['key']
        plaintext = cryptocode.decrypt(message, decrypt_key)
        cipher = substitution_encrypt(plaintext)

        # Put cipher in datastore object
        workout['container_info']['sub_cipher']['cipher'] = cipher['ciphertext']
        workout['container_info']['sub_cipher']['cleartext'] = cipher['cleartext']
        workout['container_info']['sub_cipher']['key'] = cipher['key']
        ds_client.put(workout)

        status = workout['assessment']['questions'][3]['complete']
        data = {
            'cipher': cipher['ciphertext'],
            'status': status,
        }
        return data

    def check_sub_cipher(self, submission):
        key = ds_client.key('cybergym-workout', self.workout_id)
        workout = ds_client.get(key)
        data = {
            'message': workout['container_info']['sub_cipher']['cipher'],
            'status': ''
        }

        if submission == workout['container_info']['sub_cipher']['cleartext']:
            data['status'] = True
            workout_key = workout['assessment']['questions'][3]['key']
            publish_status(self.workout_id, workout_key)
        return data
