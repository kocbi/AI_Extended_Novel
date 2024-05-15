"""
Train a model
"""
import os
import sys
import pickle
from contextlib import nullcontext
import torch
import tiktoken

from model import Model


# Hyperparameters
batch_size = 12  # How many batches per training step
context_length = 128  # Length of the token chunk each batch
max_iters = 20000  # Total of training iterations <- Change this to smaller number for testing
learning_rate = 1e-3  # 0.001
eval_interval = 50  # How often to evaluate
eval_iters = 20  # Number of iterations to average for evaluation
device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Use GPU if it's available.
TORCH_SEED = 1337
torch.manual_seed(TORCH_SEED)


# AIM Logs



# 准备训练数据
with open('../data/scifi.txt', 'r', encoding="utf-8") as file:
    text = file.read()


# Using TikToken (Same as GPT3) to tokenize the source text
encoding = tiktoken.get_encoding("cl100k_base")
tokenized_text = encoding.encode(text)
# max_token_value = max(tokenized_text)+1  # the maximum value of the tokenized numbers
tokenized_text = torch.tensor(tokenized_text, dtype=torch.long, device=device)  # 将77,919个tokens 转换到Pytorch张量中

total_tokens = encoding.encode_ordinary(text)
print(f"数据集合计有 {len(total_tokens):,} tokens")



# vocab = sorted(list(set(text)))
# vocab_size = max_token_value = len(vocab)

# char2idx = {char: idx for idx, char in enumerate(vocab)}
# idx2char = {idx: char for char, idx in char2idx.items()}
# encode = lambda x: [char2idx[char] for char in x]
# decode = lambda idxs: ''.join([idx2char[idx] for idx in idxs])
# tokenized_text = torch.tensor(encode(text), dtype=torch.long)

# Split train and validation
train_size = int(len(tokenized_text) * 0.9)
train_data = tokenized_text[:train_size]
val_data = tokenized_text[train_size:]


# Initialize the model
model = Model().to(device)

# get batch
def get_batch(split: str):
    data = train_data if split == 'train' else val_data
    idxs = torch.randint(low=0, high=len(data) - context_length, size=(batch_size,))
    x = torch.stack([data[idx:idx + context_length] for idx in idxs]).to(device)
    y = torch.stack([data[idx + 1:idx + context_length + 1] for idx in idxs]).to(device)
    return x, y


# calculate the loss
@torch.no_grad()
def estimate_loss():
    out = {}
    model.eval()
    for split in ['train', 'valid']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            x_batch, y_batch = get_batch(split)
            logits, loss = model(x_batch, y_batch)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out


# Create the optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
tracked_losses = list()
for step in range(max_iters):
    if step % eval_iters == 0 or step == max_iters - 1:
        losses = estimate_loss()
        tracked_losses.append(losses)
        print('Step:', step, 'Training Loss:', round(losses['train'].item(), 3), 'Validation Loss:', round(losses['valid'].item(), 3))


    xb, yb = get_batch('train')
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

# Save the model
torch.save(model.state_dict(), 'model/model-scifi.pt')





