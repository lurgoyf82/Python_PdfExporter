import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DirectoryMonitor:
    """
    A class to monitor a directory for file system changes and execute actions when conditions are met.
    """

    def __init__(self, directory: str):
        """
        Initializes the DirectoryMonitor with the directory to watch.

        :param directory: The directory path to monitor.
        """
        if not os.path.exists(directory):
            raise ValueError(f"The directory '{directory}' does not exist.")
        self.directory = directory
        self._actions = []  # List of actions to execute when conditions are met
        self._observer = Observer()

    def register_action(self, condition: callable, action: callable):
        """
        Registers an action to execute when a condition is met.

        :param condition: A callable that takes an event and returns True if the action should be executed.
        :param action: A callable to execute when the condition is met.
        """
        self._actions.append((condition, action))

    def start(self):
        """
        Starts monitoring the directory.
        """
        event_handler = _DirectoryEventHandler(self._actions)
        self._observer.schedule(event_handler, self.directory, recursive=False)
        self._observer.start()
        print(f"Started monitoring directory: {self.directory}")

    def stop(self):
        """
        Stops monitoring the directory.
        """
        self._observer.stop()
        self._observer.join()
        print(f"Stopped monitoring directory: {self.directory}")


class _DirectoryEventHandler(FileSystemEventHandler):
    """
    Private event handler to process file system events and execute registered actions.
    """

    def __init__(self, actions):
        """
        Initializes the event handler with the registered actions.

        :param actions: A list of (condition, action) tuples.
        """
        super().__init__()
        self._actions = actions

    def on_created(self, event):
        """
        Executes registered actions when a file is created.

        :param event: The file system event.
        """
        if event.is_directory:
            return  # Ignore directories
        for condition, action in self._actions:
            if condition(event):
                action(event)


# Example usage
if __name__ == "__main__":
    from win10toast import ToastNotifier

    def is_pdf(event):
        """Condition to check if the created file is a PDF."""
        return event.src_path.endswith(".pdf")

    def notify(event):
        """Action to show a Windows notification."""
        notifier = ToastNotifier()
        filename = os.path.basename(event.src_path)
        notifier.show_toast(
            "New PDF Detected",
            f"File '{filename}' has been added to the directory!",
            duration=5,
        )

    directory_to_watch = input("Enter the directory to monitor: ").strip()

    try:
        monitor = DirectoryMonitor(directory_to_watch)
        monitor.register_action(is_pdf, notify)
        monitor.start()
        print("Press Ctrl+C to stop.")
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        monitor.stop()
    except ValueError as e:
        print(e)
