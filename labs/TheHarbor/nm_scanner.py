import nmap


def scanner(client):

    status = []
    open_port = []
    check_port = [22, 53, 80, 5901, 6001]

    nm = nmap.PortScanner()
    nm.scan(str(client), arguments='-p T: 135, 445, 1840, 5000')

    for proto in nm[client].all_protocols():
        open_port = nm[client][proto].keys()
        status.append(nm[client]['state'])

    print(status)

    if sorted(open_port) == sorted(check_port):
        return True            # return flag
    else:
        return False           # return fw_error


# open_port = []
#   check_port = [22, 53, 80, 631, 3306, 5901, 6001, 8080]
#    check_port = [135, 445, 1840, 5000]
#
#    scan_port = nmap.portScanner()
#    scan_port.scan(client, '1,10000')
#
#    for host in scan_port.all_hosts():
#        open_port.append(scan_port[host].keys())
#
#    if sorted(open_port) == sorted(check_port):
#        return render_template(flag)
#    else:
#        return render_template(fw_error)
#
