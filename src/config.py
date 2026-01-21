import os
import json
import glob

# Default Configuration
DEFAULT_CONFIG = {
    "template": "reference.docx", 
    "outputs": ["docx", "pdf"],
    "mermaid": False,
    "embedfonts": False,
    "counters": True,
    "bibliography": True,  # Auto-detect boolean
    "markdown_files": [],   # Empty means auto-detect
    "title_file": "title.docx", # Default title file name to look for
    "list_trailing_character": None, # None = inherit template
    "list_number_suffix": None, # None = inherit template
    "heading_alignment": None, # None = inherit template. Can be string or array (["center", "left"])
    "math_font_size": None, # None = default 12.5
    "code_font_size": None # None = default 10.5
}

def load_json_file(path):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to parse config {path}: {e}")
    return {}

def merge_configs(base, override):
    """
    Merges override into base. 
    For lists (like outputs), override replaces base.
    For dicts, it merges keys.
    """
    result = base.copy()
    for key, value in override.items():
        result[key] = value
    return result

def get_project_config(project_dir, global_config_path=None, templates_dir="templates"):
    """
    Resolves the final configuration for a project.
    Hierarchy: Defaults -> Global Config -> Project Local Config
    """
    # 1. Start with Defaults
    config = DEFAULT_CONFIG.copy()

    # 2. Load Global Config
    if global_config_path and os.path.exists(global_config_path):
        global_opts = load_json_file(global_config_path)
        config = merge_configs(config, global_opts)

    # 3. Load Project Config
    local_config_path = os.path.join(project_dir, "config.json")
    if os.path.exists(local_config_path):
        local_opts = load_json_file(local_config_path)
        config = merge_configs(config, local_opts)

    # 4. Resolve Markdown Files
    # If not specified in config, find all .md files in project_dir and sort them
    if not config["markdown_files"]:
        md_files = glob.glob(os.path.join(project_dir, "*.md"))
        # Exclude config files or other non-content if any (though usually .json, .docx are ignored)
        # Sort alphabetically
        md_files.sort()
        config["markdown_files"] = md_files
    else:
        # Resolve relative paths in config to absolute paths
        resolved_mds = []
        for md in config["markdown_files"]:
            if not os.path.isabs(md):
                resolved_mds.append(os.path.join(project_dir, md))
            else:
                resolved_mds.append(md)
        config["markdown_files"] = resolved_mds

    # 5. Resolve Template
    # If it's just a filename, look in templates_dir, then project_dir
    template_val = config["template"]
    if not os.path.isabs(template_val):
        # Check templates dir first (centralized)
        central_template = os.path.join(templates_dir, template_val)
        project_template = os.path.join(project_dir, template_val)
        
        if os.path.exists(central_template):
            config["template_path"] = central_template
        elif os.path.exists(project_template):
            config["template_path"] = project_template
        else:
            # Fallback to default or error? 
            # Let's keep the value for now, might be resolved later or error out.
            config["template_path"] = project_template # Default behavior
    else:
        config["template_path"] = template_val

    # 6. Resolve Output Paths (Default to output/ProjectName)
    # This might be handled by the runner, but we can pre-calc here if needed.
    # For now, we rely on Main logic to pass output dir.
    
    # 7. Auto-detect bibliography if enabled and not specified string
    if config.get("bibliography") is True:
        bib_files = glob.glob(os.path.join(project_dir, "*.bib"))
        if bib_files:
            config["bibliography_path"] = bib_files[0]
        else:
            config["bibliography_path"] = None
    elif isinstance(config.get("bibliography"), str):
         bib_path = config["bibliography"]
         if not os.path.isabs(bib_path):
             config["bibliography_path"] = os.path.join(project_dir, bib_path)
         else:
             config["bibliography_path"] = bib_path
    else:
        config["bibliography_path"] = None

    return config
