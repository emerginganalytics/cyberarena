import os
import re
import yaml
from sense_hat import SenseHat
from sys import argv
from time import sleep
from tkinter import Tcl

sense_hat = SenseHat()

# load project config
with open('/usr/src/cyberarena-dev/config.yaml') as file:
    config = yaml.full_load(file)


class ImageToPixmap(object):
    '''
        This is a utility class used to mass generate image maps for
        the SenseHat display. This is intended to reduce the load of
        generating maps for a larger sequence of images.
    '''
    class Images:
        heart = '/usr/src/cyberarena-dev/images/heart/'
        heartrate = '/usr/src/cyberarena-dev/images/heartrate/'
        arrow = '/usr/src/cyberarena-dev/images/arrow/'
        road = '/usr/src/cyberarena-dev/images/road/'
        alerts = '/usr/src/cyberarena-dev/images/alerts/'
        faces = '/usr/src/cyberarena-dev/images/faces/'
        phase = '/usr/src/cyberarena-dev/images/phase/'
        lock = '/usr/src/cyberarena-dev/images/lock/'

    def __init__(self, **kwargs):
        self.target_dir = None
        self.image = None
        self.images = {
            'heart': '/usr/src/cyberarena-dev/images/heart/',
            'heartrate': '/usr/src/cyberarena-dev/images/heartrate/',
            'arrow': '/usr/src/cyberarena-dev/images/arrow/',
            'road': '/usr/src/cyberarena-dev/images/road/',
            'alerts': '/usr/src/cyberarena-dev/images/alerts/',
            'faces': '/usr/src/cyberarena-dev/images/faces/',
            'phase': '/usr/src/cyberarena-dev/images/phase/',
            'lock': '/usr/src/cyberarena-dev/images/lock/',
        }
        
        if 'target_dir' in kwargs:
            self.target_dir = kwargs['target_dir']
            self.name = kwargs['name']
        self.write_to_file()

    def atoi(self, msg):
        return int(msg) if msg.isdigit() else msg

    def natural_keys(self, msg):
        return [ self.atoi(c) for c in re.split('(\d+)', msg) ]

    def get_image_paths(self, target_dir):
        image_paths_list = []
        temp_list = []
        # __, __, filenames = next(os.walk(target_dir))
        filenames = os.listdir(target_dir)

        # sort filenames by alphabetical + numerical order
        sorted_list = filenames.sort(key=self.natural_keys)
        # create full file name and append to return list
        for image in filenames:
            image_paths_list.append(f'{target_dir}{image}')
        return image_paths_list

    def get_image_maps(self):
        # loads target_dir from config file
        image_maps = {}
        img_conf = config['images']
        
        if not self.target_dir or self.image:
            for name in img_conf:
                images = []
                # get image paths
                image_list = self.get_image_paths(img_conf[name])
                # gen maps for image_list
                for image in image_list:
                    _map = sense_hat.load_image(image)
                    images.append(_map)
                image_maps[name] = images
        elif self.target_dir and not self.image:
            images = []
            image_list = self.get_image_paths(self.target_dir)
            for image in image_list:
                _map = SenseHat.load_image(image)
                images.append(_map)
            image_maps[self.name] = images
        else:
            _map = SenseHat.load_image(self.image)
            image_maps[self.name] = _map
        return image_maps
    
    def write_to_file(self):
        '''
            takes generated image maps and inserts them into
            python dict with the dir name as the key. We then
            append the results to the image_maps.py file
        '''
        write_to = '/usr/src/cyberarena-dev/image_maps.py'
        image_maps = self.get_image_maps()

        with open(write_to, 'w') as f:
            f.write(f'ImageMaps = {repr(image_maps)}\n')
        print('[+] Image maps updated!')


if __name__ == '__main__':
    # target_dir or image: (target_dir/image path)
    action = argv[1]
    
    if action == 'target_dir':
        print('[*] loading pixmap for target dir ...')
        # key name to store maps under
        name = argv[2]
        ImageToPixmap(target_dir=action, name=name)
    else:
        print('[*] loading pixmaps from config ...')
        ImageToPixmap()
