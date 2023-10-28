from abc import ABC, abstractmethod

from plyer import notification


class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, message: str):
        pass


class PlyerNotificationService(NotificationService):
    def send_notification(self, message: str):
        notification.notify(
            title="Assistant",
            message=message,
            app_icon="assets/work.ico",
            timeout=8
        )
