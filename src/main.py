import argparse
import os
import sys
from .config import get_project_config
from .runner import run_build

def main():
    parser = argparse.ArgumentParser(description="Gostdown Automation Builder")
    parser.add_argument("--input-dir", required=True, help="Path to project input directory")
    parser.add_argument("--output-dir", required=True, help="Directory for output files")
    parser.add_argument("--root-dir", default=os.getcwd(), help="Root directory of the repo (for finding templates/scripts)")
    
    # Legacy flags overrides - kept for backward compatibility if user uses them via CLI
    # But Config system is preferred.
    parser.add_argument("--mermaid", action="store_true", help="Override: Enable Mermaid")
    parser.add_argument("--embedfonts", action="store_true", help="Override: Embed fonts")
    
    args = parser.parse_args()
    
    project_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    root_dir = os.path.abspath(args.root_dir)
    
    project_name = os.path.basename(project_dir)
    
    # Load Configuration
    global_config = os.path.join(root_dir, "config.json")
    templates_dir = os.path.join(root_dir, "templates")
    
    config = get_project_config(project_dir, global_config, templates_dir)
    
    # apply cli overrides if present
    if args.mermaid:
        config["mermaid"] = True
    if args.embedfonts:
        config["embedfonts"] = True
        
    # Execute
    success = run_build(project_name, config, output_dir, root_dir)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
