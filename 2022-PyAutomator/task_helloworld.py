import pyRTOS
import time
import os

def setup():
    pass


def thread_loop():
	print("Hello world")


# self is the thread object this runs in
# If this function return, the task will terminate.
def task(self):

	### Setup code here

	setup()

	### End Setup code

	# Pass control back to RTOS
	yield

	# Thread loop
	while True:


		# Remember to yield once in a while (to give control back to the OS)

		### Start Work code
		thread_loop()
		### End Work code

		# Adjust the timing here (in seconds) to fix the interval between each
    	# re-wake of the thread (the os will automatically wake it every tot time)
		# THIS IS A BLOCKING DELAY! TASK EXECUTION IS BLOCKED FOR THIS TIME
		yield [pyRTOS.timeout(5)]

		# Leave this condition, to kill the task if a certain file is written in the folder
		if os.path.exists('all.terminate'):
			return


def main():
	# Now we create the task
	# OSS: This is the entry point of the file. Execution starts here.
	# The name of the task you need to pass as first parameter is the name
	# of the function that implements the task. In this case, it's 
	# the "task()" function implemented above.
	# Mailboxes (for messages) are disabled
	pyRTOS.add_task(pyRTOS.Task(task, name="task1"))

	# Let's add a service routine that implements a 1ms delay every time the scheduler
	# is called, in order to slow down the execution, and having a minor impact on CPU
	pyRTOS.add_service_routine(lambda: time.sleep(0.1))


	pyRTOS.start()


if __name__ == '__main__':
	main()