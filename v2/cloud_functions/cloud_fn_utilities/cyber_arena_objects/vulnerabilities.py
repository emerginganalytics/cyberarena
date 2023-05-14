import gzip
import json
import urllib
from datetime import datetime
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes
from cloud_fn_utilities.gcp.cloud_logger import Logger


class Vulnerabilities:
    def __init__(self, env_dict=None):
        self.key_type = DatastoreKeyTypes.NVD_DATA
        self.env = CloudEnv(env_dict) if env_dict else CloudEnv()
        self.logger = Logger('cloud_functions.vulnerabilities').logger

    def _check_nvd_kind(self):
        """
        :returns True if table needs to be created
        """
        query = DataStoreManager(key_type=self.key_type).query(limit=1)
        if query and query != []:
            return False
        return True

    def update(self):
        ds = DataStoreManager(key_type=self.key_type)
        setup_required = self._check_nvd_kind()
        if setup_required:
            self.logger.info(f"Initializing NVD data with current year of vulnerabilities")
            today = datetime.today()
            url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{today.year}.json.gz"
        else:
            self.logger.info(f"Adding new recent vulnerabilities")
            url = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.gz"
        local_filename = urllib.request.urlretrieve(url)
        json_feed = json.loads(gzip.open(local_filename[0]).read())
        print("Processing ", local_filename)
        cve_list = []
        for cve in json_feed['CVE_Items']:
            try:
                if config := next(iter(cve['configurations']['nodes']), None):
                    if cpe := next(iter(config['cpe_match']), None):
                        cpe_parts = cpe['cpe23Uri'].split(':')
                        cvss = cve["impact"]["baseMetricV3"]["cvssV3"]
                        cve_dict = {
                            'cve_id': cve["cve"]["CVE_data_meta"]["ID"],
                            'vendor': cpe_parts[3],
                            'product': cpe_parts[4],
                            'attack_vector': cvss["attackVector"],
                            'complexity': cvss["attackComplexity"],
                            'priv': cvss["privilegesRequired"],
                            'ui': cvss["userInteraction"],
                            'confidentiality': cvss["confidentialityImpact"],
                            'integrity': cvss["integrityImpact"],
                            'availability': cvss["availabilityImpact"],
                            'description': str(cve["cve"]["description"]["description_data"][0]["value"]),
                        }
                        # Convert dict to Entity and append to cve_list
                        entity = DataStoreManager(key_type=self.key_type, key_id=cve_dict['cve_id'])
                        cve_list.append(entity.entity(cve_dict))
            except KeyError:
                pass

        # Update the table with the new cve list
        ds.put_multi(cve_list)

# [ eof ]
