import argparse
import json
import tqdm
import torch
import torch.nn as nn
import numpy as np

from models import get_model_arch

parser = argparse.ArgumentParser()
parser.add_argument('--in_path', type=str, help='path to .pth file/.pth.tar file')
parser.add_argument('--out_path', type=str, help='path to output saved model architecture')
parser.add_argument('--arch', type=str, help='architecture type of pretrained model')
#TODO support custom architecture definitions

args = parser.parse_args()

in_path = args.in_path
out_path = args.out_path
arch = args.arch

'''
Ensure that all tensor loading is on CPU, as we don't know
what device the original weights were trained on
'''
#checkpoint = torch.load(in_path, map_location = torch.device('cpu'))

'''
Next, store the model architecture within a JSON file so we can recreate the
architecture in TensorFlow later
'''


def pytorch_weights_to_tf_weights(weight_dict):
    '''
    Converts PyTorch weight format to TensorFlow weight format, as PyTorch
    uses (num, channels, height, width) format while TensorFlow uses (num, height, width, channels)
    '''
    tf_weight_dict = {}
    for name, weight in weight_dict.items():
        weight = weight.to('cpu').data.numpy() # convert to numpy array
        if weight.ndim == 4: # check that this is a convolutional layer
            # TODO: Differentiate between conv and depthwise conv
            weight = weight.transpose(2, 3, 0, 1)
            tf_weight_dict[name] = weight
        elif weight.ndim == 2: # this is a linear layer
            weight = weight.transpose(1, 0)
            tf_weight_dict[name] = weight
        else:
            tf_weight_dict[name] = weight
    return weight_dict

def model_arch_conversion(arch_string, out_path):
    model_arch = get_model_arch(arch_string)

    model_arch_list = []

    for module in enumerate(model_arch.modules()):
        if isinstance(module, nn.Conv2d):
            model_arch_list.append({
                        'name': module.__class__.__name__,
                        'in_channels': module.in_channels,
                        'out_channels': module.out_channels,
                        'kernel_size': module.kernel_size,
                        'stride': module.stride,
                        'padding': x.padding,
                    })
        elif isinstance(module, nn.BatchNorm2d):
            model_arch_list.append({
                        'name': module.__class__.__name__
                    })
        elif isinstance(module, nn.Linear):
            model_arch_list.append({
                        'name': module.__class__.__name__,
                        'in_features': module.in_features,
                        'out_features': module.out_features,
                        'bias': module.bias,
                    })
        else:
            return NotImplementedError('A module within your model is not supported.')

    print({
            'name': model_arch.__class__.__name__,
            'arch': model_arch_list,
        })



model_arch_conversion(arch, out_path)





