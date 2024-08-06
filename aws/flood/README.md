# Project: Kaggle Flood Competition

This project utilizes the AutoML framework AutoGluon to compete in the Kaggle competition [Regression with a Flood Prediction Dataset](https://www.kaggle.com/competitions/playground-series-s4e5/overview). Below are the frameworks and platforms used for this project.

- AutoGluon - A AutoML framework for prototyping ML algorithms and ensemble models. 
- SageMaker Studio - Jupyter Lab and Code Editor was used to develop this notebook and the accompanying scripts. 
- GitHub - The code repository used for this project.
- SageMaker Sklearn Docker Image - A prebuilt Amazon SageMaker Docker container used to train the AutoGluon models on AWS spot instances. 

Results: Using SageMaker training job reduced training costs by almost 50%. This is a regression task and the performance metric is $R^2$. My model's score was 0.86884. The top Kaggle score was 0.86905.  
