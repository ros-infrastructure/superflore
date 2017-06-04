#include <sys/wait.h>

#include <unistd.h>
#include <stdio.h>

int main()
{
        /* we're gonna call run... yup. */
        pid_t lunar_pid, kinetic_pid, indigo_pid;
        int lunar_status, kinetic_status, indigo_status;

        if ((lunar_pid = fork()) < 0) {
                perror("lunar: fork");
                return 1;
        } else if (lunar_pid == 0) {
                execlp("./run.py", "./run.py", "--lunar", NULL);
                perror("lunar: execlp");
                return 2;
        } else if ((kinetic_pid = fork()) < 0) {
                perror("kinetic: fork");
                return 3;
        } else if (kinetic_pid == 0) {
                execlp("./run.py", "./run.py", "--kinetic", NULL);
                perror("kinetic: execlp");
                return 4;
        } else if ((indigo_pid = fork()) < 0) {
                perror("indigo: fork");
                return 5;
        } else if ((indigo_pid == 0)) {
                execlp("./run.py", "./run.py", "--indigo", NULL);
                perror("indigo: execlp");
                return 6;
        }

        waitpid(lunar_pid, &lunar_status, 0);
        waitpid(kinetic_pid, &kinetic_status, 0);
        waitpid(indigo_pid, &indigo_status, 0);

        return indigo_status + kinetic_status + lunar_status;
}
