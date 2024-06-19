import pandas as pd 
import uuid

pd.set_option("display.max_row" , None)
data = pd.read_csv("C:\\dev\\final\\res\\data\\ub.csv")

total_pairs = 0
count = data["UID"].value_counts()
for uid , c in count.items() :
    total_pairs = total_pairs + (c*(c-1))//2

print(total_pairs)