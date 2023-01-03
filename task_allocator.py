import json
import os
from threading import Thread, Lock
import subprocess

from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist

dir_log = os.path.join(os.getcwd(), ".task_allocator_log")
makedir_if_not_exist(dir_log)


class TaskAllocator:
    def __init__(self):
        self.running_commands, self.running_commands_lock = set(), Lock()
        self.successful_commands, self.successful_commands_lock = list(), Lock()
        self.failed_commands, self.failed_commands_lock = list(), Lock()
        self.path_log, self.log_lock = os.path.join(dir_log, get_random_time_stamp()), Lock()
        self.num_max_restart = 10

    def add_running_command(self, command):
        self.running_commands_lock.acquire()
        self.running_commands.add(command)
        self.running_commands_lock.release()

    def remove_running_command(self, command):
        self.running_commands_lock.acquire()
        self.running_commands.remove(command)
        self.running_commands_lock.release()

    def add_successful_command(self, command, stdout=None, stderr=None, **kwargs):
        self.successful_commands_lock.acquire()
        self.successful_commands.append(command)
        self.successful_commands_lock.release()
        self.add_log(status="success", command=command, stdout=stdout, stderr=stderr, **kwargs)

    def add_failed_command(self, command, stdout=None, stderr=None, **kwargs):
        self.failed_commands_lock.acquire()
        self.failed_commands.append(command)
        self.failed_commands_lock.release()
        self.add_log(status="failed", command=command, stdout=stdout, stderr=stderr, **kwargs)

    def add_log(self, **kwargs):
        log = json.dumps(kwargs)
        self.log_lock.acquire()
        with open(self.path_log, "a") as fout:
            fout.write(log + "\n")
        self.log_lock.release()

    def run_task(self, command, restart_if_fail=False):
        self.add_running_command(command)
        proc = subprocess.run(command, shell=True, capture_output=True)

        num_restart, log_restart = 0, {}
        while restart_if_fail and proc.returncode != 0 and num_restart < self.num_max_restart:
            log_restart["stdout_run_%d" % num_restart] = proc.stdout
            log_restart["stderr_run_%d" % num_restart] = proc.stderr
            proc = subprocess.run(command, shell=True, capture_output=True)
            num_restart += 1

        self.remove_running_command(command)
        if proc.returncode == 0:
            self.add_successful_command(command, stdout=proc.stdout, stderr=proc.stderr, **log_restart)
        else:
            self.add_failed_command(command, stdout=proc.stdout, stderr=proc.stderr, **log_restart)

    def show_menu(self):
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
                Thread(target=self.run_task, args=(cmd, restart_if_fail)).start()
            elif option == 3 or option == 4:
                path_cmd_file = input(
                    "Please input the path to the file where commands are listed (one command each line):\n")
                if os.path.exists(path_cmd_file):
                    restart_if_fail = (option == 4)
                    with open(path_cmd_file) as fin:
                        for line in fin.readlines():
                            cmd = line.strip()
                            Thread(target=self.run_task, args=(cmd, restart_if_fail)).start()
                else:
                    print("File does not exist!")
            elif option == 5:
                for i in self.running_commands:
                    print(i)
            elif option == 6:
                for i in self.successful_commands:
                    print(i)
            elif option == 7:
                for i in self.failed_commands:
                    print(i)
            elif option == 8:
                os.system("nvidia-smi")
            else:
                print("Wrong Input!")
                continue

            print()


if __name__ == '__main__':
    task_allocator = TaskAllocator()
    while True:
        try:
            task_allocator.show_menu()
        except KeyboardInterrupt:
            print("Ctrl-C is forbidden. Use Ctrl-Z to exit!")
            continue
        except EOFError:
            print("Ctrl-D is forbidden. Use Ctrl-Z to exit!")
            continue
