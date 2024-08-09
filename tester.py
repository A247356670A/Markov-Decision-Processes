import sys
import re

group_description = '''Group''':



def read_groups():
    global group_description
    students = {}

    current_group = None
    for line in group_description.splitlines():
        if line.startswith('Group'):
            current_group = line
            continue
        x = re.search('(.*),(u.*)', line)
        if x:
            name = x.group(1)
            id = x.group(2)
            students[id] = (name, current_group)
            continue
    return students


def get_evaluation(filename, students):
    with open(filename) as f:
        evaluation = {}
        for line in f.readlines():
            x = re.search('(u.*): (\d)', line)
            if not x:
                continue
            student = x.group(1)
            eval = x.group(2)
            evaluation[student] = eval

        # Now testing
        group = students[next(iter(evaluation.keys()))][1]
        student = [name for id, (name, gr) in students.items() if gr == group and id not in evaluation]
        if len(student) != 1:
            print(f"I don't know who you are (current list is {student})")
        else:
            print(f'You are {student[0]}.')
            for st, mark in evaluation.items():
                print(f'{st} -> {mark}')
        return student, evaluation


if __name__ == '__main__':
    students = read_groups()
    filename = "U7238355.txt"
    get_evaluation(filename, students)
