import math
import jellyfish
from fuzzywuzzy import fuzz

# Comparison functions
def exact_match(value1, value2):
    return True if value1 == value2 else False

def numetic_distance(value1, value2):
    return math.sqrt((value1 - value2) ** 2)

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def cosine_similarity(vector1, vector2):
    dot_product = sum(v1 * v2 for v1, v2 in zip(vector1, vector2))
    magnitude1 = math.sqrt(sum(v1 ** 2 for v1 in vector1))
    magnitude2 = math.sqrt(sum(v2 ** 2 for v2 in vector2))
    return dot_product / (magnitude1 * magnitude2) if (magnitude1 * magnitude2) != 0 else 0

def jarowinkler(value1 , value2):
    return jellyfish.jaro_similarity(value1 , value2)*100

def levenshtein(value1 , value2):
    return fuzz.ratio(value1 , value2)