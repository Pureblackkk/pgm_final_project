import torch

class DatasetIterater(object):
    def __init__(self, batches, batchSize, device) -> None:
        self.batches = batches
        self.batchSize = batchSize
        self.batchNum = len(batches) // batchSize
        
        # Record if batch % batch_size !== 0 
        self.residue = True if len(batches) % batchSize != 0 else False

        self.index = 0
        self.device = device

    def _to_tensor(self, datas):
        x = torch.LongTensor([_[0] for _ in datas]).to(self.device)
        y = torch.LongTensor([_[1] for _ in datas]).to(self.device)

        