# xG_model_python
This repository contains code to predict Expected Goals (xG) from football (soccer) events data using machine learning models.
## What'is an xG model?
Expected Goals **(xG)** is a statistical metric in football that estimates the likelihood of a scoring opportunity resulting in a goal. Machine learning models, such as Logistic Regression, Random Forest, XGBoost, and Deep Neural Networks, are trained on historical shot data and various factors like shot location, angle, and type (header, free kick, etc.) to assign a probability value between 0 (almost no chance) and 1 (almost certain goal). xG helps analyze the quality of scoring opportunities and assess team and player performance beyond just goals scored
# Machine Learning  and "xG"
xG modeling is a classification problem where machine learning models are trained on historical shot data and various factors like location, angle, and type. These models predict the probability of a shot resulting in a goal (between 0 and 1). **xG** goes beyond goals scored to analyze the quality of chances and assess team and player performance.

Note: A significant portion of this code was inspired by the Kaggle page: Expected Goals (xG) Model by Usama Waheed.: [https://www.kaggle.com/code/usamawaheed/expected-goals-xg-model]
# In this work 
In this project, I have added new features such as score_17_18, which represents the scores of the top five European leagues from the 2017-2018 season, sourced from the UEFA website. I have also calculated the possession percentage of each team, which is used in my model.

Feel free to make any further adjustments as needed!
