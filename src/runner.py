import os
import subprocess
from .utils import linux_to_windows_path

# TODO: Move this to global config or environment variable?
# For now, hardcoded as it was in the original script
BUILD_SCRIPT_REL_PATH = "gostdown/build.ps1"
SSH_HOST = "vaivanov@192.168.122.2"

def run_build(project_name, project_config, output_dir, root_dir):
    """
    Constructs and executes the SSH command to run the PowerShell build script.
    """
    
    # Paths
    build_script_path = os.path.join(root_dir, BUILD_SCRIPT_REL_PATH)
    win_build_script = linux_to_windows_path(build_script_path)
    
    # Inputs
    md_files = project_config["markdown_files"]
    if not md_files:
        print(f"Skipping {project_name}: No markdown files found.")
        return False
        
    win_md_args = [linux_to_windows_path(md) for md in md_files]
    win_md_str = ",".join(win_md_args)
    
    win_template = linux_to_windows_path(project_config["template_path"])
    
    # Outputs
    # Check outputs config
    outputs = project_config.get("outputs", [])
    
    win_args = []
    
    # DOCX Output
    if "docx" in outputs:
        docx_path = os.path.join(output_dir, f"{project_name}.docx")
        win_docx = linux_to_windows_path(docx_path)
        win_args.extend(["-docx", win_docx])
        
    # PDF Output
    if "pdf" in outputs:
        pdf_path = os.path.join(output_dir, f"{project_name}.pdf")
        win_pdf = linux_to_windows_path(pdf_path)
        win_args.extend(["-pdf", win_pdf])
        
    # Flags checking
    if project_config.get("mermaid"):
        win_args.append("-mermaid")
        
    if project_config.get("embedfonts"):
        win_args.append("-embedfonts")
        
    if project_config.get("counters"):
        win_args.append("-counters")
        
    # Bibliography
    bib_path = project_config.get("bibliography_path")
    if bib_path:
        win_bib = linux_to_windows_path(bib_path)
        win_args.extend(["-bibliography", win_bib])

    # List Formatting
    if project_config.get("list_trailing_character"):
        win_args.extend(["-listTrailingCharacter", project_config["list_trailing_character"]])
        
    if project_config.get("list_number_suffix") is not None:
         win_args.extend(["-listNumberSuffix", project_config["list_number_suffix"]])

    if project_config.get("heading_alignment"):
         win_args.extend(["-headingAlignment", project_config["heading_alignment"]])

    # Construct PowerShell Command
    ps_command = [
        "powershell.exe",
        "-NonInteractive",
        "-NoProfile",
        "-File", win_build_script,
        "-md", win_md_str,
        "-template", win_template
    ] + win_args
    
    # Construct SSH Command with quoting
    quoted_args = []
    quoted_args.append(ps_command[0]) # powershell.exe
    
    for arg in ps_command[1:]:
        # Escape quotes if necessary, though paths shouldn't have them usually
        # But for arguments like comma separated list, we should be careful.
        # Simple wrapping in double quotes usually works for cmd->powershell.
        arg_escaped = arg.replace('"', '\\"') 
        quoted_args.append(f'"{arg_escaped}"')
        
    remote_cmd_str = " ".join(quoted_args)
    
    print(f"Running build for {project_name}...")
    print(f"Remote command: {remote_cmd_str}")
    
    ssh_cmd = ["ssh", SSH_HOST, remote_cmd_str]
    
    try:
        subprocess.check_call(ssh_cmd)
        print(f"Success! Output in {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code {e.returncode}")
        return False
