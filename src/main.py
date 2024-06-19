# load the data 
# create blocking keys 
# test the blocking key quality
# return the best results 

import pandas as pd 
import numpy as np
import random
from key import Key 
from pairs import Pair
import jellyfish
from matching import RecordMatcher
from comparison_function import *
import os
import sys



def calculate_pnew(P, x, y):
    # Convert P to a numpy array for easier manipulation
    P = np.array(P)
    
    # Calculate Pmean (mean of all sublists)
    Pmean = np.mean(P, axis=0)
    
    # Initialize Pnew
    Pnew = []
    
    # Iterate through the sublists of P
    for i in range(len(P)):
        Pi = P[i]
        Pi_next = P[(i+1) % len(P)]  # Using modulo for circular indexing
        yi = y[i]
        xi = x[i]
        
        # Calculate Pnew using the given formula
        Pnew_i = Pi + yi * (Pi - Pi_next) + xi * (Pi - Pmean)
        
        # Append the result to Pnew
        Pnew.append(Pnew_i.tolist())
    
    return Pnew


def evaluate_blocking_key(key , export):

    matcher = RecordMatcher()
    matcher_exact = RecordMatcher()
    matcher_numeric = RecordMatcher()
    
    matcher.add_attribute_weight("Name", 1)
    matcher.add_comparison_function("Name", levenshtein)
    matcher.add_attribute_weight("Surname", 1)
    matcher.add_comparison_function("Surname", levenshtein)

    matcher_exact.add_attribute_weight("Balance", 1)
    matcher_exact.add_comparison_function("Balance", exact_match)

    matcher_numeric.add_attribute_weight("Age", 1)
    matcher_numeric.add_comparison_function("Age", numetic_distance)

    pairs = []

    for value in key.values:
        directory = f'C:\\dev\\fnl\\keys\\{key.block}'
        file_name = f'{value}.csv'
        file_path = os.path.join(directory, file_name)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        records = data.loc[data[key.block] == value]
        if export == True:
            if len(records) > 1:
                records.to_csv(file_path , index=False)
        if not (len(records) <= 1) and not (len(records) >= 50):
            for i, row1 in records.iterrows():
                if i == len(records) - 1:
                    break
                for j, row2 in records.loc[i+1:].iterrows():
                    if matcher.compare_records(row1 , row2) >= 70 and matcher_exact.compare_records(row1 , row2) and matcher_numeric.compare_records(row1 , row2) < 2:
                        pair = Pair(i , j , "TP") if data.at[i , "UID"] == data.at[j , "UID"] else Pair(i , j , "FP")
                        pairs.append(pair)
                    else: 
                        pair = Pair(i , j , "FN") if data.at[i , "UID"] == data.at[j , "UID"] else Pair(i , j , "TN")
                        pairs.append(pair)
    tp = 0 
    fp = 0
    tn = 0 

    for pair in pairs:
        if pair.state == "TP":
            tp = tp +1
        if pair.state == "FP":
            fp = fp +1
        if pair.state == "TN":
            tn = tn +1

    fn = total_pairs - tp
    
    recall = tp / (tp + fn) if tp+fn > 0 else 0
    precision = tp / (tp + fp) if tp+fp > 0 else 0
    f1score = 2*((precision*recall) / (precision+recall)) if precision+recall > 0 else 0
    key.score = f1score

    return f1score


def correct_positions(positions, min_values, max_values):
    seen_values = set()
    
    for i in range(len(positions)):
        for j in range(len(positions[i])):
            if positions[i][j] < min_values[j]:
                positions[i][j] = min_values[j]
            elif positions[i][j] > max_values[j]:
                positions[i][j] = max_values[j]
        
        # Ensure the value of positions[i][0] is unique
        original_value = positions[i][0]
        if original_value in seen_values:
            new_value = original_value
            while new_value in seen_values:
                new_value += 1
                if new_value > max_values[0]:
                    new_value = min_values[0]
            positions[i][0] = new_value
        
        seen_values.add(positions[i][0])
    
    return positions


pd.set_option("display.max_row" , None)
pd.set_option("display.max_colwidth" , None)
if len(sys.argv) > 1:
    data = pd.read_csv(sys.argv[1])
else:
    print("No dataset selected")

total_pairs = 0
count = data["UID"].value_counts()
for uid , c in count.items() :
    total_pairs = total_pairs + (c*(c-1))//2

#################################################

data_cols = data.columns.drop(["UID"]).tolist()
data_func = [jellyfish.soundex , jellyfish.metaphone , jellyfish.nysiis , str]
counts = list(range(2,10))

keys = []

