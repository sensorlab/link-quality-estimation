from threading import Timer
from time import sleep

''' TODO
ACCEPTABLE_MISSED           = -20,
 else if (sDelta < ACCEPTABLE_MISSED) {
      // Something happend to this node.  Reinitialize it's state
      newEntry(iNbr,saddr);
      pNbr->received++;
      pNbr->lastSeqno = seqno;
      pNbr->flags ^= NBRFLAG_NEW;
    }
'''

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
        print("UPDATING ESTIMATION: MEAN: " + str(mean) + ", EST: " + str(self.estimation))

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
    est1 = Estimator(min_data_frequency = 3000, estimate_to_data_ratio = 3)
    est1.begin()

    while(True):
        seqno = raw_input()
        if seqno == "quit":
        	break
        est1.receive_message(int(seqno))

    est1.end()