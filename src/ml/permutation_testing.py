import pandas as pd
import numpy as np
from sys import argv, exit
from warnings import warn
import matplotlib.pyplot as plt

from sklearn.model_selection import permutation_test_score
from data_processing.read_data import read_preprocessed_data
from voting_classifier import generate_tuple_lists, NAMES, CLASSIFIERS
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import accuracy_score

VERBOSE = True

# DATA
DATA_FOLDER = '../../data'
INPUT_FOLDER = '%s/animals' % DATA_FOLDER

## Animals
INPUT_FILE = '%s/label_scores.txt' % INPUT_FOLDER
# PLANTS
# INPUT_FILE = "../../data/plants/label_scores.txt"
FEATURES_FILE = '%s/aaindex/aaindex_used.txt' % DATA_FOLDER
OUTPUT_FILE = '%s/permutation_testing_1.csv' % INPUT_FOLDER

if __name__ == '__main__':
    if len(argv) < 2:
        raise Exception('Please specify a mode. Choices: run, read')

    cols = ['Accuracy', 'Permuted accuracy']

    if argv[1] == 'run':
        if len(argv) < 3:
            raise Exception(
                'Please specify number of iterations. Usage: python permutation_testing.py run [ iterations ]'
            )
        num_iter = int(argv[2])
        y, X = read_preprocessed_data(INPUT_FILE, FEATURES_FILE, format='df')
        train_size = int(len(y) * 0.66)
        y_train, X_train = y.iloc[:train_size, :], X.iloc[:train_size, :]
        y_test, X_test = y.iloc[train_size:, :], X.iloc[train_size:, :]

        estimators = generate_tuple_lists(CLASSIFIERS, NAMES)
        accuracy_df = pd.DataFrame(columns=cols)

        for i in range(num_iter):
            print('loop iteration %d' % i)
            y_permuted = y.sample(frac=1)
            y_permuted_train = y_permuted.iloc[:train_size, :]
            y_permuted_test = y_permuted.iloc[train_size:, :]

            vc = VotingClassifier(estimators, voting='hard')
            vc_permuted = VotingClassifier(estimators, voting='hard')

            vc.fit(X_train, y_train)
            vc_permuted.fit(X_train, y_permuted_train)

            predictions = vc.predict(X_test)
            predictions_permuted = vc_permuted.predict(X_test)

            accuracy = accuracy_score(predictions, y_test)
            accuracy_permuted = accuracy_score(predictions, y_permuted_test)

            row_df = pd.DataFrame(columns=cols, data=[[accuracy, accuracy_permuted]])
            accuracy_df = accuracy_df.append(row_df)

        accuracy_df.to_csv(OUTPUT_FILE)
    elif argv[1] == 'read':
        accuracy_df = pd.read_csv(OUTPUT_FILE)
        fig = plt.figure()
        differences = np.subtract(accuracy_df[cols[0]], accuracy_df[cols[1]])
        # plt.plot(range(len(accuracy_df)), accuracy_df[cols[0]])
        # plt.plot(range(len(accuracy_df)), accuracy_df[cols[1]])
        # plt.plot(differences)
        plt.hist(differences, color='#A5DEF1')
        plt.title('Prediction accuracy difference (permuted vs. non-permuted)')
        # plt.legend(['non-permuted', 'permuted'])
        plt.xlabel('Frequency')
        plt.ylabel('Difference in accuracy')
        plt.set_cmap('BrBG')
        # plt.xticks(range(0, len(accuracy_df) + 1, 2))
        plt.show()
