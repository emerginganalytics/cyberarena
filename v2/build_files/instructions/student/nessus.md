# Nessus Vulnerability Scanning
Tenable Nessus is a popular vulnerability scanning tool widely used in cybersecurity operations. It provides comprehensive visibility and insights into the vulnerabilities that exist within an organization's systems.

Nessus is designed to help organizations identify and fix vulnerabilities, configuration issues, and other security-related problems across their networks and endpoints. It conducts scans across a vast range of systems and devices, including networks, databases, operating systems, virtual environments, and cloud infrastructure.

## Accessing Nessus

Start Nessus from your Cyber Arena landing page, if it isn't running already. Then, proceed with the following steps:

1. Click on **Connect** to access your Nessus server.
2. Navigate to the Windows virtual server, and open the Google Chrome browser.
3. The default page should be `https://10.1.1.27:8834`.
4. Login to Nessus using these credentials:
```
user: cybergym
password: Let's workout!
```
## Running a Scan

Below are the detailed steps to run your first scan:

1. Open the Nessus application, and click on **New Scan**, located on the top right.
2. Select **Basic Network Scan**. You will be directed to a form under *New Scan > Basic Network Scan* with three tabs: **Settings**, **Credentials**, and **Plugins**.
3. In the **Settings** tab:
- Provide a name for the scan.
- In the *Target* box, input `10.1.1.10,10.1.1.20` to specify the Windows and Linux servers as the scan targets.
4. Navigate to the **Credentials** tab:
- Select **Windows** and fill in the following credentials:

   ```
   Username: cyberarena
   Password: Let's workout!
   ```

- Next, select SSH credentials. From the *Authentication method* drop-down box, choose password authentication and use the same credentials you configured for Windows.
5. Once all the information is filled, click on **Save**. Your newly created scan should now appear in the *My Scans* list.
6. To start the scan, select it and then click on the **Launch** button located at the top right. The scan should take approximately 10 minutes to complete.
7. After the scan finishes, click on it to view the results.
