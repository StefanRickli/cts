from time import time
import logging

class TPMTapper():
    def __init__(self):
        self.beats_per_bar = 4
        self.n_taps = 0
        self.start_tap = -1
        self.last_tap = -1

    def tap(self):
        if self._first_run() or self._long_ago():
            self.reset()
            self.start_tap = time()
            self.last_tap = self.start_tap
            return (self.get_n_taps(), self.get_tpm())
        
        self.n_taps += 1
        self.last_tap = time()

        return (self.get_n_taps(), self.get_tpm())
    
    def get_n_taps(self):
        if self._stopped():
            return ''
        return str(self.n_taps)

    def get_tpm(self):
        if self.start_tap == -1:
            return 'stopped'
        if self.n_taps == 0:
            return 'FIRST TAP'
        
        assert(self.beats_per_bar > 0)
        return '{:.1f}'.format(60 * self.n_taps / ((self.last_tap - self.start_tap) * self.beats_per_bar) )

    def valid_tpm(self):
        tpm = self.get_tpm()
        return tpm not in ('stopped', 'FIRST TAP')

    def get_beats_per_bar(self):
        return str(self.beats_per_bar)

    def set_beats_per_bar(self, n):
        if n < 1:
            logging.warning('TPMTapper.set_beats_per_bar(n): negative n')
            return
        
        self.beats_per_bar = n
        self.reset()
        return (self.get_n_taps(), self.get_tpm())

    def _first_run(self):
        return self.last_tap == -1
    
    def _long_ago(self):
        return time() - self.last_tap > 2

    def _stopped(self):
        return self.start_tap == -1

    def reset(self):
        self.n_taps = 0
        self.start_tap = -1
        self.last_tap = -1
