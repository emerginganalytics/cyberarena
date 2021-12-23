from google.cloud import runtimeconfig
from common.globals import log_client
import pymysql
import json
import urllib
import gzip
from datetime import datetime
import ssl


def test_and_create_nvd_table(dbcon):
    """
    The database is created through a gcloud script for new Cyber Gym projects. This function sets up
    the database if necessary.
    :param dbconn: The connection object for the database
    :returns: True if the database needed to set up and otherwise False
    """
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = 'nvd_data'
        """)
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return False

    dbcur.execute("""
        CREATE TABLE nvd_data(
            cve_id varchar(255) primary key,
            vendor varchar(255), 
            product varchar(255),
            attack_vector varchar(255), 
            complexity varchar(255), 
            priv varchar(255), 
            ui varchar(255), 
            confidentiality varchar(255), 
            integrity varchar(255), 
            availability varchar(255), 
            description varchar(1024)) 
    """)
    dbcur.close()
    return True



def nvd_update():
    """
    Instantiated by cloud function to keep the CVEs current in the cloud SQL database
    """
    g_logger = log_client.logger("nvd_update")
    runtimeconfig_client = runtimeconfig.Client()
    myconfig = runtimeconfig_client.config('cybergym')
    mysql_password = myconfig.get_variable('sql_password').value.decode("utf-8")
    mysql_ip = myconfig.get_variable('sql_ip').value.decode("utf-8")

    dbcon = pymysql.connect(host=mysql_ip,
                                 user="root",
                                 password=mysql_password,
                                 db='cybergym',
                                 charset='utf8mb4')
    dbcur = dbcon.cursor()

    setup_required = test_and_create_nvd_table(dbcon)

    sql_insert_vuln = """
                    INSERT IGNORE INTO nvd_data (cve_id, vendor, product, attack_vector, complexity, 
                    priv, ui, confidentiality, integrity, availability, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

    if setup_required:
        g_logger.log_text(f"Initializing NVD data with current year of vulnerabilities")
        today = datetime.today()
        url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{today.year}.json.gz"
    else:
        g_logger.log_text(f"Adding new recent vulnerabilities")
        url = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz"
    ssl._create_default_https_context = ssl._create_unverified_context
    local_filename = urllib.request.urlretrieve(url)
    json_feed = json.loads(gzip.open(local_filename[0]).read())
    print("Processing ", local_filename)
    for cve in json_feed["CVE_Items"]:
        try:
            if len(cve['configurations']['nodes']) > 0:
                if len(cve['configurations']['nodes'][0]['cpe_match']) > 0:
                    cpe = cve['configurations']['nodes'][0]['cpe_match'][0]
                    cpe_parts = cpe['cpe23Uri'].split(':')
                    cpe_vendor = cpe_parts[3]
                    cpe_product = cpe_parts[4]
                    cve_id = cve["cve"]["CVE_data_meta"]["ID"]
                    cwe = cve['cve']['problemtype']['problemtype_data'][0]['description'][0]['value']
                    cvss = cve["impact"]["baseMetricV3"]["cvssV3"]
                    attack_vector = cvss["attackVector"]
                    complexity = cvss["attackComplexity"]
                    priv = cvss["privilegesRequired"]
                    ui = cvss["userInteraction"]
                    confidentiality = cvss["confidentialityImpact"]
                    integrity = cvss["integrityImpact"]
                    availability = cvss["availabilityImpact"]
                    vuln_description = dbcon.escape(cve["cve"]["description"]["description_data"][0]["value"])

                    vuln_args = (cve_id, cpe_vendor, cpe_product, attack_vector, complexity, priv, ui, confidentiality,
                                 integrity, availability, vuln_description)
                    dbcur.execute(sql_insert_vuln, vuln_args)
        except KeyError:
            pass
    dbcon.commit()
