import warnings
import os
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.ensemble import HistGradientBoostingClassifier,RandomForestClassifier 
from CustomMethods import dropTargets, model_fit_evaluate
from sklearn.model_selection import StratifiedKFold

if __name__ == "__main__":
    ROOT = Path('/home', 'gmarvin', 'Network_1_Znanstveni_Rad')
    # ROOT = Path(os.getcwd())
    INPUT_OUTPUT_DATA = Path(ROOT, 'input_output_data_0_P', 'input_output_merged_0_P.csv')
    INPUT_OUTPUT_DATA_OLD = Path(ROOT,'input_output_data_0_P_old', 'input_output_merged_0_P.csv')

    X_y = pd.read_csv(INPUT_OUTPUT_DATA, header=None)
    X_y_old = pd.read_csv(INPUT_OUTPUT_DATA_OLD, header=None)


    y = X_y.drop(X_y_old.columns[4:], axis=1)
    X = X_y.drop(X_y_old.columns[:4], axis=1).values

    y_ID = LabelEncoder().fit_transform(dropTargets(y, 0))

    y_old = X_y_old.drop(X_y_old.columns[4:], axis=1)
    X_old = X_y_old.drop(X_y_old.columns[:4], axis=1).values

    y_old_ID = LabelEncoder().fit_transform(dropTargets(y_old, 0))

    HGB = HistGradientBoostingClassifier(learning_rate=0.15216, loss='categorical_crossentropy', random_state=42)
    RFC = RandomForestClassifier(n_jobs=-1, random_state=42)

    HGB_OLD = HistGradientBoostingClassifier(learning_rate=0.15216, loss='categorical_crossentropy', random_state=42)
    RFC_OLD = RandomForestClassifier(n_jobs=-1, random_state=42)

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=1997)
    model_fit_evaluate( X=X_old,
                        y=y_old_ID,
                        test_size=0.16,
                        cv=cv,
                        random_state=1997,
                        model=HGB_OLD)

    model_fit_evaluate( X=X_old,
                        y=y_old_ID,
                        test_size=0.16,
                        cv=cv,
                        random_state=1997,
                        model=RFC_OLD)

    # model_fit_evaluate( X=X,
    #                     y=y_ID,
    #                     test_size=0.16,
    #                     cv=cv,
    #                     random_state=1997,
    #                     model=HGB)

    # model_fit_evaluate( X=X,
    #                     y=y_ID,
    #                     test_size=0.16,
    #                     cv=cv,
    #                     random_state=1997,
    #                     model=HGB)

