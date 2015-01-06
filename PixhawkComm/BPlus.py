class BPlusTree():
    key_list = []
    data_list = []

    def __init__(self, order):
        for data_type in range(0, DATA_TYPES_NUMBER):
            pass

    def insertMeasurement(self, data_type, data, timestamp):
        self.key_list.insert(data)
        self.data_list.insert(data)

    def search_smaller(self, timestamp):
        min_delta = timestamp * 10
        found_index = -1

        for index in range(0, self.key_list.__len__()):
            delta = timestamp - self.key_list[index]
            if 0 <= delta < min_delta:
                min_delta = delta
                found_index = index

        if min_delta < 0:
            return None

        return self.key_list[found_index], self.data_list[found_index]

    def search_bigger(self, timestamp):
        min_delta = timestamp * 10
        found_index = -1

        for index in range(0, self.key_list.__len__()):
            delta = self.key_list[index] - timestamp
            if 0 <= delta < min_delta:
                min_delta = delta
                found_index = index

        if min_delta < 0:
            return None

        return self.key_list[found_index], self.data_list[found_index]


DATA_TYPES_NUMBER = 100
TREES_ORDER = 20


class DataManagerInterface():
    types_array_of_trees = range(0, 100)

    def __init__(self, order = TREES_ORDER):
        for data_type in range(0, DATA_TYPES_NUMBER):
            print "DIE!!"
            self.types_array_of_trees[data_type] = BPlusTree(order)

    def insertMeasurement(self, data_type, data, timestamp):
        self.types_array_of_trees[data_type].key_list.append(timestamp)
        self.types_array_of_trees[data_type].data_list.append(data)

    def estimate(self, data_type, timestamp):
        smaller = self.types_array_of_trees[data_type].search_smaller(timestamp)
        bigger = self.types_array_of_trees[data_type].search_bigger(timestamp)
        if smaller is None or bigger is None:
            return None
        (lower_value, lower_timestamp) = smaller
        (higher_value, higher_timestamp) = bigger

        if higher_timestamp == lower_timestamp:
            return lower_value
        else:
            estimation = ((higher_value - lower_value) * (timestamp - lower_timestamp)) / (higher_timestamp - lower_timestamp) + lower_value
            return estimation