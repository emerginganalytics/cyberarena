import pymysql
import json
import urllib
import gzip
from datetime import datetime
import ssl

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.cloud_logger import Logger


class Vulnerabilities:
    class DatabaseCommands:
        INSERT_VULNERABILITY = """
            INSERT IGNORE INTO nvd_data (cve_id, vendor, product, attack_vector, complexity, 
            priv, ui, confidentiality, integrity, availability, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    def __init__(self):
        self.env = CloudEnv()
        self.logger = Logger("cloud_functions.vulnerabilities").logger
        self.dbcon = pymysql.connect(host=self.env.sql_ip, user="root", password=self.env.sql_password, db='cybergym',
                                     charset='utf8mb4')

    def nvd_update(self):
        """
        Instantiated by cloud function to keep the CVEs current in the cloud SQL database
        """
        dbcur = self.dbcon.cursor()

        setup_required = self._test_and_create_nvd_table()

        if setup_required:
            self.logger.info(f"Initializing NVD data with current year of vulnerabilities")
            today = datetime.today()
            url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{today.year}.json.gz"
        else:
            self.logger.info(f"Adding new recent vulnerabilities")
            # url = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz"
            url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-2022.json.gz"
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
                        cvss = cve["impact"]["baseMetricV3"]["cvssV3"]
                        attack_vector = cvss["attackVector"]
                        complexity = cvss["attackComplexity"]
                        priv = cvss["privilegesRequired"]
                        ui = cvss["userInteraction"]
                        confidentiality = cvss["confidentialityImpact"]
                        integrity = cvss["integrityImpact"]
                        availability = cvss["availabilityImpact"]
                        vuln_description = self.dbcon.escape(cve["cve"]["description"]["description_data"][0]["value"])

                        vuln_args = (
                            cve_id, cpe_vendor, cpe_product, attack_vector, complexity, priv, ui, confidentiality,
                            integrity, availability, vuln_description
                        )
                        dbcur.execute(self.DatabaseCommands.INSERT_VULNERABILITY, vuln_args)
            except KeyError:
                pass
        self.dbcon.commit()
        dbcur.close()


    def _test_and_create_nvd_table(self):
        """
        The database is created through a gcloud script for new Cyber Gym projects. This function sets up
        the database if necessary.

        :returns: True if the database needed to set up and otherwise False
        """
        dbcur = self.dbcon.cursor()
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
