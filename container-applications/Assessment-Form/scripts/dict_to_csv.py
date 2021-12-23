import csv
from utilities.assessment_questions import *

# field names
fields = ['Number', 'Question', 'Domain', 'Capability', 'MaxPoints']

filename = "question_report.csv"

rows = []
for q in questions:
    domain_id = questions[q]['domain']
    capability_id = questions[q]['capability']
    domain = domains[domain_id]
    capability = domain['capabilities'][capability_id]
    new_row = [
        q,
        questions[q]['question'],
        domain['name'],
        capability,
        max(questions[q]['points'])
    ]
    rows.append(new_row)

# writing to csv file
with open(filename, 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(fields)
    csv_writer.writerows(rows)


