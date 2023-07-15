import pandas as pd
import random
from random_word import Wordnik

PROMPT_POOL = 'Assets\PromptsGenerationPool.csv'
PREPOSITIONS = 'Assets\Prepositions.csv'
MIN_CORPUS_COUNT = 10000
WORDNIK_API_KEY = "zqai8u9e5pi2p1ia43ee0359w7loishvhyoll5k06hk5j3ges"

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

def get_random_dict(data, banned=None):
    total_score = sum(header[1] for header in data.keys() if header[0] != banned)
    random_value = random.uniform(0, total_score)
    current_sum = 0
    for header, items in data.items():
        if header == banned:
            continue
        current_sum += header[1]
        if random_value <= current_sum:
            return {header: items}
    return None

def get_random_subgroup(data, banned=None):
    # Get a random dictionary
    random_dict = get_random_dict(data, banned)
    # Extract the only key-value pair from the dictionary
    (header, _), items = list(random_dict.items())[0]
    total_score = sum(subgroup[1] for subgroup in items.keys())
    random_value = random.uniform(0, total_score)
    current_sum = 0
    for subgroup, elements in items.items():
        current_sum += subgroup[1]
        if random_value <= current_sum:
            return (header, {subgroup: elements})
    return None

# Returns a tuple of (header, random_element from the PromptGenerationPool)
def get_random_element(data, banned=None):
    # Get a random subgroup
    header, random_subgroup = get_random_subgroup(data, banned)
    # Extract the only key-value pair from the dictionary
    (subgroup, _), elements = list(random_subgroup.items())[0]
    # Pick a random element from the list
    random_element = random.choice(elements)
    return (header, random_element)

def get_random_elements(data, num_elements=6, banned=None):
    random_elements = []
    for _ in range(num_elements):
        random_element = get_random_element(data, banned)[1]
        random_elements.append(random_element)
    return random_elements

# Returns a dict of elements from get_random_element by (random_element, header)
def get_random_elements_dict(data, num_elements=6, banned=None):
    random_elements = {}
    for _ in range(num_elements):
        random_element = get_random_element(data, banned)
        random_elements[random_element[1]] = random_element[0]
    return random_elements

wordnik_service = Wordnik(api_key=WORDNIK_API_KEY)

def get_random_word():
    return wordnik_service.get_random_word(hasDictionaryDef="true", includePartOfSpeech="noun,verb", minCorpusCount=MIN_CORPUS_COUNT, minDictionaryCount=20)

def get_random_word_list():
    word_list = wordnik_service.get_random_words(hasDictionaryDef="true", includePartOfSpeech="noun,verb", minCorpusCount=MIN_CORPUS_COUNT, minDictionaryCount=20, limit=6)
    while len(word_list) < 6:
        word_list.append(get_random_word())
    return word_list

def prompt_user(word_list):
    print("Pick a word from the following list:")
    for i, word in enumerate(word_list):
        print(f"{i+1}. {word}")
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if choice < 1 or choice > len(word_list):
                raise ValueError
            break
        except ValueError:
            print("Invalid choice. Please enter a number between 1 and", len(word_list))
    chosen_word = word_list[choice-1]
    print("You chose:", chosen_word)
    return chosen_word

if __name__ == "__main__":
    df = pd.read_csv(PROMPT_POOL)
    data = process_dataframe(df)

    word_list = get_random_word_list()
    prompt_user(word_list)

    curated_word_dict = get_random_elements_dict(data)
    choosen_word = prompt_user(list(curated_word_dict.keys()))

    curated_word_list2 = get_random_elements(data, num_elements=5, banned=curated_word_dict[choosen_word])
    curated_word_list2.append(get_random_word())
    prompt_user(curated_word_list2)

    
    

