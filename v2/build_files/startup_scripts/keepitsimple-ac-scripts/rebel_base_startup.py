import os
import subprocess

import tkinter as tk
from tkinter.font import Font
from tkinter import messagebox

from cert_manager import CertManager

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
        self.image = tk.PhotoImage(file="jedi-master-on-a-computer.png")
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
        users_to_delete = ['orson', 'grievous', 'darth', 'watto']
        old_users_deleted = True
        for user in users_to_delete:
            command = f"net user {user}"
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                old_users_deleted = False
                break
        if old_users_deleted:
            messagebox.showinfo("Congratulations!", f"You have completed your Youngling training! "
                                                    f"The passcode for your certificate is:")
        else:
            messagebox.showinfo("Keep Trying!", "You are missing some users that should be removed")



    def padawan_assessment(self):
        self.cert_manager.decrypt_padawan_cert()

    def jedi_assessment(self):
        self.cert_manager.decrypt_jedi_cert()

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


def main():
    # Your main code here
    RebelBaseForm().render()


if __name__ == "__main__":
    main()
