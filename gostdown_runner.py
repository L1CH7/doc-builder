#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import glob

# Configuration
# Mapping Linux mount point to Windows drive
LINUX_MOUNT_PREFIX = "/mnt/win10-share"
WINDOWS_DRIVE_PREFIX = "Z:"
VM_USER = "vaivanov"
VM_HOST = "192.168.122.2"
BUILD_SCRIPT_WIN_PATH = r"Z:\gostdown-proj\gostdown\build.ps1"

def linux_to_windows_path(linux_path):
    """Converts a Linux path in the shared directory to a Windows path."""
    abs_path = os.path.abspath(linux_path)
    if not abs_path.startswith(LINUX_MOUNT_PREFIX):
        raise ValueError(f"Path {linux_path} is not within the shared directory {LINUX_MOUNT_PREFIX}. Please move your input files there.")
    
    rel_path = abs_path[len(LINUX_MOUNT_PREFIX):]
    # Ensure correct slash direction for Windows
    win_path = WINDOWS_DRIVE_PREFIX + rel_path.replace("/", "\\")
    return win_path

def run_build(args):
    project_dir = args.input_dir
    output_dir = args.output_dir
    
    # 1. Prepare Paths
    # We scan for MD files in the project directory
    # Order matters! We can look for an 'order.txt' or simple sort.
    # For now: alphabetical or specific standard names.
    md_files = sorted(glob.glob(os.path.join(project_dir, "*.md")))
    if not md_files:
        print(f"Error: No .md files found in {project_dir}")
        return False

    # Bibliography
    bib_files = glob.glob(os.path.join(project_dir, "*.bib"))
    win_bib_arg = []
    if bib_files:
        win_bib = linux_to_windows_path(bib_files[0])
        win_bib_arg = ["-bibliography", win_bib]
    template_path = os.path.join(project_dir, "reference.docx")
    if not os.path.exists(template_path):
        # Fallback to default template in gostdown dir if needed, or error
        # Assuming user provides it or we use a default
        # For this logic, let's look for *any* docx as template or fail
        docx_files = glob.glob(os.path.join(project_dir, "*.docx"))
        if docx_files:
            template_path = docx_files[0]
        else:
            print("Error: No reference.docx or template found in project dir.")
            return False

    # Output file
    project_name = os.path.basename(os.path.normpath(project_dir))
    output_docx = os.path.join(output_dir, f"{project_name}.docx")
    output_pdf = os.path.join(output_dir, f"{project_name}.pdf")

    # 2. Translate Paths to Windows
    try:
        win_md_files = [linux_to_windows_path(f) for f in md_files]
        win_template = linux_to_windows_path(template_path)
        win_output_docx = linux_to_windows_path(output_docx)
        win_output_pdf = linux_to_windows_path(output_pdf)
    except ValueError as e:
        print(f"Path Error: {e}")
        return False

    # 3. Construct PowerShell Command
    # joining multiple MD files with comma
    md_arg = ",".join(win_md_files)
    
    ps_command = [
        "powershell.exe",
        "-NonInteractive",
        "-NoProfile",
        "-File", BUILD_SCRIPT_WIN_PATH,
        "-md", md_arg,
        "-template", win_template,
        "-docx", win_output_docx,
        "-pdf", win_output_pdf,
        "-counters"
    ] + win_bib_arg

    if args.mermaid:
        ps_command.append("-mermaid")
    
    if args.embedfonts:
        ps_command.append("-embedfonts")
        
    # Join command for SSH
    # Windows CMD requires double quotes for paths with spaces.
    # We will quote arguments that might contain spaces or special chars.
    quoted_args = []
    
    # Executable usually doesn't need quotes if in PATH, but double quotes are safe in CMD
    quoted_args.append("powershell.exe")
    
    for arg in ps_command[1:]:
        # Escape existing double quotes
        arg_escaped = arg.replace('"', '\\"')
        quoted_args.append(f'"{arg_escaped}"')
    
    remote_cmd_str = " ".join(quoted_args)
    
    ssh_command = [
        "ssh",
        f"{VM_USER}@{VM_HOST}",
        remote_cmd_str
    ]

    print(f"Running build for {project_name}...")
    print(f"Remote command: {remote_cmd_str}")

    # 4. Execute
    result = subprocess.run(ssh_command)
    
    if result.returncode == 0:
        print(f"Success! Output in {output_dir}")
        return True
    else:
        print("Build failed.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Gostdown Runner")
    parser.add_argument("--input-dir", required=True, help="Directory containing project files (.md, reference.docx)")
    parser.add_argument("--output-dir", required=True, help="Directory to save output")
    parser.add_argument("--mermaid", action="store_true", help="Enable mermaid filter")
    parser.add_argument("--embedfonts", action="store_true", help="Embed fonts in DOCX")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    success = run_build(args)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
