import os
from threading import Thread, Lock
import subprocess

running_commands, running_commands_lock = set(), Lock()
successful_commands, successful_commands_lock = list(), Lock()
failed_commands, failed_commands_lock = list(), Lock()


def run_task(command, restart_if_fail=False):
    running_commands_lock.acquire()
    running_commands.add(command)
    running_commands_lock.release()

    proc = subprocess.run(command, shell=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stderr)
    num_max_restart, num_restart = 5, 0
    while restart_if_fail and proc.returncode != 0 and num_restart < num_max_restart:
        proc = subprocess.run(command, shell=True, capture_output=True)
        num_restart += 1

    running_commands_lock.acquire()
    running_commands.remove(command)
    running_commands_lock.release()

    if proc.returncode == 0:
        successful_commands_lock.acquire()
        successful_commands.append(command)
        successful_commands_lock.release()
    else:
        failed_commands_lock.acquire()
        failed_commands.append(command)
        failed_commands_lock.release()


def main():
    while True:
        option = input(
            "=======================================================================\n"
            "Please input corresponding number to select menu item:\n"
            "1. submit a task from input.\n"
            "2. submit a task from input (restart if fail).\n"
            "3. submit a task from file.\n"
            "4. submit a task from file (restart if fail).\n"
            "5. show running commands.\n"
            "6. show successfully finished commands.\n"
            "7. show failed commands.\n"
            "8. show GPU usage.\n"
            "=======================================================================\n"
        )
        try:
            option = int(option)
        except ValueError:
            print("Wrong Input!")
            continue
        print()

        if option == 1 or option == 2:
            cmd = input("Please input the command to run:\n")
            restart_if_fail = (option == 2)
            Thread(target=run_task, args=(cmd, restart_if_fail)).start()
        elif option == 3 or option == 4:
            path_cmd_file = input(
                "Please input the path to the file where commands are listed (one command each line):\n")
            if os.path.exists(path_cmd_file):
                restart_if_fail = (option == 4)
                with open(path_cmd_file) as fin:
                    for line in fin.readlines():
                        cmd = line.strip()
                        Thread(target=run_task, args=(cmd, restart_if_fail)).start()
            else:
                print("File does not exist!")
        elif option == 5:
            for i in running_commands:
                print(i)
        elif option == 6:
            for i in successful_commands:
                print(i)
        elif option == 7:
            for i in failed_commands:
                print(i)
        elif option == 8:
            os.system("nvidia-smi")
        else:
            print("Wrong Input!")
            continue

        print()


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Ctrl-C is forbidden. Use Ctrl-Z to exit!")
            continue
        except EOFError:
            print("Ctrl-D is forbidden. Use Ctrl-Z to exit!")
            continue
