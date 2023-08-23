# Phishing Practice: Step-by-Step Instructions

## Introduction
You've heard about Social Engineering and spam emails, but have you ever wondered what happens if you click on those links? Let's explore that in this practice session. We'll be looking at a specific type of attack called phishing and how to protect yourself. Don't worry if you're not tech-savvy – we'll be using a tool called BeEF (Browser Exploitation Framework) to show you how it works.

## Understanding BeEF
BeEF is easy to use and gives you insights into hooked browsers. A hooked browser is one that has visited a page infected by BeEF. To interact with a hooked browser, click on it. The page will show details, logs, and commands for that browser. We'll focus on the first three sections.

In the "Commands" section, you'll see modules on the left. These are BeEF's built-in tools. The right side shows module details and options to execute. The middle column displays results of completed commands.

## Getting Started
1. Log into the Guacamole web server using the username and password given on the landing page. Refresh if needed – you'll log in automatically.
2. Your goal is to access the BeEF UI panel at `localhost:3002/ui/panel/`. Use "workout" as the username and "gonephishing" as the password. Keep this info.
3. Open a new tab and go to `http://10.1.1.20:3001/login`. Log in with "root" and "password" as the username and password. Ignore pop-ups for now.
4. Read a short article about social engineering, spam, and phishing attacks to refresh your memory.
5. **Task 1:** Accept the cookie request.
6. **Task 2:** Return to the BeEF tab and check the logs in the panel. Do you notice anything important?
7. **Task 3:** Experiment with some modules (listed below) and observe their effects on the PhishPhactor tab.
8. **Task 4:** Can you find a hidden flag on the PhishPhactor page?

## Modules to Try
Go to the "Commands" tab in the BeEF panel.
Anything between [ ] is a module, followed by a specific command.
- `[Browser]=>Get-HTML`
- `[Browser]=>Create Alert Dialog Box or Create Prompt Dialog (or both!)`
- `[Social Engineering]=>Fake_Flash`
(Hint: You might need to install Flash...)

Remember, all activities will be within the provided Cyber Gym machine. Have fun exploring the world of phishing and enhancing your digital awareness!
