import os
import subprocess
import time

import win32net
import win32security

import tkinter as tk
from tkinter.font import Font
from tkinter import messagebox

from cert_manager import CertManager
from privilege_checker import PrivilegeChecker, Roles

class RebelGlobals:
    INSTRUCTIONS = "In a galaxy far, far away, you are a skilled system administrator responsible for managing the" \
                   " server infrastructure of the Rebel Base. As the Rebel Alliance grows and evolves, the server's " \
                   "access control has become cluttered and needs cleanup to ensure security and efficiency.\n" \
                   "\n" \
                   "You begin with an access control audit, reviewing the existing user accounts, groups, and " \
                   "permissions on the server. There are numerous outdated accounts, former Rebel members who have " \
                   "left the organization, and redundant permissions that are no longer necessary.\n" \
                   "\n" \
                   "If you are a Youngling Jedi, use the force to begin the cleanup process. Start by removing the " \
                   "user accounts of former Rebel members or suspicious members of the Dark Side.\n" \
                   "\n" \
                   "If you are a Padawan, perform the activities of the younling but also identify and remove " \
                   "unnecessary group memberships that appear to be no longer needed.\n" \
                   "\n" \
                   "Then, if you are a Jedi Master, continue to further enhance security and strengthen access " \
                   "control by applying the principle of least privilege in a role-based access control system. " \
                   "Open the Rebel Plans folder at C:\Rebel Plans and ensure only groups have permissions, " \
                   "and the group access is appropriate according to the following policies:\n" \
                   "1. The Jedi Council should have full access to all strategic plans and mission reports\n" \
                   "2. The Rebel Alliance Leaders must have full access to mission reports and read/write " \
                   "permissions to the strategic plans\n" \
                   "3. Pilots must be able to read-only permission to mission reports and full writes to flight logs, " \
                   "starship specificaions and navigation charts.\n" \
                   "4. Engineers must have full access to all technical documentation, design blueprints, and " \
                   "maintenance schedules.\n" \
                   "5. Only Rebel Alliance Leaders can have access to the alliance budgets.\n" \
                   "\n" \
                   "As the Rebel Base's system administrator, your diligent efforts to clean up the access control " \
                   "system play a vital role in safeguarding critical resources, protecting sensitive information, " \
                   "and ensuring the secure operation of the Rebel Alliance's infrastructure."


