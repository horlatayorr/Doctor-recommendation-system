import csv
import math
import re

import inflect
import pandas as pd

from .stop_words import stop_words

df = pd.read_csv("./datasets/Training.csv")
p = inflect.engine()


class RecommendDoctor:
    def __init__(self) -> None:
        self.columns = df.columns[:-2]

    def remove_stop_words(self, sentence):
        new_word_list = []
        # split if the , or space is found in the sentence
        splitted_words = re.split(r"[,\s]+", sentence.lower())
        for word_ in splitted_words:
            if word_ not in stop_words:
                word = p.singular_noun(word_)
                if word:
                    cleaned_word = self.clean_numbers_and_special_characters(word)
                cleaned_word = word
                new_word_list.append(cleaned_word)
        return [i for i in new_word_list if i]

    def clean_numbers_and_special_characters(self, word):
        pattern = "[^a-zA-Z]"
        if re.match(pattern, word):
            formatted_word = re.sub(pattern, "", word)
            return formatted_word
        return word

    def create_vector_from_input(self, formatted_word_list):
        input_vector = []
        for column in self.columns:
            splitted_column = re.split("_", column)
            input_vector.append(1 if set(splitted_column).issubset(set(formatted_word_list)) else 0)
        return input_vector

    def dot_product(self, vector1, vector2):
        return sum([vector1[i] * vector2[i] for i in range(len(vector1))])

    def magnitude(self, vector):
        return math.sqrt(sum([x**2 for x in vector]))

    def cosine_similarity(self, vector1, vector2):
        return self.dot_product(vector1, vector2) / (self.magnitude(vector1) * self.magnitude(vector2))

    def get_cosine_similarities(self, vec2):
        similarities = []
        with open("./datasets/updated_training_data.csv") as file_obj:
            reader_obj = csv.reader(file_obj)
            next(reader_obj)
            for row in reader_obj:
                int_row = [int(num) for num in row[1:]]
                try:
                    result = self.cosine_similarity(int_row, vec2)
                except:
                    result = 0
                similarities.append([int(row[0]), result])

        return similarities

    def sort_similarities(self, similarities, top_n):
        sorted_scores = sorted(similarities, key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_n]

    def give_disease(self, input_text, no_of_doctors=5):
        disease_result = []
        formatted_list = self.remove_stop_words(input_text)
        vec2 = self.create_vector_from_input(formatted_list)
        similarities = self.get_cosine_similarities(vec2)
        results = self.sort_similarities(similarities, no_of_doctors)
        for res in results:
            disease_result.append(df.iloc[res[0]]["prognosis"])
        return set(disease_result)


if __name__ == "__main__":
    d = RecommendDoctor()
    input_text = input("Enter your symptoms: ")
    res = d.give_disease(input_text, 50)
    print(res)
