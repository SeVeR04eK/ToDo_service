from abc import ABC, abstractmethod


class MessagePublisher(ABC):
    """Abstract interface for publishing messages to external systems."""

    @abstractmethod
    async def publish_welcome_email(self, username: str, email: str) -> None:
        """Publish a welcome email message.
        
        Args:
            username: The username of the new user.
            email: The email address of the new user.
        """
        ...
