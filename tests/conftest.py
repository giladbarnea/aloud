import pytest
import rich.box
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo
from rich.panel import Panel
from rich.traceback import Traceback

from aloud.console import console


def pytest_runtest_makereport(item: Item, call: CallInfo) -> TestReport | None:
    test_failed: bool = call.when == 'call' and call.excinfo is not None
    if not test_failed:
        return
    print_rich_traceback(call.excinfo.value)


def pytest_runtest_call(item: Item):
    file, line_numer, test_name = item.location
    console.print(
        Panel(
            f'[cyan][bold]Running:[/cyan] {test_name}[/]',
            box=rich.box.MINIMAL,
            subtitle=f'[dim]{file}:{line_numer}[/]',
            subtitle_align='right',
        ),
    )


def pytest_runtest_teardown(item: Item):
    file, line_numer, test_name = item.location
    console.print(
        Panel(
            f'[bold]Teardown: {test_name}[/]',
            box=rich.box.MINIMAL,
            subtitle=f'[dim]{file}:{line_numer}[/]',
            subtitle_align='right',
        ),
    )


def pytest_report_teststatus(report: TestReport, config):
    test_title = f'{report.location[0]} {report.head_line}'
    if report.when == 'call':
        if report.passed:
            return 'passed', f'\n✔ {test_title}', '✔ PASSED'
        if report.failed:
            return 'failed', f'\n✘ {test_title}', '✘ FAILED'
        if report.skipped:
            return 'skipped', f'\n⚠ {test_title}', '⚠ SKIPPED'
    return None


@pytest.fixture(scope='function')
def current_test_name(request):
    return request.node.name.replace('[', '_').replace(']', '_')


def print_rich_traceback(
    exception: BaseException,
    *args,
    extra_lines=10,
    show_locals=True,
    locals_max_string=1000,
    locals_max_length=1000,
    width=console.width,
    suppress=('.venv',),
    console=console,
):
    traceback = Traceback.from_exception(
        type(exception),
        exception,
        traceback=exception.__traceback__,
        extra_lines=extra_lines,
        show_locals=show_locals,
        locals_max_string=locals_max_string,
        locals_max_length=locals_max_length,
        suppress=suppress,
        width=width,
    )

    console.print(traceback, *args)
