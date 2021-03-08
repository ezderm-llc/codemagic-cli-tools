#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import List
from typing import NamedTuple

from mdutils.mdutils import MdUtils
from mdutils.tools.Table import Table

sys.path.insert(0, os.path.abspath('./src'))

from codemagic import cli
from codemagic import tools


class SerializedArgument(NamedTuple):
    key: str
    description: str
    flags: str
    name: str
    required: bool
    default: str
    nargs: bool
    choices: str


class Action(NamedTuple):
    action_name: str
    name: str
    description: str
    required_args: List[SerializedArgument]
    optional_args: List[SerializedArgument]


class ArgumentKwargs(NamedTuple):
    nargs: bool
    required: bool
    default: str
    choices: str


class ArgumentsSerializer:
    def __init__(self, raw_arguments):
        self.raw_arguments = raw_arguments
        self.required_args: List[SerializedArgument]
        self.optional_args: List[SerializedArgument]

    def serialize(self) -> ArgumentsSerializer:
        def _serialize(arg) -> SerializedArgument:
            description = str_plain(arg._value_.description)
            arg_type = getattr(arg._value_, 'type')
            if isinstance(arg_type, type) and issubclass(arg_type, cli.argument.EnvironmentArgumentValue):
                description = str_plain(arg.get_description())
                env_var = arg_type.__dict__.get('environment_variable_key')
                if env_var:
                    description = re.sub(f'({env_var}| {arg._name_} )', r'`\1`', description).replace('"', '`')

            kwargs = self._proccess_kwargs(getattr(arg._value_, 'argparse_kwargs'))
            return SerializedArgument(
                key=arg._value_.key,
                description=description,
                flags=', '.join(getattr(arg._value_, 'flags', '')),
                name='' if arg_type and arg_type.__name__ == 'bool' else arg._name_,
                required=kwargs.required,
                default=kwargs.default,
                nargs=kwargs.nargs,
                choices=kwargs.choices,
            )

        args = list(map(_serialize, self.raw_arguments))
        self.required_args = [arg for arg in args if arg.required]
        self.optional_args = [arg for arg in args if not arg.required]
        return self

    @classmethod
    def _proccess_kwargs(cls, kwargs):
        def _process_choice(choices):
            return ' | '.join([str(c) for c in choices] if choices else '')

        def _process_default(default):
            if not default:
                return ''
            if isinstance(default, tuple) and len(default) > 1 and isinstance(default[0], Path):
                default = ', '.join(str(p).replace(str(Path.home()), '$HOME') for p in default)
            if isinstance(default, tuple) and isinstance(default[0], Path):
                default = default[0]
            if isinstance(default, Path):
                default = str(default).replace(str(Path.home()), '$HOME')
            return str(default)

        kwargs = kwargs or {}
        return ArgumentKwargs(
            nargs=kwargs.get('nargs', '') == '+',
            required=kwargs.get('required', True),
            default=_process_default(kwargs.get('default', '')),
            choices=_process_choice(kwargs.get('choices')),
        )


# docs/README.md
class MainPageDocumentationGenerator:
    def __init__(self, title: str, main_dir: str):
        self.title = title
        self.main_dir = main_dir

    def generate(self, tools: List[cli.CliApp]):
        os.makedirs(self.main_dir, exist_ok=True)
        md = MdUtils(file_name=f'{self.main_dir}/README', title=self.title)
        Writer(md).write_tools_table(tools)
        md.create_md_file()


