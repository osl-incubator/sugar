"""Main application module for the Sugar Terminal User Interface."""

import json

from pathlib import Path
from typing import Any, Dict, TypeVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Rule,
    Static,
)

from sugar.logs import SugarLogs

# Define type variables for App and Screen
A = TypeVar('A', bound=object)
T = TypeVar('T', bound=object)


class SugarTUI(App[A]):
    """Sugar Terminal User Interface application."""

    TITLE = 'Sugar TUI — Container Management Simplified'

    CSS_PATH = Path(__file__).parent / 'styles/styles.css'

    DATA_PATH = Path(__file__).parent / 'data/app.json'

    BINDINGS = [
        Binding('q', 'quit', 'Quit'),
        Binding('p', "push_screen('profiles')", 'Profiles'),
        Binding('s', "push_screen('services')", 'Services'),
        Binding('l', 'logs', 'Logs'),
        Binding('d', 'details', 'Details'),
        Binding('r', 'refresh', 'Refresh'),
        Binding('escape', 'back', 'Back'),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.mock_data = self.load_mock_data()

    def load_mock_data(self) -> Dict[str, Any]:
        """Load mock data from JSON file."""
        try:
            with open(self.DATA_PATH, 'r') as f:
                data: Dict[str, Any] = json.load(f)
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            SugarLogs.print_warning(f'Error loading mock data: {e}')
            return {'profiles': [], 'services': [], 'system_metrics': {}}

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()

        yield Container(
            Vertical(
                Static('SUGAR TERMINAL USER INTERFACE', classes='title'),
                Static('Container Management Dashboard', classes='subtitle'),
                Grid(
                    Vertical(
                        Static('ACTIVE PROFILES', classes='dashboard-header'),
                        self._create_profiles_panel(),
                        classes='dashboard-panel profiles-panel',
                    ),
                    Vertical(
                        Static('RUNNING SERVICES', classes='dashboard-header'),
                        self._create_services_panel(),
                        classes='dashboard-panel services-panel',
                    ),
                    Vertical(
                        Static('SYSTEM METRICS', classes='dashboard-header'),
                        self._create_status_panel(),
                        classes='dashboard-panel metrics-panel',
                    ),
                    Vertical(
                        Static('QUICK ACTIONS', classes='dashboard-header'),
                        self._create_actions_panel(),
                        classes='dashboard-panel actions-panel',
                    ),
                    id='dashboard-grid',
                ),
                id='main-content',
            ),
            id='app-container',
        )

        yield Footer()

    def _create_profiles_panel(self) -> DataTable[Any]:
        """Create the profiles panel for the dashboard."""
        profiles_table: DataTable[Any] = DataTable()
        profiles_table.cursor_type = 'row'
        profiles_table.add_columns('Profile', 'Services', 'Status')

        if self.mock_data.get('profiles'):
            for profile in self.mock_data['profiles']:
                profiles_table.add_row(
                    profile['profile'], profile['services'], profile['status']
                )

        return profiles_table

    def _create_services_panel(self) -> DataTable[Any]:
        """Create the services panel for the dashboard."""
        services_table: DataTable[Any] = DataTable()
        services_table.cursor_type = 'row'
        services_table.add_columns(
            'Service', 'Status', 'Ports', 'CPU', 'Memory'
        )

        if self.mock_data.get('services'):
            for service in self.mock_data['services']:
                services_table.add_row(
                    service['service'],
                    service['status'],
                    service['ports'],
                    service['cpu'],
                    service['memory'],
                )

        return services_table

    def _create_status_panel(self) -> Vertical:
        """Create the system status panel for the dashboard."""
        metrics = self.mock_data.get('system_metrics', {})

        return Vertical(
            Horizontal(
                Label('Active Profiles:', classes='data-label'),
                Label(
                    metrics.get('active_profiles', 'N/A'), classes='data-value'
                ),
            ),
            Horizontal(
                Label('Running Containers:', classes='data-label'),
                Label(
                    metrics.get('running_containers', 'N/A'),
                    classes='data-value',
                ),
            ),
            Rule(),
            Horizontal(
                Label('CPU Usage:', classes='data-label'),
                Label(
                    metrics.get('cpu_usage', 'N/A'),
                    classes='data-value-highlight',
                ),
            ),
            Horizontal(
                Label('Memory Usage:', classes='data-label'),
                Label(
                    metrics.get('memory_usage', 'N/A'),
                    classes='data-value-highlight',
                ),
            ),
            Horizontal(
                Label('Disk Usage:', classes='data-label'),
                Label(metrics.get('disk_usage', 'N/A'), classes='data-value'),
            ),
            Rule(),
            Horizontal(
                Label('Network In:', classes='data-label'),
                Label(
                    metrics.get('network_in', 'N/A'), classes='data-value-blue'
                ),
            ),
            Horizontal(
                Label('Network Out:', classes='data-label'),
                Label(
                    metrics.get('network_out', 'N/A'),
                    classes='data-value-purple',
                ),
            ),
            Rule(),
            Horizontal(
                Label('Uptime:', classes='data-label'),
                Label(metrics.get('uptime', 'N/A'), classes='data-value'),
            ),
            classes='dashboard-data',
        )

    def _create_actions_panel(self) -> Vertical:
        """Create the quick actions panel for the dashboard."""
        return Vertical(
            Button(
                'Start All Services', id='start-all-btn', variant='success'
            ),
            Button('Stop All Services', id='stop-all-btn', variant='error'),
            Button(
                'Restart Services', id='restart-all-btn', variant='warning'
            ),
            Button('View Logs', id='view-logs-btn', variant='primary'),
            Button('Service Details', id='details-btn', variant='default'),
            Button('Run Health Checks', id='health-btn', variant='success'),
            classes='action-buttons',
        )

    def on_mount(self) -> None:
        """Event handler called when app is mounted."""
        try:
            from sugar.tui.screens.details import DetailsScreen
            from sugar.tui.screens.logs import LogsScreen
            from sugar.tui.screens.profiles import ProfileScreen
            from sugar.tui.screens.services import ServiceScreen

            self.install_screen(ProfileScreen(), name='profiles')
            self.install_screen(ServiceScreen(), name='services')
            self.install_screen(LogsScreen(), name='logs')
            self.install_screen(DetailsScreen(), name='details')

            SugarLogs.print_info('Screens installed successfully')
        except ImportError as e:
            SugarLogs.print_warning(f'Error loading screens: {e}')
            self._create_basic_screens()

    def action_refresh(self) -> None:
        """Refresh the dashboard data."""
        self.notify('Refreshing dashboard data...')
        self.mock_data = self.load_mock_data()
        self.app.refresh()

    def action_logs(self) -> None:
        """View logs."""
        self.notify('Viewing logs...')
        try:
            self.push_screen('logs')
        except Exception:
            self.notify('Logs screen not available', severity='error')

    def action_details(self) -> None:
        """View details."""
        self.notify('Viewing details...')
        try:
            self.push_screen('details')
        except Exception:
            self.notify('Details screen not available', severity='error')

    async def action_back(self) -> None:
        """Go back to previous screen."""
        try:
            self.pop_screen()
        except Exception as e:
            pass
            self.log.debug(f'Could not pop screen: {e}')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses on the dashboard."""
        button = event.button
        button_text = button.label if hasattr(button, 'label') else ''
        button_text_str = str(button_text)

        if 'Start' in button_text_str:
            self.notify('Starting all services...', title='Starting')
        elif 'Stop' in button_text_str:
            self.notify('Stopping all services...', title='Stopping')
        elif 'Restart' in button_text_str:
            self.notify('Restarting all services...', title='Restarting')
        elif 'Logs' in button_text_str:
            self.action_logs()
        elif 'Details' in button_text_str:
            self.action_details()
        elif 'Health' in button_text_str:
            self.notify('Running health checks...', title='Health Check')

    def _create_basic_screens(self) -> None:
        """Create basic screen files if they don't exist."""
        from textual.widgets import Static

        class BasicScreen(Screen[T]):
            def compose(self) -> ComposeResult:
                yield Static('Coming soon...', classes='title')

        self.install_screen(BasicScreen(), name='profiles')
        self.install_screen(BasicScreen(), name='services')
        self.install_screen(BasicScreen(), name='logs')
        self.install_screen(BasicScreen(), name='details')

        SugarLogs.print_info('Created and installed basic screens')


def run() -> None:
    """Run the Sugar TUI application."""
    SugarLogs.print_info('Inside run() function')
    app: SugarTUI[object] = SugarTUI()
    app.run()


if __name__ == '__main__':
    run()
