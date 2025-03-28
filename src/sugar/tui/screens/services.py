"""Services management screen for interacting with running containers."""

from pathlib import Path
from typing import Any, TypeVar

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
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

T = TypeVar('T')


class ServiceScreen(Screen[T]):
    """Screen to display and manage services."""

    CSS_PATH = Path(__file__).parent.parent / 'styles/screens.css'

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Back'),
        ('l', "app.push_screen('logs')", 'Logs'),
        ('d', "app.push_screen('details')", 'Details'),
        ('r', 'refresh', 'Refresh'),
    ]

    def compose(self) -> ComposeResult:
        """Compose the service screen layout."""
        yield Header()

        yield Container(
            Vertical(
                Static('SERVICE MANAGEMENT', classes='title'),
                Horizontal(
                    Static(
                        'Manage your container services', classes='subtitle'
                    ),
                    Static('Total Services: 6', classes='subtitle-right'),
                    id='screen-header',
                ),
                # Give the main table area more space
                Vertical(
                    self._create_services_table(), id='main-table-container'
                ),
                Horizontal(
                    Button('Start', id='start-service', variant='success'),
                    Button('Stop', id='stop-service', variant='error'),
                    Button('Restart', id='restart-service', variant='warning'),
                    Button('Logs', id='logs-service', variant='primary'),
                    Button('Details', id='details-service', variant='default'),
                    Button('Back', id='back-btn', variant='default'),
                    id='profile-actions',
                ),
                id='screen-content',
            ),
            id='screen-container',
        )

        yield Footer()

    def _create_services_table(self) -> DataTable[Any]:
        """Create the services table."""
        # Create table with explicit height styling
        table: DataTable[Any] = DataTable(id='services-table')
        table.cursor_type = 'row'

        # Apply the same height constraints as profiles table
        table.styles.height = 7
        table.styles.max_height = 7

        table.add_columns(
            'Service', 'Status', 'Ports', 'Image', 'Container ID'
        )

        # This would be populated from actual Sugar config in the future
        table.add_rows(
            [
                (
                    'frontend',
                    '● Running',
                    '3000:3000',
                    'node:16',
                    'abc123def456',
                ),
                (
                    'api',
                    '● Running',
                    '8000:8000',
                    'python:3.10',
                    'def456ghi789',
                ),
                (
                    'db',
                    '● Running',
                    '5432:5432',
                    'postgres:14',
                    '789ghi101112',
                ),
                (
                    'redis',
                    '● Running',
                    '6379:6379',
                    'redis:latest',
                    'jkl131415mno',
                ),
                (
                    'nginx',
                    '● Running',
                    '80:80, 443:443',
                    'nginx:latest',
                    'pqr161718stu',
                ),
                ('worker', '○ Stopped', '-', 'python:3.10', ''),
            ]
        )

        return table

    def on_mount(self) -> None:
        """Handle mounting of the screen."""
        self.notify('Services screen loaded')

        self._update_service_details(
            'frontend', '● Running', '3000:3000', 'node:16', 'abc123def456'
        )

    def _update_service_details(
        self, name: str, status: str, ports: str, image: str, container_id: str
    ) -> None:
        """Update the service details section with the selected service."""
        # Create details container if it doesn't exist
        if not self.query('#service-details'):
            details = Vertical(
                Static('Service Details', classes='section-title'),
                Horizontal(
                    Label('Name:', classes='detail-label'),
                    Label(name, classes='detail-value', id='service-name'),
                ),
                Horizontal(
                    Label('Status:', classes='detail-label'),
                    Label(status, classes='detail-value', id='service-status'),
                ),
                Horizontal(
                    Label('Ports:', classes='detail-label'),
                    Label(ports, classes='detail-value', id='service-ports'),
                ),
                Horizontal(
                    Label('Image:', classes='detail-label'),
                    Label(image, classes='detail-value', id='service-image'),
                ),
                Horizontal(
                    Label('Container ID:', classes='detail-label'),
                    Label(
                        container_id, classes='detail-value', id='container-id'
                    ),
                ),
                id='service-details',
            )

            # Add to the main container
            self.query_one('#main-table-container').mount(Rule())
            self.query_one('#main-table-container').mount(details)
        # Otherwise update existing labels
        else:
            self.query_one('#service-name', Label).update(name)
            self.query_one('#service-status', Label).update(status)
            self.query_one('#service-ports', Label).update(ports)
            self.query_one('#service-image', Label).update(image)
            self.query_one('#container-id', Label).update(container_id)

    def action_refresh(self) -> None:
        """Refresh the services data."""
        self.notify('Refreshing services data...')

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Update details when a service is selected in the table."""
        table = event.data_table
        row_idx = table.cursor_row
        if row_idx is not None:
            # Get the data from the selected row
            row_data = table.get_row_at(row_idx)
            # Update the details section
            self._update_service_details(
                row_data[0], row_data[1], row_data[2], row_data[3], row_data[4]
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == 'back-btn':
            self.app.pop_screen()
            return

        table = self.query_one('#services-table', DataTable)
        if table.cursor_row is None:
            self.notify('Please select a service first', severity='error')
            return

        service = table.get_row_at(table.cursor_row)[0]

        if button_id == 'start-service':
            self.notify(f'Starting {service}...', title='Starting')
        elif button_id == 'stop-service':
            self.notify(f'Stopping {service}...', title='Stopping')
        elif button_id == 'restart-service':
            self.notify(f'Restarting {service}...', title='Restarting')
        elif button_id == 'logs-service':
            try:
                self.app.push_screen('logs')
            except Exception as e:
                self.notify(f'Error opening logs: {e!s}', severity='error')
        elif button_id == 'details-service':
            try:
                self.app.push_screen('details')
            except Exception as e:
                self.notify(f'Error opening details: {e!s}', severity='error')
