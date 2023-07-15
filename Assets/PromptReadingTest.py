import pandas as pd
import random
from random_word import Wordnik

FILE_PATH = 'Assets\PromptsGenerationPool.csv'
MIN_CORPUS_COUNT = 10000

# replace 'file.csv' with your file path
df = pd.read_csv(FILE_PATH)

def process_dataframe(df):
    data = {}
    # Initialize current subgroup for each column
    current_subgroup = {column: None for column in df.columns}
    
    # Loop over each row in the DataFrame
    for _, row in df.iterrows():
        # Loop over each column in the row
        for column in df.columns:
            # If the row value is a subgroup, update the current subgroup
            if pd.notna(row[column]) and row[column].startswith('('):
                current_subgroup[column] = row[column]
                # Initialize a new list for this subgroup
                header, header_score = column.rsplit(" ", 1)
                header_score = int(header_score.strip("()"))
                subgroup_score, subgroup = row[column].split(" ", 1)
                subgroup = subgroup.strip()
                subgroup_score = int(subgroup_score.strip("()"))
                if (header, header_score) not in data:
                    data[(header, header_score)] = {}
                data[(header, header_score)][(subgroup, subgroup_score)] = []
            # Otherwise, if there's a current subgroup, add the value to the list
            elif pd.notna(row[column]) and current_subgroup[column] is not None:
                header, header_score = column.rsplit(" ", 1)
                header_score = int(header_score.strip("()"))
                subgroup_score, subgroup = current_subgroup[column].split(" ", 1)
                subgroup = subgroup.strip()
                subgroup_score = int(subgroup_score.strip("()"))
                data[(header, header_score)][(subgroup, subgroup_score)].append(row[column])
    return data

def get_random_dict(data):
    total_score = sum(header[1] for header in data.keys())
    random_value = random.uniform(0, total_score)
    current_sum = 0
    for header, items in data.items():
        current_sum += header[1]
        if random_value <= current_sum:
            return {header: items}
    return None

def get_random_subgroup(data):
    # Get a random dictionary
    random_dict = get_random_dict(data)
    # Extract the only key-value pair from the dictionary
    (header, _), items = list(random_dict.items())[0]
    total_score = sum(subgroup[1] for subgroup in items.keys())
    random_value = random.uniform(0, total_score)
    current_sum = 0
    for subgroup, elements in items.items():
        current_sum += subgroup[1]
        if random_value <= current_sum:
            return {subgroup: elements}
    return None

def get_random_element(data):
    # Get a random subgroup
    random_subgroup = get_random_subgroup(data)
    # Extract the only key-value pair from the dictionary
    (subgroup, _), elements = list(random_subgroup.items())[0]
    # Pick a random element from the list
    random_element = random.choice(elements)
    return random_element

wordnik_service = Wordnik(api_key="zqai8u9e5pi2p1ia43ee0359w7loishvhyoll5k06hk5j3ges")

# Return Word of the day
print(wordnik_service.get_random_words(hasDictionaryDef="true", includePartOfSpeech="noun", minCorpusCount=MIN_CORPUS_COUNT, minDictionaryCount=20))


# data = process_dataframe(df)

# for _ in range(5):
#     random_element = get_random_element(data)
#     print(random_element)
