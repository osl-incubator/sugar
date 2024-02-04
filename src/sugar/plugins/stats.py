"""Sugar Plugin for Containers Statics."""
from __future__ import annotations

import datetime
import io

from itertools import tee
from typing import Iterable

import plotille

from rich.text import Text
from textual.app import App, ComposeResult
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Header

from sugar.console import get_terminal_size
from sugar.inspect import get_container_name, get_container_stats
from sugar.logs import KxgrErrorType, KxgrLogs
from sugar.plugins.base import SugarDockerCompose

CHART_WINDOW_DURATION = 60
CHART_TIME_INTERVAL = 1


class StatsPlot:
    """Plot containers statistic data."""

    def __init__(
        self,
        container_names: list[str],
        window_duration: int = CHART_WINDOW_DURATION,
        interval: int = CHART_TIME_INTERVAL,
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

        self.create_chart()
        self.reset_data()

    def create_chart(self):
        """Create a new chart."""
        self.fig_mem = plotille.Figure()
        self.fig_cpu = plotille.Figure()

        self.resize_chart()

        self.chart_colors: tuple[Iterable, Iterable] = {
            'mem': tee(self.fig_mem._color_seq),
            'cpu': tee(self.fig_cpu._color_seq),
        }

        self.stats: dict[str, dict[str, list[str]]] = {
            name: {'times': [], 'mem_usages': [], 'cpu_usages': []}
            for name in self.container_names
        }

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

    def resize_chart(self):
        """Resize chart."""
        console_width, console_height = get_terminal_size()

        chart_height = min((console_height - 20) // 2, 10)
        chart_width = console_width - 30

        self.fig_mem.width = chart_width
        self.fig_mem.height = chart_height
        self.fig_cpu.width = chart_width
        self.fig_cpu.height = chart_height

    def reset_chart(self):
        """Reset chart state."""
        self.fig_mem._plots.clear()
        self.fig_cpu._plots.clear()

        self.fig_mem._color_seq = tee(self.chart_colors['mem'][0])[1]
        self.fig_cpu._color_seq = tee(self.chart_colors['cpu'][0])[1]

        self.resize_chart()

    def reset_data(self):
        """Generate a clean data."""
        current_time = datetime.datetime.now()

        for name in self.container_names:
            container_stats = self.stats[name]

            container_stats['mem_usages'].clear()
            container_stats['cpu_usages'].clear()
            container_stats['times'].clear()

            container_stats['mem_usages'].extend([0.0] * CHART_WINDOW_DURATION)
            container_stats['cpu_usages'].extend([0.0] * CHART_WINDOW_DURATION)
            container_stats['times'].extend(
                [
                    current_time
                    - datetime.timedelta(seconds=i * CHART_TIME_INTERVAL)
                    for i in range(CHART_WINDOW_DURATION)
                ][::-1]
            )

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

    def plot_stats(self):
        """
        Plot containers statistic.

        Plots the memory and CPU usage of multiple Docker containers over
        time in a single chart for each metric.
        """
        current_time = datetime.datetime.now()

        for name in self.container_names:
            mem_usage, cpu_usage = get_container_stats(name)

            # Update and maintain window for stats
            container_stats = self.stats[name]
            container_stats['times'].append(current_time)
            container_stats['mem_usages'].append(round(mem_usage, 2))
            container_stats['cpu_usages'].append(round(cpu_usage, 2))

            container_stats['times'] = container_stats['times'][
                -self.window_duration :
            ]
            container_stats['mem_usages'] = container_stats['mem_usages'][
                -self.window_duration :
            ]
            container_stats['cpu_usages'] = container_stats['cpu_usages'][
                -self.window_duration :
            ]

        self.reset_chart()

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
        interval_time = CHART_TIME_INTERVAL
        self.set_interval(
            interval_time, self.update_plot
        )  # Update every second
        self.stats_plot = StatsPlot(
            container_names=self.container_names,
            window_duration=CHART_WINDOW_DURATION,
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

    TITLE = 'Sugar Containers Stats'
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
