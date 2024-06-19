class RecordMatcher:
    def __init__(self):
        self.weights = {}
        self.comparisons = {}

    def add_attribute_weight(self, attribute_name, weight):
        self.weights[attribute_name] = weight

    def compare_records(self, record1, record2):
        composite_weight = 0
        for attribute_name, weight in self.weights.items():
            if attribute_name not in record1 or attribute_name not in record2:
                continue  # Skip attributes that are not present in both records
            if attribute_name not in self.comparisons:
                raise ValueError(f"Comparison function for attribute '{attribute_name}' not implemented.")
            comparison_function = self.comparisons[attribute_name]
            composite_weight += comparison_function(record1[attribute_name], record2[attribute_name]) * weight

        return composite_weight / len(self.weights)

    def add_comparison_function(self, attribute_name, comparison_function):
        self.comparisons[attribute_name] = comparison_function






