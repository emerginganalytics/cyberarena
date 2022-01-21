# Build Locker
### How to work with build specifications and teacher instructions having answer key information
All build-spec and teacher instruction files are encrypted with AES encryption before they are uploaded 
to any public facing storage. To handle the encryption and decryption of these files, you can use the `BuildLocker` class
found in `/build-files/build-update-scripts/build_locker`.    

This class can be called one of two ways, as a script or imported
as a class.   

### Encrypting/Decrypting Files by Script   
Navigate to `cyberarena/build-files/build-update-scripts/` to run the script.

Script options:   
   - `-m` or `--mode`: Either `'encrypt'` or `'decrypt'`   
   - `-t` or `--type`: Either `'instructions'` or `'specs'`   
   - `-p` or `--password`: Password used to encrypt and decrypt files   

Example calls:   
   - Windows: `python ./build_locker.py -m 'decrypt' -t 'specs' -p '<your-password-here>'`   
   - *nix: `python3 ./build_locker.py -m 'decrypt' -t 'specs' -p '<your-password-here>'`   

   
### Encrypting/Decrypting Files by class   
```python
from pathlib import Path
from build_locker import BuildLocker

input_directory = Path("../build-files/workout-specs/needs-encrypted")
output_directory = Path("../workout-specs")
mode = 'encrypt'
pwd = 'YOUR-PASSWORD-HERE'
doc_type = 'specs'

BuildLocker(input_dir=input_directory, output_dir=output_directory,
                pwd=pwd, mode=mode, doc_type=doc_type)
```   

It is encouraged to encrypt all unencrypted teacher instruction and workout-spec files before pushing to any public repository or Cloud bucket. This helps
protect the integrity of any workout keys stored in the files.   

