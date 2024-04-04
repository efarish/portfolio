# Multi-GPU Training

This application is based on PyTorch documentation examples to train a model using multiple GPUs. 

The task I've chosen is classifying credit card activity as fradulent. 

A simple PyTorch Sequential model is defined and trained.

After training, the model is evaluated using a F1 score. 

The dataset came from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud. 

Two trainings were done using AWS SageMaker:

- ml.p3.2xlarge with 1 v100 GPU with 16 gigs of memory
- ml.p3.8xlarge with 4 v100 GPUs with 64 gigs of memory

Files: 

- [train_multi_gpu.py](https://github.com/efarish/portfolio/blob/main/fundamentals/multi_gpu/train_multi_gpu.py) - A PyTorch script that builds and trains the model.
- [MultiGPU_1_V100.ipynb](https://github.com/efarish/portfolio/blob/main/fundamentals/multi_gpu/MultiGPU_1_V100.ipynb) - The results of training the script on one V100 GPU.
- [MultiGPU_4_V100.ipynb](https://github.com/efarish/portfolio/blob/main/fundamentals/multi_gpu/MultiGPU_4_V100.ipynb) - The results of training the script on o4 V100 GPUs.

## Results

Below is a screen shot of using the `nvidia-smi` utility to see the GPU utilization.

![alt text](https://github.com/efarish/portfolio/blob/main/fundamentals/multi_gpu/assets/img/nvidia_v_gpu.png)

Interestingly, the training duration is the same when using 1 v100 GPU and 4 GPUs. This is probably due to my model not being large enough to evidence the benefit of using multiple GPUs.

However, aside from the screenshot above, the evidence that training has been split amoung the 4 GPUs is seen by the number of steps taken for each epoc. For the 1 v100 GPU training, there are 24 steps for each epoc. The 4 v100 GPU training only takes 6 steps per epoc.




