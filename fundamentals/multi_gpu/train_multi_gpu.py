# -*- coding: utf-8 -*-
"""
An application based on PyTorch documentation examples 
  to train a model using multiple GPUs. The task I've chosen 
  is classifying credit card activity as fradulent. 

A simple PyTorch Sequential model is defined and trained.

After training, the model is evaluated using a F1 score. 

The dataset came from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud. 

Place the "creditcard.csv" file in the same directory as this script.  
"""

import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

import torch.multiprocessing as mp
from torch.utils.data.distributed import DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed import init_process_group, destroy_process_group
import os


class CCModel(nn.Module):
    """
    A simple PyTorch model, with dropouts and batch normalization.
    """

    def __init__(self, _gpu_id):
        super().__init__()
        self.layer1 = nn.Linear(29, 20).to(_gpu_id)
        self.act1 = nn.ReLU().to(_gpu_id)
        self.bat1 = nn.BatchNorm1d(20).to(_gpu_id)
        self.dropout1 = nn.Dropout(0.2)
        self.layer2 = nn.Linear(20, 20).to(_gpu_id)
        self.act2 = nn.ReLU().to(_gpu_id)
        self.bat2 = nn.BatchNorm1d(20).to(_gpu_id)
        self.dropout2 = nn.Dropout(0.2)
        self.output = nn.Linear(20, 2).to(_gpu_id)
        # self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.act1(self.layer1(x))
        x = self.dropout1(x)
        x = self.bat1(x)
        x = self.act2(self.layer2(x))
        x = self.dropout2(x)
        x = self.bat2(x)
        # x = self.sigmoid(self.output(x))
        x = self.output(x)
        return x


class TrainingDataset(Dataset):
    def __init__(self, file_name):
        data = pd.read_csv(file_name)
        X = data.iloc[:, 1:30]  # Exclude Time variable.
        y = data.iloc[:, 30]
        from sklearn.preprocessing import StandardScaler

        X[["Amount"]] = StandardScaler().fit_transform(X[["Amount"]])
        self.X_train = torch.tensor(X.values, dtype=torch.float32)
        self.y_train = torch.tensor(y.values, dtype=torch.long)

    def __len__(self):
        return len(self.y_train)

    def __getitem__(self, idx):
        return self.X_train[idx], self.y_train[idx]


def ddp_setup(rank, world_size):
    """
    Args:
        rank: Unique identifier of each process
        world_size: Total number of processes
    """
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    init_process_group(backend="nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)


class Trainer:
    def __init__(
        self,
        model: torch.nn.Module,
        train_data: DataLoader,
        optimizer: torch.optim.Optimizer,
        gpu_id: int,
        save_every: int,
    ) -> None:
        self.gpu_id = gpu_id
        self.model = model.to(gpu_id)
        self.train_data = train_data
        self.optimizer = optimizer
        self.save_every = save_every
        self.model = DDP(model, device_ids=[gpu_id])
        self.loss_func = torch.nn.CrossEntropyLoss()

    def _run_batch(self, source, targets):
        self.optimizer.zero_grad()
        output = self.model(source)
        # loss = F.cross_entropy(output, targets)
        loss = self.loss_func(output, targets)
        loss.backward()
        self.optimizer.step()

    def _run_epoch(self, epoch):
        b_sz = len(next(iter(self.train_data))[0])
        print(
            f"[GPU{self.gpu_id}] Epoch {epoch} | Batchsize: {b_sz} | Steps: {len(self.train_data)}"
        )
        self.train_data.sampler.set_epoch(epoch)
        for source, targets in self.train_data:
            source = source.to(self.gpu_id)
            targets = targets.to(self.gpu_id)
            self._run_batch(source, targets)

    def _save_checkpoint(self, epoch):
        ckp = self.model.module.state_dict()
        PATH = "checkpoint.pt"
        torch.save(ckp, PATH)
        print(f"Epoch {epoch} | Training checkpoint saved at {PATH}")

    def train(self, max_epochs: int):
        for epoch in range(max_epochs):
            self._run_epoch(epoch)
            if self.gpu_id == 0 and epoch % self.save_every == 0:
                self._save_checkpoint(epoch)


def load_train_objs(rank):
    train_set = TrainingDataset("creditcard.csv")
    model = CCModel(rank)
    # optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)
    optimizer = torch.optim.Rprop(model.parameters(), lr=1e-3)
    # optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    return train_set, model, optimizer


def prepare_dataloader(dataset: Dataset, batch_size: int):
    return DataLoader(
        dataset,
        batch_size=batch_size,
        pin_memory=True,
        shuffle=False,
        sampler=DistributedSampler(dataset),
    )


def main(
    rank: int, world_size: int, save_every: int, total_epochs: int, batch_size: int
):
    """
    This this method called by each GPU process spawned in the host.
    """

    try:
        ddp_setup(rank, world_size)
        dataset, model, optimizer = load_train_objs(rank)
        train_data = prepare_dataloader(dataset, batch_size)
        trainer = Trainer(model, train_data, optimizer, rank, save_every)
        trainer.train(total_epochs)

        if rank == 0:
            import numpy as np
            from sklearn.metrics import accuracy_score, f1_score

            y_preds = []
            for _X, _y in train_data:
                _X = _X.to(0, non_blocking=True)
                trainer.model.eval()
                with torch.no_grad():
                    y_pred = np.argmax(trainer.model(_X).cpu(), axis=1)
                trainer.model.train()
                y_pred = y_pred.numpy()
                y_preds.append(f1_score(_y, y_pred))
            print(f"Reclassification F1 Score: {np.mean(y_preds):.6f}")
        # return trainer, train_data
    except Exception as err:
        print(err)
        raise
    finally:
        destroy_process_group()


if __name__ == "__main__":
    """
    Spawn a number of processes equal to the
      number of GPUs on the host.
    """
    import time

    t0 = time.time()
    world_size = torch.cuda.device_count()
    print(f'Found {world_size} GPUs.')
    # The "main" method passed as the first parameter is defined above.
    mp.spawn(main, args=(world_size, 5, 10, 12000), nprocs=world_size)
    print(f"Duration: {time.time()-t0}")