class ToolDocumentationGenerator:
    def __init__(self, tool, main_dir: str):
        class_args_serializer = ArgumentsSerializer(tool.CLASS_ARGUMENTS).serialize()

        self.tool = tool
        self.tool_command = tool.get_executable_name()
        self.tool_prefix = f'{main_dir}/{self.tool_command}'
        self.tool_optional_args = class_args_serializer.optional_args
        self.tool_required_args = class_args_serializer.required_args
        self.tool_options = self._serialize_default_options(self.tool)
        self.tool_serialized_actions = self._serialize_actions(self.tool)

    def generate(self):
        def _write_tool_command_arguments_and_options():
            writer.write_arguments(f'command `{self.tool_command}`', self.tool_optional_args, self.tool_required_args)
            writer.write_options(self.tool_options)

        # docs/<tool-name>/README.md
        os.makedirs(self.tool_prefix, exist_ok=True)
        md = MdUtils(file_name=f'{self.tool_prefix}/README', title=self.tool_command)
        writer = Writer(md)
        writer.write_description(self.tool.__doc__)
        writer.write_tool_command_usage(self)
        _write_tool_command_arguments_and_options()
        writer.write_actions_table(self.tool_serialized_actions)
        md.create_md_file()

        for action in self.tool_serialized_actions:
            # docs/<tool-name>/<action-name>.md
            md = MdUtils(file_name=f'{self.tool_prefix}/{action.action_name}', title=action.action_name)
            writer = Writer(md)
            writer.write_description(action.description)
            writer.write_action_command_usage(self, action)
            writer.write_arguments(f'action `{action.action_name}`', action.optional_args, action.required_args)
            _write_tool_command_arguments_and_options()
            md.create_md_file()

    @classmethod
    def _serialize_actions(cls, tool: cli.CliApp) -> List[Action]:
        def _serialize_action(action: Callable) -> Action:
            action_args_serializer = ArgumentsSerializer(action.arguments).serialize()
            return Action(
                action_name=action.action_name,
                name=action.__name__,
                description=action.__doc__,
                required_args=action_args_serializer.required_args,
                optional_args=action_args_serializer.optional_args,
            )

        return list(map(_serialize_action, tool.get_class_cli_actions()))

    @classmethod
    def _serialize_default_options(cls, tool: cli.CliApp) -> List[SerializedArgument]:
        def _serialize_option(option) -> SerializedArgument:
            return SerializedArgument(
                key='',
                description=str_plain(str(option.help)).replace('[', '').replace(': ', ' `').replace(']', '`'),
                flags=', '.join(option.option_strings),
                name='',
                required=False,
                default='',
                nargs=False,
                choices=' | '.join(option.choices) if option.choices else '',
            )

        parser = argparse.ArgumentParser(
            description=tool.__doc__,
            formatter_class=cli.cli_help_formatter.CliHelpFormatter,
        )
        tool.get_default_cli_options(parser)
        return list(map(_serialize_option, parser._actions))


class CommandUsageGenerator:
    def __init__(self, doc_generator: ToolDocumentationGenerator):
        self.doc_generator = doc_generator

    def get_tool_command_usage(self) -> List[str]:
        return [
            f'{self.doc_generator.tool_command} {self._get_opt_common_flags()}',
            *self._get_tool_arguments_and_flags(),
            'ACTION',
        ]

    def get_action_command_usage(self, action: Action) -> List[str]:
        return [
            f'{self.doc_generator.tool_command} {action.action_name} {self._get_opt_common_flags()}',
            *self._get_tool_arguments_and_flags(),
            *map(self._get_formatted_flag, action.optional_args),
            *map(self._get_formatted_flag, action.required_args),
        ]

    def _get_opt_common_flags(self) -> str:
        return ' '.join(map(self._get_formatted_flag, self.doc_generator.tool_options))

    def _get_tool_arguments_and_flags(self) -> Iterable[str]:
        return map(
            self._get_formatted_flag,
            [*self.doc_generator.tool_required_args, *self.doc_generator.tool_optional_args],
        )

    @classmethod
    def _get_formatted_flag(cls, arg: SerializedArgument) -> str:
        flag = f'{arg.flags.split(",")[0]}'
        if not arg.flags and arg.name:
            flag = arg.name
        elif arg.choices and not arg.name:
            flag = f'{flag} STREAM'
        elif arg.name:
            flag = f'{flag} {arg.name}'
        return flag if arg.required else f'[{flag}]'


