"""Details screen for displaying container and service information."""

from typing import Any, TypeVar

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Static,
)

# Define type variable for Screen
T = TypeVar('T')


class DetailsScreen(Screen[T]):
    """Screen to display service details."""

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Back'),
        ('r', 'refresh', 'Refresh'),
        ('l', "app.push_screen('logs')", 'Logs'),
    ]

    def compose(self) -> ComposeResult:
        """Compose the details screen."""
        yield Header()

        yield Container(
            Vertical(
                Static('SERVICE DETAILS', classes='title'),
                Horizontal(
                    Static(
                        'Container and configuration information',
                        classes='subtitle',
                    ),
                    Static(id='service-name', classes='subtitle-highlight'),
                    id='screen-header',
                ),
                Grid(
                    # Configuration panel
                    Vertical(
                        Static('CONFIGURATION', classes='section-title'),
                        self._create_config_panel(),
                        classes='detail-panel',
                    ),
                    # Status panel
                    Vertical(
                        Static('STATISTICS', classes='section-title'),
                        self._create_stats_panel(),
                        classes='detail-panel',
                    ),
                    # Volumes panel
                    Vertical(
                        Static('VOLUMES', classes='section-title'),
                        self._create_volumes_panel(),
                        classes='detail-panel',
                    ),
                    # Network panel
                    Vertical(
                        Static('NETWORKS', classes='section-title'),
                        self._create_network_panel(),
                        classes='detail-panel',
                    ),
                    id='details-grid',
                ),
                Horizontal(
                    Button('View Logs', id='logs-btn', variant='primary'),
                    Button('Restart', id='restart-btn', variant='warning'),
                    Button('Stop', id='stop-btn', variant='error'),
                    Button('Back', id='back-btn', variant='default'),
                    id='details-actions',
                ),
                id='screen-content',
            ),
            id='screen-container',
        )

        yield Footer()

    def _create_config_panel(self) -> Vertical:
        """Create the configuration panel."""
        return Vertical(
            Horizontal(
                Label('Image:', classes='detail-label'),
                Label('nginx:latest', classes='detail-value', id='image-name'),
            ),
            Horizontal(
                Label('Container ID:', classes='detail-label'),
                Label(
                    'abc123def456', classes='detail-value', id='container-id'
                ),
            ),
            Horizontal(
                Label('Created:', classes='detail-label'),
                Label(
                    '2024-03-07 08:42:15',
                    classes='detail-value',
                    id='created-at',
                ),
            ),
            Horizontal(
                Label('Status:', classes='detail-label'),
                Label('● Running', classes='detail-value', id='status'),
            ),
            Horizontal(
                Label('Ports:', classes='detail-label'),
                Label('8080:80, 443:443', classes='detail-value', id='ports'),
            ),
            Horizontal(
                Label('Env Vars:', classes='detail-label'),
                Label(
                    'NGINX_HOST=example.com, PORT=80',
                    classes='detail-value',
                    id='env-vars',
                ),
            ),
            id='config-details',
        )

    def _create_stats_panel(self) -> Vertical:
        """Create the stats panel."""
        return Vertical(
            Horizontal(
                Label('CPU Usage:', classes='detail-label'),
                Label('2.5%', classes='detail-value', id='cpu-usage'),
            ),
            Horizontal(
                Label('Memory:', classes='detail-label'),
                Label(
                    '128MB / 512MB', classes='detail-value', id='memory-usage'
                ),
            ),
            Horizontal(
                Label('Network In:', classes='detail-label'),
                Label('1.2MB/s', classes='detail-value', id='network-in'),
            ),
            Horizontal(
                Label('Network Out:', classes='detail-label'),
                Label('0.8MB/s', classes='detail-value', id='network-out'),
            ),
            Horizontal(
                Label('Uptime:', classes='detail-label'),
                Label('2d 3h 45m', classes='detail-value', id='uptime'),
            ),
            Horizontal(
                Label('Restarts:', classes='detail-label'),
                Label('0', classes='detail-value', id='restarts'),
            ),
            id='stats-details',
        )

    def _create_volumes_panel(self) -> DataTable[Any]:
        """Create the volumes panel."""
        volumes_table: DataTable[Any] = DataTable(id='volumes-table')
        volumes_table.cursor_type = 'row'
        volumes_table.add_columns('Source', 'Destination', 'Mode')

        # Add mock data
        volumes_table.add_rows(
            [
                ('/data', '/var/www/html', 'rw'),
                ('nginx_logs', '/var/log/nginx', 'rw'),
                ('nginx_conf', '/etc/nginx/conf.d', 'ro'),
            ]
        )

        return volumes_table

    def _create_network_panel(self) -> DataTable[Any]:
        """Create the network panel."""
        network_table: DataTable[Any] = DataTable(id='network-table')
        network_table.cursor_type = 'row'
        network_table.add_columns('Network', 'IP Address', 'Gateway')

        # Add mock data
        network_table.add_rows(
            [
                ('bridge', '172.17.0.2', '172.17.0.1'),
                ('host', '127.0.0.1', '-'),
            ]
        )

        return network_table

    def on_mount(self) -> None:
        """Handle mounting of the screen."""
        self.query_one('#service-name', Static).update('nginx')
        self.notify('Details screen loaded')

    def action_refresh(self) -> None:
        """Refresh the details data."""
        self.notify('Refreshing service details...')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == 'logs-btn':
            self.app.push_screen('logs')
        elif button_id == 'restart-btn':
            self.notify('Restarting service...', title='Restarting')
        elif button_id == 'stop-btn':
            self.notify('Stopping service...', title='Stopping')
        elif button_id == 'back-btn':
            self.app.pop_screen()
