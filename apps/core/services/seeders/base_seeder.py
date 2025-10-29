from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any


class BaseSeeder(ABC):
    
    def __init__(self, stdout=None, style=None):
        self.stdout = stdout
        self.style = style

    def log(self, message: str, style_method: str = 'SUCCESS') -> None:
        if self.stdout:
            if self.style and hasattr(self.style, style_method):
                self.stdout.write(getattr(self.style, style_method)(message))
            else:
                self.stdout.write(message)

    def log_info(self, message: str) -> None:
        self.log(f'ℹ️  {message}', 'WARNING')

    def log_success(self, message: str) -> None:
        self.log(f'✓ {message}', 'SUCCESS')

    def log_error(self, message: str) -> None:
        self.log(f'✗ {message}', 'ERROR')

    @abstractmethod
    def seed(self) -> None:
        pass

    def get_or_skip(self, model, **kwargs) -> Tuple[Optional[Any], bool]:
        try:
            obj, created = model.objects.get_or_create(**kwargs)
            return obj, created
        except Exception as e:
            self.log_error(f'Error creating {model.__name__}: {str(e)}')
            return None, False
