import torch
import torch.nn as nn

class Generator(nn.Module):
    def __init__(self, input_dim):
        super(Generator, self).__init__()
        # Deep enough to learn cycles, but stabilized with specific layers
        self.fc = nn.Sequential(
            nn.Linear(input_dim * 2, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim),
            nn.Sigmoid()
        )
        
    def forward(self, x, m):
        inputs = torch.cat([x, m], dim=1)
        return self.fc(inputs)

class Discriminator(nn.Module):
    def __init__(self, input_dim):
        super(Discriminator, self).__init__()
        # Simplified and "blinded" with high dropout to prevent 0.0000 loss
        self.fc = nn.Sequential(
            nn.Linear(input_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, input_dim),
            nn.Sigmoid()
        )
        
    def forward(self, x, h):
        inputs = torch.cat([x, h], dim=1)
        return self.fc(inputs)