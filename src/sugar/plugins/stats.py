"""Sugar Plugin for Containers Statics."""
from __future__ import annotations

import io
import re
import subprocess  # nosec B404
import time

import plotille

from rich.text import Text
from textual.app import App, ComposeResult
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Header

from sugar.inspect import get_container_name
from sugar.logs import KxgrErrorType, KxgrLogs
from sugar.plugins.base import SugarDockerCompose


def get_container_stats(container_name: str) -> tuple[float, float]:
    """
    Fetch the current memory and CPU usage of a given Docker container.

    Parameters
    ----------
        container_name (str): Name of the Docker container.

    Returns
    -------
    tuple:
        The current memory usage of the container in MB and CPU usage as
        a percentage.
    """
    command = (
        f'docker stats {container_name} --no-stream --format '
        f"'{{{{.MemUsage}}}} {{{{.CPUPerc}}}}'"
    )
    result = subprocess.run(  # nosec B602, B603
        command, capture_output=True, text=True, shell=True, check=False
    )
    output = result.stdout.strip().split()
    mem_usage_str = output[0].split('/')[0].strip()
    cpu_usage_str = output[-1].strip('%')

    mem_usage = float(re.sub(r'[^\d.]', '', mem_usage_str))
    cpu_usage = float(cpu_usage_str)

    return mem_usage, cpu_usage


class StatsPlot:
    """Plot containers statistic data."""

    def __init__(
        self,
        container_names: list[str],
        window_duration: int = 60,
        interval: int = 1,
    ):
        """
        Initialize StatsPlot.

        Parameters
        ----------
        container_names: list
            Names of the Docker containers.
        window_duration: int
            Duration of the window frame for the data in seconds.
        interval: int
            Interval between data points, in seconds.
        """
        self.container_names = container_names
        self.window_duration = window_duration
        self.interval = interval
        self.start_time = time.time()

        self.fig_mem = plotille.Figure()
        self.fig_cpu = plotille.Figure()

        self.stats: dict[str, dict[str, list[str]]] = {
            name: {'times': [], 'mem_usages': [], 'cpu_usages': []}
            for name in container_names
        }

    def plot_stats(self):
        """
        Plot containers statistic.

        Plots the memory and CPU usage of multiple Docker containers over
        time in a single chart for each metric.
        """
        self.fig_mem = plotille.Figure()
        self.fig_mem.width = 50
        self.fig_mem.height = 5
        self.fig_cpu = plotille.Figure()
        self.fig_cpu.width = 50
        self.fig_cpu.height = 5

        current_time = time.time() - self.start_time

        for name in self.container_names:
            mem_usage, cpu_usage = get_container_stats(name)

            # Update and maintain window for stats
            container_stats = self.stats[name]
            container_stats['times'].append(round(current_time, 2))
            container_stats['mem_usages'].append(round(mem_usage, 2))
            container_stats['cpu_usages'].append(round(cpu_usage, 2))

            if len(container_stats['times']) > self.window_duration:
                container_stats['times'] = container_stats['times'][
                    -self.window_duration :
                ]
                container_stats['mem_usages'] = container_stats['mem_usages'][
                    -self.window_duration :
                ]
                container_stats['cpu_usages'] = container_stats['cpu_usages'][
                    -self.window_duration :
                ]

        for name in self.container_names:
            container_stats = self.stats[name]
            # Add data to plots
            self.fig_mem.plot(
                container_stats['times'],
                container_stats['mem_usages'],
                label=name,
            )
            self.fig_cpu.plot(
                container_stats['times'],
                container_stats['cpu_usages'],
                label=name,
            )


class StatsPlotWidget(Widget):
    """Plot Docker Stats Widget."""

    content: Reactive[str] = Reactive('')

    DEFAULT_CSS = """
        Plot {
            width: 100%;
            height: 100%;
        }
    """

    def __init__(self, container_names: list[str], *args, **kwargs) -> None:
        """Initialize StatsPlotWidget."""
        self.container_names = container_names
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        """Set up the widget."""
        # Set up a periodic update, adjust the interval as needed
        interval_time = 1
        self.set_interval(
            interval_time, self.update_plot
        )  # Update every second
        self.stats_plot = StatsPlot(
            container_names=self.container_names,
            window_duration=60,
            interval=interval_time,
        )

    async def update_plot(self) -> None:
        """Update plot data."""
        self.stats_plot.plot_stats()
        self.content = (
            'Memory Usage (MB):\n'
            + self.stats_plot.fig_mem.show(legend=False)
            + '\n\nCPU Usage (%):\n'
            + self.stats_plot.fig_cpu.show(legend=True)
        )

    def render(self) -> Text:
        """Render the widget."""
        return Text.from_ansi(self.content)


class StatsPlotApp(App[str]):
    """StatsPlotApp app class."""

    TITLE = 'Containers Stats'
    container_names: list[str]

    def __init__(self, container_names: list[str], *args, **kwargs) -> None:
        """Initialize StatsPlotApp."""
        self.container_names = container_names
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Compose the app."""
        yield Header()
        yield StatsPlotWidget(self.container_names)


class SugarStats(SugarDockerCompose):
    """SugarStats provides special commands not available on docker-compose."""

    def __init__(self, *args, **kwargs):
        """Initialize the SugarExt class."""
        self.actions += [
            'plot',
        ]

        super().__init__(*args, **kwargs)

    def _plot(self):
        """Call the plot command."""
        _out = io.StringIO()
        _err = io.StringIO()

        self._call_compose_app_core(
            'ps',
            services=self.service_names,
            options_args=['-q'],
            _out=_out,
            _err=_err,
        )

        raw_out = _out.getvalue()

        if not raw_out:
            service_names = ', '.join(self.service_names)
            KxgrLogs.raise_error(
                f'No container found for the services: {service_names}',
                KxgrErrorType.KXGR_NO_SERVICES_RUNNING,
            )

        containers_ids = [cids for cids in raw_out.split('\n') if cids]

        containers_names = [get_container_name(cid) for cid in containers_ids]
        app = StatsPlotApp(containers_names)
        app.run()
