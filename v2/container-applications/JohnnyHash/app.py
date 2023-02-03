from flask import Flask, redirect

from JohnnyHash.utils import gen_pass
from JohnnyHash.routes import johnnyhash
import os

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(johnnyhash)


# Loader Route; Used to determines which Blueprint to use
@app.route('/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'johnnycipher':
            if workout['container_info']['cipher_one']['cipher'] == '':
                CaesarCipherBuilder(workout_id=workout_id).set_ciphers()
                SubstitutionCipherBuilder(workout_id=workout_id).set_sub_cipher()
            return redirect(f'/johnnycipher/caesar/{workout_id}')
        elif workout['type'] == 'johnnyhash':
            if workout['container_info']['correct_password'] == '':
                gen_pass(workout_id)
            return redirect(f'/johnnyhash/hash_it_out/{workout_id}')
        elif workout['type'] == 'Trojan Arena Level 2':
            return redirect(f'/arena/cipher-warehouse/{workout_id}')
        elif workout['type'] == 'GenCyber Arena Level 1':
            # temp route used only for GenCyber Arena. Merge this with JohnnyArena for future arena builds
            get_arena_sub_cipher()
            return redirect(f'/johnnyGenCipher/substitution/{workout_id}')
    else:
        return redirect('/johnnyhash/invalid')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get(port=5000)))
