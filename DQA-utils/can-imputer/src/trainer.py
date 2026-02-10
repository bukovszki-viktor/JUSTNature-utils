import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from src.gain import Generator, Discriminator

class GAINTrainer:
    def __init__(self, input_dim, alpha=100, lr=0.001):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.input_dim = input_dim
        self.alpha = alpha

        self.G = Generator(input_dim).to(self.device)
        self.D = Discriminator(input_dim).to(self.device)

        self.optimizer_G = optim.Adam(self.G.parameters(), lr=lr)
        self.optimizer_D = optim.Adam(self.D.parameters(), lr=lr * 0.5) # D learns slower

        self.mse_loss = nn.MSELoss()

    def _sample_hint(self, mask, hint_rate=0.7):
        batch_size, dim = mask.shape
        h_matrix = torch.rand(batch_size, dim).to(self.device)
        h_matrix = (h_matrix < hint_rate).float()
        return mask * h_matrix

    def train_step(self, x, m, train_d=True):
        batch_size = x.size(0)
        
        # 1. Prepare Imputation
        z = torch.rand(batch_size, self.input_dim).to(self.device) * 0.01
        x_with_noise = x * m + z * (1 - m)
        
        # 2. Train Discriminator (Only if requested)
        d_loss_val = 0
        if train_d:
            self.optimizer_D.zero_grad()
            with torch.no_grad():
                imputed_x = self.G(x_with_noise, m)
                x_hat = x * m + imputed_x * (1 - m)
            
            h = self._sample_hint(m)
            d_prob = self.D(x_hat, h)
            
            # Label Smoothing: Use 0.9 instead of 1.0 to prevent D overconfidence
            d_loss = -torch.mean(m * 0.9 * torch.log(d_prob + 1e-8) + (1 - m) * (1 - 0.1) * torch.log(1 - d_prob + 1e-8))
            d_loss.backward()
            self.optimizer_D.step()
            d_loss_val = d_loss.item()

        # 3. Train Generator
        self.optimizer_G.zero_grad()
        imputed_x = self.G(x_with_noise, m)
        x_hat = x * m + imputed_x * (1 - m)
        h = self._sample_hint(m)
        d_prob = self.D(x_hat, h)
        
        g_loss_adv = -torch.mean((1 - m) * torch.log(d_prob + 1e-8))
        g_loss_mse = self.mse_loss(m * x, m * imputed_x) / (torch.mean(m) + 1e-8)
        
        g_loss_total = g_loss_adv + self.alpha * g_loss_mse
        g_loss_total.backward()
        self.optimizer_G.step()

        return d_loss_val, g_loss_total.item()

    def save_models(self, path_g, path_d):
        torch.save(self.G.state_dict(), path_g)
        torch.save(self.D.state_dict(), path_d)