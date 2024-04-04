# Multi-GPU Training

This application is based on PyTorch documentation examples to train a model using multiple GPUs. 

The task I've chosen is classifying credit card activity as fradulent. 

A simple PyTorch Sequential model is defined and trained.

After training, the model is evaluated using a F1 score. 

The dataset came from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud. 

Files: 

- [train_multi_gpu.py](https://github.com/efarish/portfolio/blob/main/fundamentals/multi_gpu/train_multi_gpu.py) - A PyTorch script that builds and trains the model.
- [MultiGPU_1_V100.ipynb](https://github.com/efarish/portfolio/blob/main/fundamentals/multi_gpu/MultiGPU_1_V100.ipynb) - The results of training the script on one V100 GPU.
- [MultiGPU_1_V100.ipynb](https://github.com/efarish/portfolio/blob/main/fundamentals/multi_gpu/MultiGPU_1_V100.ipynb) - The results of training the script on o4 V100 GPUs.

Results:

Below is a screen shot of using the `nvidia-smi` utility to see the GPU utilization.

![alt text](https://github.com/efarish/portfolio/blob/main/fundamentals/multi_gpu/assets/img/nvidia_v_gpu.png)

Interestingly, the training duration is the same when using 1 v100 GPU and 4 v100 GPUs. This probably means the model I used is not big enough to evidence the advantage of using multiple GPUs. 




