class BPlusTree():
    def __init__(self, order):
        self.key_list = []
        self.data_list = []

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


DATA_TYPES_NUMBER = 900
TREES_ORDER = 20


class DataManagerInterface():
    types_array_of_trees = range(0, 900)

    def __init__(self, order = TREES_ORDER):
        #for data_type in range(0, DATA_TYPES_NUMBER):
        self.types_array_of_trees[27] = BPlusTree(order)

    def print_tree_or_not_tree(self):
        for data_type in range(0, DATA_TYPES_NUMBER):
            for index in range(0, len(self.types_array_of_trees[data_type].data_list)):
                print self.types_array_of_trees[data_type].key_list[index]
                #print self.types_array_of_trees[data_type].data_list[index]


    def insertMeasurement(self, data_type, data, timestamp):
        self.types_array_of_trees[data_type].key_list.append(timestamp)
        self.types_array_of_trees[data_type].data_list.append(data)

    def estimate(self, data_type, timestamp):
        smaller = self.types_array_of_trees[data_type].search_smaller(timestamp)
        bigger = self.types_array_of_trees[data_type].search_bigger(timestamp)
        if smaller is None or bigger is None:
            return None
        (lower_timestamp, lower_value) = smaller
        (higher_timestamp, higher_value) = bigger
        estimation = []
        if higher_timestamp == lower_timestamp:
            return lower_value
        else:
            for index in xrange(0, len(lower_value)):
                estimation.append(float((higher_value[index] - lower_value[index]) * (timestamp - lower_timestamp)) / (higher_timestamp - lower_timestamp) + lower_value[index])
            return estimation