for itr in range(5):
    selected_cols = random.sample(data_cols , random.randint(1 , len(data_cols)))
    selected_func = random.choices(data_func , k=len(selected_cols))
    selected_count = random.choices(counts , k=len(selected_cols))

    key = Key(f"Key{itr}" , selected_cols , selected_func , selected_count)
    key.export_to_custom_format("C:\\dev\\fnl\\keys" , f"key{itr}.txt")
    
    if key not in keys:
        keys.append(key)

    for index , row in data.iterrows():
        data.at[index , f"Key{itr}"] = key.Keyv(row=row)

print(data)

fitness_values = {}

population = keys
best_key = None
best_fitness = 0

pos = [key.to_position() for key in population]
pos = [np.array(p) for p in pos]
particle_means = [np.mean(p, axis=0) for p in pos]
Pmean = np.mean(particle_means, axis=0)
Pmean = np.round(Pmean).astype(int)

for key in population:
    score = evaluate_blocking_key(key , True)
    if score > best_fitness and score < 1:
        best_key = key
        best_fitness = score
    print(f"{key.block} ---------  {score}")
print("\n\n\n")

for iteration in range(10):

    print(f"starting test {iteration} \n")

    repl = None
    a = random.randint(1 , 2)
    r = random.randint(1 , 2)
    print("selecting")
    for key in population:
        Pnew = [Pb + a * r * (Pmean - Pi) for Pb, Pi in zip(best_key.to_position(), key.to_position())]
        Pnew = np.round(Pnew).astype(int).tolist()
        Pnew = correct_positions(Pnew , [0 , 0 , 2] , [7 , 3 , 10])
        k = Key.from_position(Pnew , key.block)
        if k not in population:
            for index , row in data.iterrows():
                data.at[index , f"{k.block}"] = k.Keyv(row=row)
            s = evaluate_blocking_key(k , False)
            if s > key.score:
                population[population.index(key)] = k
                repl = k
            if s > best_key.score:
                best_key = k
                best_fitness = s

    print("searching")
    for i, key in enumerate(population):
        x = random.randint(1 , 3)
        y = random.randint(1 , 3)
        if i + 1 < len(population):
            Pnext = population[i+1].to_position()
            p_mean = [np.mean(p, axis=0) for p in Pnext]
            Pnext = np.mean(p_mean, axis=0)
            Pnext = np.round(Pmean).astype(int)
        if len(Pnext) > 0:
            Pnew = [Pi + y * (Pi - Pnext) + x * (Pi - Pmean) for Pi in key.to_position()]
        else:
            Pnew = [Pi + x * (Pi - Pmean) for Pi in key.to_position()]
            
        Pnew = np.round(Pnew).astype(int).tolist()
        Pnew = correct_positions(Pnew , [0 , 0 , 2] , [7 , 3 , 10])
        k = Key.from_position(Pnew , key.block)
        if k not in population:
            for index , row in data.iterrows():
                data.at[index , f"{k.block}"] = k.Keyv(row=row)
            s = evaluate_blocking_key(k , False)
            if s > key.score:
                if repl != None:
                    population[population.index(repl)] = k
                    repl = k
                else:
                    population[population.index(key)] = k
            if s > best_key.score:
                best_key = k
                best_fitness = s


    print("swooping")
    for i, key in enumerate(population):
        x = random.random()
        y = random.random()
        c1 = random.randint(1,2)
        c2 = random.randint(1,2)

        pb_mean = [np.mean(p, axis=0) for p in best_key.to_position()]
        Pbest = np.mean(pb_mean, axis=0)
        Pbest = np.round(Pbest).astype(int)
        
        Pnew = [random.random() * Pbest + y * (Pi - c1 * Pmean) + x * (Pi - c2 * Pmean) for Pi in key.to_position()]
        Pnew = np.round(Pnew).astype(int).tolist()
        Pnew = correct_positions(Pnew , [0 , 0 , 2] , [7 , 3 , 10])
        k = Key.from_position(Pnew , key.block)
        if k not in population:
            for index , row in data.iterrows():
                data.at[index , f"{k.block}"] = k.Keyv(row=row)
            s = evaluate_blocking_key(k , False)
            if s > key.score:
                if repl != None:
                    population[population.index(repl)] = k
                    repl = k
                else:
                    population[population.index(key)] = k
            if s > best_key.score:
                best_key = k
                best_fitness = s

    print(f"test {iteration} done \n")

    for p in population:
        if p.score < 1:
            p.export_to_custom_format(f"C:\\dev\\fnl\\BES_keys\\test{iteration}" , f"{p.block}_{float(p.score*100)}.txt")
        
