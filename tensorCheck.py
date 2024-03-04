import torch

# Check if CUDA is available
if torch.cuda.is_available():
    print("CUDA is available.")
    # Set the device to GPU
    device = torch.device("cuda")
    # Create a tensor and move it to GPU
    x = torch.tensor([1, 2, 3], device=device)
    # Perform a simple operation
    y = x * 2
    print("Result on GPU:", y)
    # Check if cuDNN is enabled
    if torch.backends.cudnn.enabled:
        print("cuDNN is enabled and available.")
    else:
        print("cuDNN is not available.")
else:
    print("CUDA is not available.")
print("\n\n")


import torch.nn as nn


# Define a simple neural network
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc = nn.Linear(10, 5)

    def forward(self, x):
        return self.fc(x)


# Create the network and move it to GPU
net = SimpleNet().cuda()

# Create some random input data and move it to GPU
input_data = torch.randn(3, 10).cuda()

# Forward pass
output = net(input_data)

print("Output on GPU:", output)
