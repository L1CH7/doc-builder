import os

# Mapping from Linux mount point to Windows path
# TODO: Make this configurable in global config if needed, or keep hardcoded for this specific env
LINUX_MOUNT_POINT = "/mnt/win10-share"
WINDOWS_DRIVE_LETTER = "Z:"

def linux_to_windows_path(linux_path):
    """
    Converts a Linux path (e.g., /mnt/win10-share/project/file.md)
    to a Windows path (e.g., Z:\project\file.md).
    """
    abs_path = os.path.abspath(linux_path)
    if abs_path.startswith(LINUX_MOUNT_POINT):
        rel_path = abs_path[len(LINUX_MOUNT_POINT):]
        # Ensure regex/replace handles basic forward slashes to backslashes
        win_path = WINDOWS_DRIVE_LETTER + rel_path.replace("/", "\\")
        return win_path
    else:
        # Fallback or error if path is not in the shared mount
        # For now, just return as is or raise error. 
        # But maybe the user passes relative paths which get resolved.
        # Let's assume absolute paths are passed here.
        raise ValueError(f"Path {linux_path} is not under {LINUX_MOUNT_POINT}")
