import numpy as np

"""
http://code.activestate.com/recipes/68429-ring-buffer/
http://stackoverflow.com/questions/4151320/efficient-circular-buffer
"""

class RingBuffer(object):
    def __init__(self, size_max, default_value=0.0, dtype=float):
        """
        Initialization of RingBuffer with a fixed size.
        """
        self.size_max = size_max
        self._data = np.empty(size_max, dtype=dtype)
        self._data.fill(default_value)
        self.size = 0

    def append(self, value):
        """
        Append an element to the ring buffer.
        """
        self._data = np.roll(self._data, 1)
        self._data[0] = value
        self.size += 1

        if self.size == self.size_max:
            self.__class__ = RingBufferFull

    def get_all(self):
        """
        Return all elements in the buffer (oldest to newest).
        """
        return self._data

    def get_partial(self):
        """
        Return only the filled part of the buffer.
        """
        return self.get_all()[0:self.size]

    def moving_average(self, window_size):
        """
        Calculate the moving average over a given window size.
        """
        if self.size < window_size:
            window = self.get_partial()[:self.size]
        else:
            window = self.get_partial()[:window_size]
        return np.mean(window)

    def __getitem__(self, key):
        """
        Get an element by index.
        """
        return self._data[key]

    def __repr__(self):
        """
        Return string representation.
        """
        s = self._data.__repr__()
        s = s + '\t' + str(self.size)
        s = s + '\t' + self.get_all()[::-1].__repr__()
        s = s + '\t' + self.get_partial()[::-1].__repr__()
        return s


class RingBufferFull(RingBuffer):
    def append(self, value):
        """
        Append an element when the buffer is full.
        """
        self._data = np.roll(self._data, 1)
        self._data[0] = value
