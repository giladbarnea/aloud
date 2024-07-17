from ruamel.yaml import YAML


def str_representer(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        style = '|'
    else:
        style = None
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)


yaml = YAML(typ='safe', pure=True)
yaml.default_flow_style = False
yaml.indent = 4
yaml.preserve_quotes = True
yaml.representer.add_representer(str, str_representer)
yaml.sequence_dash_offset = 2
yaml.sort_base_mapping_type_on_output = True
yaml.sort_keys = True
yaml.width = 999
