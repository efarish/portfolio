# Project: AWS Development

Below are AWS SageMaker projects. These projects are examples of developing code in the AWS SageMaker platform. The code was developed using Python in Jupyter Lab notebooks and Code Editor (Sagemaker’s version of VS Code). They highlight the use of Sagemaker Docker containers to prototype models and perform model hyperparameter tuning on EC2 spot instances. While AWS claims using spot instances for training reduces costs up to 90%, in my experience training on ml.m5.12xlarge and similar instance types results in about a 50% saving in billable time.

- [AutoGluon Kaggle Competition](https://github.com/efarish/portfolio/tree/main/aws/flood): Using AutoML framework AutoGluon to compete in a Kaggle competition.
- [AutoGluon Example](https://github.com/efarish/portfolio/tree/main/aws/AutoGluon): Example of using SageMaker SKLearn container to run a AutoGluon prototyping Python script.
- [Optuna](https://github.com/efarish/portfolio/tree/main/aws/Optuna): Example of using the hyperparameter tuning framework Optuna for a LightGBM model.