class Writer:
    def __init__(self, file: MdUtils):
        self.file = file

    def write_description(self, content: str):
        content = str_plain(content)
        self.file.new_paragraph(f'**{content}**')

    def write_tool_command_usage(self, generator: ToolDocumentationGenerator):
        self._write_command_usage(self.file, CommandUsageGenerator(generator).get_tool_command_usage())

    def write_action_command_usage(self, generator: ToolDocumentationGenerator, action: Action):
        self._write_command_usage(self.file, CommandUsageGenerator(generator).get_action_command_usage(action))

    def write_table(self, content: List[List[str]], header: List[str]):
        flat_content: List[str] = sum(content, [])
        table = Table().create_table(
            columns=len(header),
            rows=len(content) + 1,
            text=header + flat_content,
            text_align='left',
        )
        self.file.write(table)

    def write_tools_table(self, tools: List[cli.CliApp]):
        def _get_tool_link(tool: cli.CliApp) -> str:
            return f'[`{tool.get_executable_name()}`]({tool.get_executable_name()}/README.md)'

        def _get_tool_doc(tool: cli.CliApp) -> List[str]:
            return [_get_tool_link(tool), str_plain(tool.__doc__)]

        self.write_table(list(map(_get_tool_doc, tools)), ['Tool name', 'Description'])

    def write_actions_table(self, actions: List[Action]):
        def _get_action_doc(action: Action) -> List[str]:
            return [f'[`{action.action_name}`]({action.action_name}.md)', str_plain(action.description)]

        self.file.new_header(level=3, title='Actions', add_table_of_contents='n')
        self.write_table(list(map(_get_action_doc, actions)), ['Action', 'Description'])

    def write_arguments(self, obj: str, optional: List[SerializedArgument], required: List[SerializedArgument]):
        self._write_arguments(self.file, f'Required arguments for {obj}', required)
        self._write_arguments(self.file, f'Optional arguments for {obj}', optional)

    def write_options(self, options: List[SerializedArgument]):
        self._write_arguments(self.file, 'Common options', options)

    @classmethod
    def _write_command_usage(cls, file: MdUtils, lines: List[str]):
        file.new_header(level=3, title='Usage', add_table_of_contents='n')
        main_lines = ''.join([f'    {line}\n' for line in lines[1:]])
        file.write(f'```bash\n{lines[0]}\n{main_lines}```')

    @classmethod
    def _write_arguments(cls, file: MdUtils, title: str, args: List[SerializedArgument]):
        def _process_flag(arg: SerializedArgument) -> str:
            flag = arg.flags
            if flag and arg.choices:
                return f'{flag}={arg.choices}'
            if flag and arg.name:
                return f'{flag}={arg.name}'
            return arg.name if arg.name else flag

        def _process_description(arg: SerializedArgument) -> str:
            description = arg.description.replace('*', r'\*')
            description += '. Multiple arguments' if arg.nargs else ''
            return f'{description}. Default:&nbsp;`{arg.default}`' if arg.default else description

        if not args:
            return

        file.new_header(level=3, title=title, add_table_of_contents='n')
        for arg in args:
            description = _process_description(arg).replace('..', '.')
            file.new_header(level=5, title=f'`{_process_flag(arg)}`', add_table_of_contents='n')
            file.new_paragraph(description)


def str_plain(string: str) -> str:
    return re.compile(r'(\x1b\[\d*m|\x1b\[\d*m|\t)').sub('', string).replace('\n', ' ').strip()


def main():
    print(f'Generate documentation for module {tools.__name__} from {tools.__file__}')
    main_dir = 'docs'
    tool_classes = cli.CliApp.__subclasses__()
    MainPageDocumentationGenerator('CLI tools', main_dir).generate(tool_classes)
    for tool_class in tool_classes:
        print(f'Generate documentation for tool {tool_class.get_executable_name()}')
        ToolDocumentationGenerator(tool_class, main_dir).generate()


if __name__ == '__main__':
    main()
