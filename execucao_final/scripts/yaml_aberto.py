"""Consistent, non-mutating YAML parsing for OpenAPI documents."""
import yaml
import re

class StringMappingKeys:
    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            seen = set()
            for key_node, _ in node.value:
                if key_node.tag == 'tag:yaml.org,2002:merge':
                    continue
                if not isinstance(key_node, yaml.ScalarNode):
                    raise yaml.constructor.ConstructorError(None, None, 'chave YAML nao escalar', key_node.start_mark)
                if key_node.value in seen:
                    raise yaml.constructor.ConstructorError(None, None, 'chave YAML duplicada: '+key_node.value, key_node.start_mark)
                seen.add(key_node.value)
            self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            if not isinstance(key_node, yaml.ScalarNode):
                raise yaml.constructor.ConstructorError(None, None, 'chave YAML nao escalar', key_node.start_mark)
            key = key_node.value
            result[key] = self.construct_object(value_node, deep=deep)
        return result

class OpenAPICLoader(StringMappingKeys, yaml.CSafeLoader):
    pass

class OpenAPILoader(StringMappingKeys, yaml.SafeLoader):
    pass

_BLOCKED = {'tag:yaml.org,2002:timestamp', 'tag:yaml.org,2002:value', 'tag:yaml.org,2002:bool', 'tag:yaml.org,2002:int', 'tag:yaml.org,2002:float'}
for loader in (OpenAPICLoader, OpenAPILoader):
    loader.yaml_implicit_resolvers = {
        key: [(tag, pattern) for tag, pattern in rules if tag not in _BLOCKED]
        for key, rules in loader.yaml_implicit_resolvers.items()
    }
    loader.add_implicit_resolver('tag:yaml.org,2002:bool', re.compile(r'^(?:true|false)$', re.I), list('tTfF'))
    loader.add_implicit_resolver('tag:yaml.org,2002:int', re.compile(r'^-?(?:0|[1-9][0-9]*)$'), list('-0123456789'))
    loader.add_implicit_resolver('tag:yaml.org,2002:float', re.compile(r'^-?(?:0|[1-9][0-9]*)(?:(?:\.[0-9]+)(?:[eE][-+]?[0-9]+)?|[eE][-+]?[0-9]+)$'), list('-0123456789'))

def load_document(raw):
    try:
        return yaml.load(raw, Loader=OpenAPICLoader), 'OpenAPICLoader'
    except yaml.YAMLError:
        return yaml.load(raw, Loader=OpenAPILoader), 'OpenAPILoader'
