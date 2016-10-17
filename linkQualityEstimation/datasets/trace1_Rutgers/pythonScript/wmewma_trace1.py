from threading import Timer
from time import sleep
import time
import os

class Estimator:
    ALPHA = 0.6 # controls the history of the estimator - [0, 1]
    MIN_DATA_FREQUENCY = 10000 # minimum message rate, one packet per x miliseconds, e.g. 10000 (1 packet / 10 seconds)
    ESTIMATE_TO_DATA_RATIO = 20 # defines time window, e.g. 20 means estimation is performed every 20 times MIN_DATA_FREQUENCY

    def __init__(self, alpha = ALPHA, min_data_frequency = MIN_DATA_FREQUENCY, estimate_to_data_ratio = ESTIMATE_TO_DATA_RATIO):
        self.alpha = alpha
        self.estimate_to_data_ratio = estimate_to_data_ratio
        self.interval = (float(min_data_frequency) * estimate_to_data_ratio) / 1000
        self.__timer = None
        self.__timer_running = False
        self.is_running = False

        self.reset()

    def reset(self):
        if not self.is_running:
            self.missed = 0
            self.received = 0
            self.last_seq_num = 0
            self.estimation = 0
            self.new = True
            self.est_init = True

    def receive_message(self, seq_num):
        if self.is_running:
            # update counters
            if self.new:
                self.received += 1
                self.last_seq_num = seq_num
                self.new = False
                return

            diff = seq_num - self.last_seq_num - 1
            if diff >= 0:
                self.received += 1
                self.missed += diff
                self.last_seq_num = seq_num
            else:
                # duplicate message
                pass

    def __update_estimation(self):
        self.__timer_running = False
        self.__start_timer()
        
        # calculate the estimation
        if self.new:
            return

        expected_packets = self.estimate_to_data_ratio
        actual_sent_packets = self.received + self.missed
        total_packets = max(expected_packets, actual_sent_packets)

        mean = float(self.received) / total_packets # packet reception ratio
        self.received = 0
        self.missed = 0

        if self.est_init:
            self.est_init = False
            self.estimation = mean
        else:
            self.estimation = (self.alpha * self.estimation) + ((1 - self.alpha) * mean)
        #print("UPDATING ESTIMATION: MEAN: " + str(mean) + ", EST: " + str(self.estimation))

    def __start_timer(self):
        if not self.__timer_running:
            self.__timer = Timer(self.interval, self.__update_estimation)
            self.__timer.start()
            self.__timer_running = True

    def begin(self):
        self.is_running = True
        self.__start_timer()
        

    def end(self):
        self.__timer.cancel()
        self.__timer_running = False
        self.is_running = False


if __name__ == "__main__":
    est1 = Estimator(min_data_frequency = 150, estimate_to_data_ratio = 20)
    PATH = "/home/ijs/Desktop/eWINE_Paris_SC2_RSSI/Trace_1/data/"
    PATH_TO_OUTPUT = "/home/ijs/Desktop/eWINE_Paris_SC2_RSSI/Trace_1/output/"
    for root, dirs, files in os.walk(PATH):
        for file in files:
            if file.endswith(""):
                print(str(file))
                root_output = root.lstrip()
                tmp = root_output[len(PATH):]
                dir = tmp.split("/")
                name = dir[1].split("_")
                if not os.path.exists(PATH_TO_OUTPUT + dir[0] + "/" + name[1]):
                    os.makedirs(PATH_TO_OUTPUT + dir[0] + "/" + name[1])
                if os.path.isfile(PATH_TO_OUTPUT + dir[0] + "/" + name[1] + '/' + str(file) + '_wmewma.txt'):
                    print("skipping\n")
                    continue
                output_file = open(PATH_TO_OUTPUT + dir[0] + "/" + name[1] + '/' + str(file) + '_wmewma.txt', 'w')
                input_file = open(os.path.join(root, file), 'r')

                est1.begin()

                real_seqno = 0
                line = input_file.readline()
                if line.strip():
                    seqno, _ = line.split(" ")
                else:
                    seqno = -1
                while real_seqno <= 300:
                    if int(seqno) == real_seqno:
                        est1.receive_message(int(seqno))
                        line = input_file.readline()
                        if line.strip():
                            seqno, _ = line.split(" ")
                    #print(real_seqno, seqno, est1.estimation)
                    output_file.write(str(real_seqno) + " " + str(est1.estimation) + "\n")
                    sleep(0.1)
                    #target_time = time.clock() + 0.1
                    #while time.clock() < target_time:
                    #    pass
                    real_seqno += 1

                est1.end()
                est1.reset()
                input_file.close()
                output_file.close()