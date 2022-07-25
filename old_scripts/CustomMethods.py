import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RepeatedKFold
from sklearn.metrics import accuracy_score, r2_score
from sklearn.decomposition import PCA

def plot_scree(X):

    pca = PCA()
    pca.fit(X)

    singular_values = pca.singular_values_
    PCs = [f"PC{i+1}" for i in range(len(singular_values))]

    explained_variance_ratio = pca.explained_variance_ratio_

    plt.figure(figsize=(20, 10))
    plt.bar(PCs, singular_values, color="r")
    plt.title("original data")

    plt.figure(figsize=(20, 10))
    plt.bar(PCs, explained_variance_ratio * 100, color="r")
    plt.title("scree plot")
    plt.show()


def dropTargets(y, target_to_work_with):

    """
    Function to drop unnecessary targets
    """

    # all_targets = ["ID", "A", "Cd", "start_time"]
    all_targets = [i for i in range(4)]


    targets_to_drop = [
        target for target in all_targets if target != target_to_work_with
    ]
    
    y = y.drop(targets_to_drop, axis=1).values.ravel()
    return y


def myRandomGridSearch(X, y, pipeline, cv, grid, n_iter, n_jobs, seed):
    """
    Does RandomGrid Search 
    """
    random_grid_search = RandomizedSearchCV(
    estimator=pipeline,
    param_distributions=grid,
    n_iter=n_iter,
    n_jobs=n_jobs,
    cv=cv,
    verbose=2,
    random_state=seed,
    )

    random_grid_search.fit(X, y)
    best_params = random_grid_search.best_params_
    best_score = random_grid_search.best_score_

    print("\n")
    print("RESULTS FOR RANDOM SEARCH:")
    pprint(grid)
    print("==========================")
    print(f"Best score: {best_score}")
    for k in best_params.keys():
        print(f"{k}: {best_params[k]}")
    print("==========================")
    
def top_n_probas(predict_probability, y_test, model, N):

    classes = model.classes_

    preds_idx = np.argsort(-predict_probability, axis=1)[:, :N]
    true_positive = 0
    for i, row_idx in enumerate(preds_idx):
        topn_row = [classes[idx] for idx in row_idx]
        if y_test[i] in topn_row:
            true_positive += 1
        else:
            true_positive += 0

    perc = true_positive / y_test.shape[0]
    print(f"Accuracy of prediction in top {N} predictions: {perc*100}%")

def model_fit_evaluate(X, y, test_size, cv, random_state, model, purpose):

    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=test_size, random_state=random_state)
    print("==================================================================================================")
    print(f"Trainig on {train_X.shape[0]} instances...")
    print(f"Testing on {test_X.shape[0]} instances...")
    print(f"Evaluating model for prediction of {purpose}")

    model.fit(train_X, train_y)

    kfold = cv

    cross_val_results = cross_val_score(model, X, y, cv=kfold)

    cross_val_mean = cross_val_results.mean() * 100
    cross_val_std = cross_val_results.std() * 100

    pred_o = model.predict(test_X)
    predictions = [value for value in pred_o]

    accuracy = accuracy_score(test_y, predictions)
    acc = accuracy * 100

    probs = model.predict_proba(test_X)

    top_n_probas(probs, test_y, model, N=1)
    top_n_probas(probs, test_y, model, N=3)
    top_n_probas(probs, test_y, model, N=5)
    top_n_probas(probs, test_y, model, N=10)

    print(f"Model {model}")
    print(f"Accuracy: {acc}%")
    print(f"Mean/std: {cross_val_mean}/{cross_val_std}")
    print("==================================================================================================")

def evaluate_regression_model(X, y, cv, model, purpose):
    
    print("==================================================================================================")
    print(f"Evaluating model for prediction of {purpose}")
    r2_score_st = list()
    
    i = 0
    for train_ix, test_ix in cv.split(X):

        X_train, X_test = X[train_ix], X[test_ix]
        y_train, y_test = y[train_ix], y[test_ix]
        
        model.fit(X_train, y_train)
        
        print(f'Training on {X_train.shape[0]} istances ...')
    
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test,y_pred)
        
        print(f'Results for {i+1}. fold')
        print(f'R2(A): {np.round(r2,4) * 100}%')    
        r2_score_st.append(r2)
        i+=1
    
    r2_mean = np.mean(r2_score_st)
    r2_std = np.std(r2_score_st)
    print(f'R2 score mean: {r2_mean}')
    print(f'R2 score std: {r2_std}')
    print("==================================================================================================")
