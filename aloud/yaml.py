from ruamel.yaml import YAML


def str_representer(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        style = '|'
    else:
        style = None
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)


yaml = YAML(typ='unsafe', pure=True)
yaml.default_flow_style = False
yaml.preserve_quotes = True
yaml.representer.add_representer(str, str_representer)
