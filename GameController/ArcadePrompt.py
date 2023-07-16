import asyncio
import pandas as pd
import random
from random_word import Wordnik
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

PROMPT_POOL = 'Assets\PromptsGenerationPool.csv'
PREPOSITIONS = 'Assets\Preposition.csv'
MIN_CORPUS_COUNT = 10000
WORDNIK_API_KEY = "zqai8u9e5pi2p1ia43ee0359w7loishvhyoll5k06hk5j3ges"
ROW_SIZE = 3

_generation_data = None
_prepositions = None

@staticmethod
def initlisation():
    global _generation_data
    global _prepositions
    _generation_data = process_generation_poll(pd.read_csv(PROMPT_POOL))
    _prepositions = process_prepositions()

initlisation()

@staticmethod
def process_generation_poll(df):
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

@staticmethod
def process_prepositions():
    data = []
    with open(PREPOSITIONS, 'r') as f:
        prepositions = f.readlines()
        data = prepositions[0].split(',')
    return data


def get_random_dict(data, banned=None):
    total_score = sum(score for (header, score) in data.keys() if header != banned)
    random_value = random.uniform(0, total_score)
    current_sum = 0
    for (header, score), items in data.items():
        if header == banned:
            continue
        current_sum += score
        if random_value <= current_sum:
            return {(header, score) : items}
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

#Should I make it more common for nouns to show up (ie change ratio of nouns to verbs?)
def get_random_word_list(length=6):
    word_list = wordnik_service.get_random_words(hasDictionaryDef="true", includePartOfSpeech="noun,verb", minCorpusCount=MIN_CORPUS_COUNT, minDictionaryCount=20, limit=length)
    while len(word_list) < length:
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

def comma_seperated_output(str1, str2, str3):
    return f"{str1}, {str2}, {str3}"

def randomize_strings(str1, str2, str3):
    # prepositions = process_prepositions()
    strings = [str1, str2, str3]
    random.shuffle(strings)
    result = ""
    for i in range(len(strings) - 1):
        result += strings[i] + " " +  random.choice(_prepositions) + " "
    result += strings[-1]
    return result
    # return f"{strings[0]} {random.choice(prepositions)} {strings[1]} + {random.choice(prepositions)} + {strings[2]}"

async def sendPhase1Messages(bot, room):
    await room.broadcast(bot, "ArcadePhase1p1")
    await asyncio.sleep(2)
    await room.broadcast(bot, "ArcadePhase1p2")
    await asyncio.sleep(2)

def make_keyboard(word_list):
    keyboard = []
    for i in range(0, len(word_list), ROW_SIZE):
        row = []
        for j in range(ROW_SIZE):
            if i+j < len(word_list):
                row.append(InlineKeyboardButton(word_list[i+j], callback_data=str(i+j)))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)    

async def sendPhase2Messages(bot, room, player):
    curated_word_dict = get_random_elements_dict(_generation_data)
    player.sendMessage("ArcadePhase2p1")

async def beginPhase1(bot, room):
    asyncio.create_task(sendPhase1Messages(bot, room))
    # df = pd.read_csv(PROMPT_POOL)
    # data = process_generation_poll(df)

    curated_word_dict = get_random_elements_dict(_generation_data)
    choosen_word1 = prompt_user(list(curated_word_dict.keys()))

    word_list = get_random_word_list()
    choosen_word2 = prompt_user(word_list)

    curated_word_list2 = get_random_elements(_generation_data, num_elements=5, banned=curated_word_dict[choosen_word1])
    choosen_word3 = prompt_user(curated_word_list2)

    print("Comma seperated prompt is: " + choosen_word1 + ", " + choosen_word2 + ", " + choosen_word3)
    print("Randomized prompt is: " + randomize_strings(choosen_word1, choosen_word2, choosen_word3))

if __name__ == "__main__":
    df = pd.read_csv(PROMPT_POOL)
    data = process_generation_poll(df)

    curated_word_dict = get_random_elements_dict(data)
    choosen_word1 = prompt_user(list(curated_word_dict.keys()))

    word_list = get_random_word_list()
    choosen_word2 = prompt_user(word_list)

    # curated_word_list2 = get_random_elements(data, num_elements=5, banned=curated_word_dict[choosen_word1])
    curated_word_list2 = get_random_elements(data, num_elements=3, banned=curated_word_dict[choosen_word1])
    curated_word_list2.extend(get_random_word_list(length=3))
    choosen_word3 = prompt_user(curated_word_list2)

    print("Comma seperated prompt is: " + choosen_word1 + ", " + choosen_word2 + ", " + choosen_word3)
    print("Random preposition prompt is: " + randomize_strings(choosen_word1, choosen_word2, choosen_word3))
    print("Random preposition prompt is: " + randomize_strings(choosen_word1, choosen_word2, choosen_word3))