class RebelBaseForm:
    HYPERLINK_BUTTON_STYLE = {
        "foreground": "blue",
        "underline": True,
        "borderwidth": 0,
        "activebackground": "white",
        "activeforeground": "blue",
        "cursor": "hand2"
    }

    def __init__(self):
        self.cert_manager = CertManager()

        self.window = tk.Tk()
        self.window.title("Rebel Base Access Control Mission")
        self.image = tk.PhotoImage(file="img/jedi-master-on-a-computer.png")
        self.bold_heading2_font = Font(family="Arial", size=14, weight="bold")
        self.normal_font = Font(family="Arial", size=11)
        canvas = tk.Canvas(self.window, width=500, height=500)

        # Create the form elements
        instructions = tk.Button(self.window, text="Your Mission", command=self.show_instructions,
                                 font=self.bold_heading2_font, **self.HYPERLINK_BUTTON_STYLE)
        label1 = tk.Label(self.window, text="Click the button associated with your experience level after you have "
                                            "completed your mission. If you successfully completed the mission, you "
                                            "will receive the passcode to unlock your certificate",
                          font=self.bold_heading2_font, wraplength=500)
        youngling_button = tk.Button(self.window, text="Youngling Assessment", font=self.normal_font,
                                     command=self.youngling_assessment)
        padawan_button = tk.Button(self.window, text="Padawan Assessment", font=self.normal_font,
                                   command=self.padawan_assessment)
        jedi_button = tk.Button(self.window, text="Jedi Master Assessment", font=self.normal_font,
                                command=self.jedi_assessment)

        # Pack the self.window
        instructions.pack()
        canvas.pack()
        label1.pack()
        canvas.create_image(0, 0, image=self.image, anchor="nw")
        youngling_button.pack(side="left")
        padawan_button.pack(side="left")
        jedi_button.pack(side="left")

    def render(self):
        self.window.mainloop()

    def youngling_assessment(self):
        users_to_delete = ['orson', 'grevious', 'darth', 'watto']
        old_users_deleted = True
        for user in users_to_delete:
            command = f"net user {user}"
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                old_users_deleted = False
                break
        if old_users_deleted:
            self.cert_manager.decrypt_youngling_cert()
            self.show_certificate(CertManager.CertFiles.YOUNGLING)
        else:
            messagebox.showinfo("Keep trying you must...", "You are missing some users that should be removed")



    def padawan_assessment(self):
        remove_group_accounts = {
            "Rebel Alliance Leaders": ['han', 'orson', 'grievous'],
            "Pilots": ["jarjar", "darth", "dooku"],
            "Engineers": ["watto"],
            "Jedi Council": ["luke", "r2d2", "darth", "dooku"]
        }

        users_remaining = 0
        group_removed = None
        for group_name in remove_group_accounts:
            try:
                group_info = win32net.NetLocalGroupGetMembers(None, group_name, 2)
            except:
                group_removed = group_name
                break

            for member_info in group_info[0]:
                try:
                    if member_info['domainandname'].split("\\")[-1] in remove_group_accounts[group_name]:
                        users_remaining += 1
                except TypeError:
                    continue

        if not users_remaining:
            self.cert_manager.decrypt_padawan_cert()
            self.show_certificate(CertManager.CertFiles.PADAWAN)
        elif group_removed:
            messagebox.showinfo("Keep trying you must...",
                                f"Uh oh! The group {group_removed} was deleted! Please add it back and try again")
        else:
            messagebox.showinfo("Keep trying you must...",
                                f"Keep Trying. You have {users_remaining} users remaining to remove")

    def jedi_assessment(self):
        base_folder = "C:\\Rebel Forces"
        correct_folder_acl = {
            'Alliance Budgets': {
                'Rebel Alliance Leaders': Roles.FULL_ACCESS
            },
            'Design Blueprints': {
                'Engineers': Roles.FULL_ACCESS
            },
            'Flight Logs': {
                'Pilots': Roles.FULL_ACCESS,
                'Engineers': Roles.READ_ONLY
            },
            'Maintenance Schedules': {
                'Engineers': Roles.FULL_ACCESS
            },
            'Mission Reports': {
                'Jedi Council': Roles.FULL_ACCESS,
                'Rebel Alliance Leaders': Roles.FULL_ACCESS,
                'Pilots': Roles.READ_ONLY
            },
            'Navigational Charts': {
                'Pilots': Roles.FULL_ACCESS
            },
            'Starship Specifications': {
                'Pilots': Roles.FULL_ACCESS,
                'Engineers': Roles.FULL_ACCESS
            },
            'Strategic Plans': {
                'Jedi Council': Roles.FULL_ACCESS,
                'Rebel Alliance Leaders': Roles.READ_WRITE
            },
            'Technical Documentation': {
                'Engineers': Roles.FULL_ACCESS
            }
        }

        privileges_correct = True
        too_many_privileges = False
        missing_folder = False
        for folder in correct_folder_acl:
            # Get the security descriptor of the folder
            try:
                security_descriptor = win32security.GetFileSecurity(os.path.join(base_folder, folder),
                                                                    win32security.DACL_SECURITY_INFORMATION)
            except:
                missing_folder = True
                break

            # Get the discretionary access control list (DACL) from the security descriptor
            dacl = security_descriptor.GetSecurityDescriptorDacl()

            # Iterate over each access control entry (ACE) in the DACL
            for i in range(dacl.GetAceCount()):
                ace = dacl.GetAce(i)
                sid = ace[2]
                access_mask = ace[1]

                # Get the user account associated with the SID
                try:
                    account_name, domain, account_type = win32security.LookupAccountSid(None, sid)
                except Exception as e:
                    continue
                if account_name in correct_folder_acl[folder]:
                    role = correct_folder_acl[folder][account_name]
                    if not PrivilegeChecker(role=role, access_mask=access_mask).check_permissions():
                        privileges_correct = False
                        break
                else:
                    if domain not in ['NT Authority']:
                        too_many_privileges = True
                        break

        if privileges_correct and not too_many_privileges and not missing_folder:
            self.cert_manager.decrypt_jedi_cert()
            self.show_certificate(CertManager.CertFiles.JEDI)
        elif missing_folder:
            messagebox.showinfo("I've got a bad feeling about this...", f"You are missing the folder {folder}")
        elif too_many_privileges:
            messagebox.showinfo("Keep trying you must...",
                                f"Uh oh! It looks like the folder {folder} has too many users and groups.")
        else:
            messagebox.showinfo("Keep trying you must...", f"There are incorrect permissions on the folder {folder}")

    def show_instructions(self):
        self.instructions_window = tk.Toplevel(self.window)
        self.instructions_window.title("Instructions")
        label1 = tk.Label(self.instructions_window, text="Your Instructions", font=self.bold_heading2_font,
                          anchor="w", justify="left")
        label2 = tk.Label(self.instructions_window, text=RebelGlobals.INSTRUCTIONS, anchor="w", font=self.normal_font,
                          justify="left", wraplength=600)
        label1.pack()
        label2.pack()
        self.instructions_window.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.instructions_window.destroy()

    def show_certificate(self, certificate):
        subprocess.run(['start', '', f"certs/{certificate}"], shell=True)


def main():
    # Your main code here
    RebelBaseForm().render()


if __name__ == "__main__":
    main()
