"""Base model"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import signature


@dataclass(kw_only=True)
class SynapseModel(ABC):
    """Synapse base model"""

    @classmethod
    def from_kwargs(cls, **kwargs):
        """Add kwargs"""
        # fetch the constructor's signature
        cls_fields = {field for field in signature(cls).parameters}

        # split the kwargs into native ones and new ones
        native_args, new_args = {}, {}
        for name, val in kwargs.items():
            if name in cls_fields:
                native_args[name] = val
            else:
                new_args[name] = val

        # use the native ones to create the class ...
        ret = cls(**native_args)

        # ... and add the new ones by hand
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)
        return ret

    @abstractmethod
    def _get_url(self) -> str:
        """Get endpoint path"""
        ...

    @abstractmethod
    def _post_url(self) -> str:
        """Post endpoint path"""
        ...

    @abstractmethod
    def _put_url(self) -> str:
        """Put endpoint path"""
        ...

    @abstractmethod
    def _delete_url(self) -> str:
        """Delete endpoint path"""
        ...
