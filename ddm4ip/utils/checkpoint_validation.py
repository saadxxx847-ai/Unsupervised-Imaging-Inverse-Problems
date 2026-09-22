"""Finite tensor checks for trusted, independently hashed checkpoint artifacts."""
import torch

def require_finite_tensors(payload, path='checkpoint'):
    if isinstance(payload, torch.nn.Module):
        require_finite_tensors(payload.state_dict(), path)
    elif isinstance(payload, torch.Tensor):
        if not torch.isfinite(payload).all():
            raise ValueError(f'non-finite checkpoint tensor: {path}')
    elif isinstance(payload, dict):
        for key, value in payload.items():
            require_finite_tensors(value, f'{path}.{key}')
    elif isinstance(payload, (tuple, list)):
        for index, value in enumerate(payload):
            require_finite_tensors(value, f'{path}[{index}]')
