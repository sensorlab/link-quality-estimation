class Estimator:
    ALPHA = 0.6 # controls the history of the estimator - [0, 1]
    PACKETS_PER_WINDOW = 3 # basically a number of lines to read from a file

    def __init__(self, alpha = ALPHA, packets_per_window = PACKETS_PER_WINDOW):
        self.alpha = alpha
        self.packets_per_window = packets_per_window

        self.reset()

    def reset(self):
        self.missed = 0
        self.received = 0
        self.last_seq_num = 0
        self.estimation = 0
        self.new = True
        self.est_init = True
        self.current_packet = 0

    def receive_message(self, seq_num):
        # update counters
        self.current_packet += 1

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

        if self.current_packet >= self.packets_per_window:
            self.__update_estimation()
            self.current_packet = 0

    def __update_estimation(self):
        # calculate the estimation
        if self.new:
            return

        expected_packets = self.packets_per_window
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



if __name__ == "__main__":
    est1 = Estimator(packets_per_window = 2, alpha = 0.6)

    file = open('../datasets/trace1_Rutgers/data/dbm0/Results_node1-2_DailyTest_Sat-Oct-15-04_46_38-2005/sdec1-4', 'r')
    for line in file:
        seqno, _ = line.split(" ")
        est1.receive_message(int(seqno))
