from flask import Blueprint, render_template


faqs_app = Blueprint('faq', __name__, url_prefix="/faq", static_folder="./static", template_folder="./templates")


@faqs_app.route('/', methods=['GET'])
def faq():
    return render_template('faq.html')


@faqs_app.route('/cyberattack', methods=['GET'])
def cyberattack_faq():
    return render_template('cyberattack_faq.html')


@faqs_app.route('/ransomware', methods=['GET'])
def ransomware_faq():
    return render_template('ransomware_faq.html')


@faqs_app.route('/dos', methods=['GET'])
def dos_faq():
    return render_template('dos_faq.html')


@faqs_app.route('/johnnyhash', methods=['GET'])
def johnnyhash_faq():
    return render_template('johnnyhash_faq.html')


@faqs_app.route('/johnnycipher', methods=['GET'])
def johnnycipher_faq():
    return render_template('johnnycipher_faq.html')


@faqs_app.route('/mobileforensics', methods=['GET'])
def mobileforensics_faq():
    return render_template('mobileforensics_faq.html')


@faqs_app.route('/trust', methods=['GET'])
def trust_faq():
    return render_template('trust_faq.html')


@faqs_app.route('/nessus', methods=['GET'])
def nessus_faq():
    return render_template('nessus_faq.html')


@faqs_app.route('/bufferoverflow', methods=['GET'])
def bufferoverflow_faq():
    return render_template('fbufferoverflow_faq.html')


@faqs_app.route('/publicprivate', methods=['GET'])
def publicprivate_faq():
    return render_template('publicprivate_faq.html')


@faqs_app.route('/wireshark', methods=['GET'])
def wireshark_faq():
    return render_template('wireshark_faq.html')


@faqs_app.route('/2fa', methods=['GET'])
def twofa_faq():
    return render_template('2fa_faq.html')


@faqs_app.route('/access-control', methods=['GET'])
def accesscontrol_faq():
    return render_template('access-control_faq.html')


@faqs_app.route('/arena_snake', methods=['GET'])
def arena_snake_faq():
    return render_template('arena_snake_faq.html')


@faqs_app.route('/hiddennode', methods=['GET'])
def hiddennode_faq():
    return render_template('hiddennode_faq.html')


@faqs_app.route('/inspect', methods=['GET'])
def inspect_faq():
    return render_template('inspect_faq.html')


@faqs_app.route('/kersplunk', methods=['GET'])
def kersplunk_faq():
    return render_template('kersplunk_faq.html')


@faqs_app.route('/missionpermissions2', methods=['GET'])
def missionpermissions2_faq():
    return render_template('missionpermissions2_faq.html')


@faqs_app.route('/password-policy', methods=['GET'])
def passwordpolicy_faq():
    return render_template('password-policy_faq.html')


@faqs_app.route('/phishing', methods=['GET'])
def phishing_faq():
    return render_template('phishing_faq.html')


@faqs_app.route('/reversus', methods=['GET'])
def reversus_faq():
    return render_template('reversus_faq.html')


@faqs_app.route('/shodan', methods=['GET'])
def shodan_faq():
    return render_template('shodan_faq.html')


@faqs_app.route('/sql_injection', methods=['GET'])
def sql_injection_faq():
    return render_template('sql_injection_faq.html')


@faqs_app.route('/xss', methods=['GET'])
def xss_faq():
    return render_template('xss_faq.html')
