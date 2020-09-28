import json
import urllib
import gzip


def get_vulnerabilities(cpe):
    """

    """
    url = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-2017.json.gz"
    local_filename = urllib.request.urlretrieve(url)
    json_feed = json.loads(gzip.open(local_filename[0]).read())
    print("Processing ", local_filename)
    for cve in json_feed["CVE_Items"]:
        try:
            if len(cve['configurations']['nodes']) > 0:
                cpe = cve['configurations']['nodes'][0]['cpe_match'][0]
                cpe_parts = cpe['cpe23Uri'].split(':')
                vendor = cpe_parts[3]
                product = cpe_parts[4]
                cve_id = cve["cve"]["CVE_data_meta"]["ID"]
                cwe = cve['cve']['problemtype']['problemtype_data'][0]['description'][0]['value']
                cvss = cve["impact"]["baseMetricV3"]["cvssV3"]
                attack_vector = cvss["attackVector"]
                complexity = cvss["attackComplexity"]
                privileges = cvss["privilegesRequired"]
                ui = cvss["userInteraction"]
                confidentiality = cvss["confidentialityImpact"]
                integrity = cvss["integrityImpact"]
                availability = cvss["availabilityImpact"]
                vuln_description = cve["cve"]["description"]["description_data"][0]["value"]
                exploitability = vulners_check(cve_id)

            # row[COL_VENDOR], row[COL_PRODUCT], row[COL_ATTACK], row[COL_COMPLEXITY],
            # row[COL_UI], row[COL_PRIVILEGES], row[COL_CONFIDENTIALITY], row[COL_INTEGRITY],
            # row[COL_AVAILABILITY], row[COL_CWE]
        except KeyError:
            pass

        # Create a dictionary to find the vendor/product with the most number of vulnerabilities
        product_key = vendor + ':' + product
        if product_key in vuln_counts:
            vuln_counts[product_key]["vuln_count"] += 1
        else:
            vuln_counts[product_key] = {"vuln_count": 1, "exploits": 0}

        # Add exploitability counts
        if exploitability:
            vuln_counts[product_key]["exploits"] += 1