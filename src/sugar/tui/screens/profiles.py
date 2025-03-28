"""Profiles management screen for Sugar TUI."""

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

# Define the type parameter for Screen
T = TypeVar('T')


class ProfileScreen(Screen[T]):
    """Screen for managing profiles."""

    # Define CSS path for screen-specific styles
    CSS_PATH = Path(__file__).parent.parent / 'styles/screens.css'

    BINDINGS = [
        ('escape', 'app.pop_screen', 'Back'),
        ('s', "app.push_screen('services')", 'Services'),
        ('r', 'refresh', 'Refresh'),
    ]

    def compose(self) -> ComposeResult:
        """Compose the profile screen."""
        yield Header()

        yield Container(
            Vertical(
                Static('PROFILE MANAGEMENT', classes='title'),
                Horizontal(
                    Static('Manage your Sugar profiles', classes='subtitle'),
                    Static('Total Profiles: 4', classes='subtitle-right'),
                    id='screen-header',
                ),
                # Give the main table area more space
                Vertical(
                    self._create_profiles_table(), id='main-table-container'
                ),
                Horizontal(
                    Button(
                        'Add Profile', id='add-profile-btn', variant='primary'
                    ),
                    Button(
                        'Edit Profile',
                        id='edit-profile-btn',
                        variant='primary',
                    ),
                    Button(
                        'Delete Profile',
                        id='delete-profile-btn',
                        variant='error',
                    ),
                    Button('Back', id='back-btn', variant='default'),
                    id='profile-actions',
                ),
                id='screen-content',
            ),
            id='screen-container',
        )

        yield Footer()

    def _create_profiles_table(self) -> DataTable[Any]:
        """Create the profiles table."""
        # Create the table and give it explicit height styling
        profiles_table: DataTable[Any] = DataTable(id='profiles-detail-table')
        profiles_table.cursor_type = 'row'
        # Set explicit height to ensure visibility
        # profiles_table.styles.height = "1fr"
        # profiles_table.styles.min_height = 15

        profiles_table.add_columns(
            'Profile', 'Project Name', 'Config Path', 'Services', 'Status'
        )

        # Add mock data
        profiles_table.add_rows(
            [
                (
                    'development',
                    'project-dev',
                    'containers/dev/compose.yaml',
                    'frontend, api, db',
                    '● Active',
                ),
                (
                    'staging',
                    'project-staging',
                    'containers/staging/compose.yaml',
                    'All services',
                    '● Active',
                ),
                (
                    'production',
                    'project-prod',
                    'containers/prod/compose.yaml',
                    'web, api, db, cache',
                    '○ Inactive',
                ),
                (
                    'testing',
                    'project-test',
                    'containers/test/compose.yaml',
                    'test-suite, mockdb',
                    '○ Inactive',
                ),
            ]
        )

        return profiles_table

    def on_mount(self) -> None:
        """Handle mounting of the screen."""
        self.notify('Profile screen loaded')

        # Update the details section with the first profile's data
        self._update_profile_details(
            'development',
            'project-dev',
            'containers/dev/compose.yaml',
            'frontend, api, db',
        )

    def _update_profile_details(
        self, name: str, project: str, config: str, services: str
    ) -> None:
        """Update the profile details section with the selected profile."""
        # Create details container if it doesn't exist
        # Fix: Use single # for ID selector
        if not self.query('#profile-details'):
            details = Vertical(
                Static('Profile Details', classes='section-title'),
                Horizontal(
                    Label('Name:', classes='detail-label'),
                    Label(name, classes='detail-value', id='profile-name'),
                ),
                Horizontal(
                    Label('Project:', classes='detail-label'),
                    Label(project, classes='detail-value', id='project-name'),
                ),
                Horizontal(
                    Label('Config:', classes='detail-label'),
                    Label(config, classes='detail-value', id='config-path'),
                ),
                Horizontal(
                    Label('Services:', classes='detail-label'),
                    Label(
                        services, classes='detail-value', id='services-list'
                    ),
                ),
                id='profile-details',
            )

            # Add to the main container
            self.query_one('#main-table-container').mount(Rule())
            self.query_one('#main-table-container').mount(details)
        # Otherwise update existing labels
        else:
            self.query_one('#profile-name', Label).update(name)
            self.query_one('#project-name', Label).update(project)
            self.query_one('#config-path', Label).update(config)
            self.query_one('#services-list', Label).update(services)

    def action_refresh(self) -> None:
        """Refresh the profiles data."""
        self.notify('Refreshing profiles data...')

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Update details when a profile is selected in the table."""
        table = event.data_table
        row_idx = table.cursor_row
        if row_idx is not None:
            # Get the data from the selected row
            row_data = table.get_row_at(row_idx)
            # Update the details section
            self._update_profile_details(
                row_data[0], row_data[1], row_data[2], row_data[3]
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == 'add-profile-btn':
            self.notify('Adding new profile...')
        elif button_id == 'edit-profile-btn':
            table = self.query_one('#profiles-detail-table', DataTable)
            if table.cursor_row is not None:
                profile = table.get_row_at(table.cursor_row)[0]
                self.notify(f'Editing profile: {profile}')
            else:
                self.notify('Please select a profile first', severity='error')
        elif button_id == 'delete-profile-btn':
            table = self.query_one('#profiles-detail-table', DataTable)
            if table.cursor_row is not None:
                profile = table.get_row_at(table.cursor_row)[0]
                self.notify(f'Deleting profile: {profile}', severity='warning')
            else:
                self.notify('Please select a profile first', severity='error')
        elif button_id == 'back-btn':
            self.app.pop_screen()
