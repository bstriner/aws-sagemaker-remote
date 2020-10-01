import argparse
from aws_sagemaker_remote.training.main import sagemaker_training_main
import torch
from torch import nn
from torch.utils import data
from torchvision import datasets
import torchvision.transforms as transforms
import aws_sagemaker_remote
import os


class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.model = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, stride=2),
            nn.LeakyReLU(),
            nn.Conv2d(in_channels=32, out_channels=64,
                      kernel_size=3, stride=2),
            nn.LeakyReLU(),
            nn.Conv2d(in_channels=64, out_channels=128,
                      kernel_size=3, stride=1),
            nn.LeakyReLU(),
            nn.Conv2d(in_channels=128, out_channels=10,
                      kernel_size=3, stride=1),
        )

    def forward(self, input):
        return torch.mean(self.model(input), dim=(2, 3))


def main(args):
    print("Training")
    batch_size = 32
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    dataset = data.DataLoader(
        datasets.MNIST(
            root=args.input, download=True, train=True,
            transform=transforms.ToTensor()
        ),
        batch_size=batch_size,
        shuffle=True, num_workers=2, drop_last=False)
    # Create model, optimizer, and criteria
    model = Model().to(device)
    optimizer = torch.optim.Adam(
        params=model.parameters(), lr=args.learning_rate)
    criteria = nn.CrossEntropyLoss()
    model.train()

    for i in range(args.epochs):
        for j, (pixels, labels) in enumerate(dataset):
            pixels, labels = pixels.to(device), labels.to(device)
            logits = model(pixels)
            loss = criteria(input=logits, target=labels)
            accuracy = torch.mean(
                torch.eq(torch.argmax(logits, dim=-1), labels).float())
            loss.backward()
            optimizer.step()
            if j % 100 == 0:
                print("epoch {}, step {}, loss {}, accuracy {}".format(
                    i, j,
                    loss.item(), accuracy.item()
                ))
    os.makedirs(args.model_dir, exist_ok=True)
    torch.save(
        model, os.path.join(args.model_dir, 'model.pt')
    )


def argparse_callback(parser):
    parser.add_argument(
        '--learning-rate',
        default=1e-3,
        type=float,
        help='Learning rate')
    parser.add_argument(
        '--epochs',
        default=5,
        type=int,
        help='Epochs to train')


if __name__ == '__main__':
    sagemaker_training_main(
        script=__file__,
        main=main,
        inputs={
            'input': 'output/data'
        },
        dependencies={
            'aws_sagemaker_remote': aws_sagemaker_remote
        },
        argparse_callback=argparse_callback
    )
