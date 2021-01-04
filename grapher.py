import pickle
import matplotlib.pyplot as plt
from pathlib import Path

mod_path = Path(__file__).parent

data_path = (mod_path / "Data/data.pickle").resolve()

entry = dict()
epochs = []
loss = []

with open(data_path, 'rb') as f:
    entry = pickle.load(f, encoding = 'latin1')
    epochs = entry['epochs']
    loss = entry['losses']

plt.plot(epochs,loss)
plt.xlabel('Epochs')
plt.ylabel("Loss(%)")
plt.show()


