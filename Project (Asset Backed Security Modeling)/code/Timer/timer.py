'''9815 Homework Section 2.1.1: Timer class'''


import time # needed for time functions

class Timer(object):
    def __init__(self):
        self._currently_running = False
        self._start_time = None
        self._end_time = None
        self._result_time = None
        self._output_format= "S" # choice of S=seconds, M=minutes, H=hours
        self._divisor=1

    def start(self):
        if self._currently_running == True:
            raise Exception("Timer already running")
        self._start_time = time.time()
        self._currently_running=True

    def end(self):
        if self._currently_running == False:
            raise Exception("Timer not currently running")
        self._end_time = time.time()
        self._currently_running=False
        self._result_time = self._end_time - self._start_time
        # self.elapsed_time()
        return self._result_time

    def elapsed_time(self):

        if self._output_format == "M":
            self._divisor=60
        if self._output_format == "H":
            self._divisor=3600
        print "Elapsed Time (" + self._output_format + "): " + str(self._result_time / self._divisor)


    @property
    def format(self):
        return self._output_format

    @format.setter
    def format(self, user_entry):
        self._output_format = user_entry

    @property
    def elapsed(self):
        return self._result_time


