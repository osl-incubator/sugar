from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Label, Button, Rule
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.binding import Binding
from pathlib import Path
import time
import json
from datetime import datetime

class SugarTUI(App):
    """Sugar Terminal User Interface application."""
    
    TITLE = "Sugar TUI — Container Management Simplified"
    
    # Use the CSS file path
    CSS_PATH = Path(__file__).parent / "styles/styles.css"
    
    # Path to the mock data JSON file
    DATA_PATH = Path(__file__).parent / "data/app.json"
    # DATA_PATH = Path("/data/mock_data.json")
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("p", "push_screen('profiles')", "Profiles"),
        Binding("s", "push_screen('services')", "Services"),
        Binding("l", "logs", "Logs"),
        Binding("d", "details", "Details"),
        Binding("r", "refresh", "Refresh"),
        Binding("escape", "back", "Back"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_data = self.load_mock_data()
    
    def load_mock_data(self):
        """Load mock data from JSON file."""
        try:
            with open(self.DATA_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading mock data: {e}")
            # Return default empty data structure if file can't be loaded
            return {
                "profiles": [],
                "services": [],
                "system_metrics": {}
            }
    
    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()
        
        yield Container(
            Vertical(
                Static("SUGAR TERMINAL USER INTERFACE", classes="title"),
                Static("Container Management Dashboard", classes="subtitle"),
                
                # Create a dashboard grid with 4 panels
               Grid(
                    # Profiles Panel
                    Vertical(
                        Static("ACTIVE PROFILES", classes="dashboard-header"),
                        self._create_profiles_panel(),
                        classes="dashboard-panel profiles-panel"
                    ),
                    
                    # Services Panel
                    Vertical(
                        Static("RUNNING SERVICES", classes="dashboard-header"),
                        self._create_services_panel(),
                        classes="dashboard-panel services-panel"
                    ),
                    
                    # Status Panel
                    Vertical(
                        Static("SYSTEM METRICS", classes="dashboard-header"),
                        self._create_status_panel(),
                        classes="dashboard-panel metrics-panel"
                    ),
                    
                    # Actions Panel
                    Vertical(
                        Static("QUICK ACTIONS", classes="dashboard-header"),
                        self._create_actions_panel(),
                        classes="dashboard-panel actions-panel"
                    ),
                    
                    id="dashboard-grid"
                ),
                
                id="main-content"
            ),
            id="app-container"
        )
        
        yield Footer()
    
    def _create_profiles_panel(self) -> DataTable:
        """Create the profiles panel for the dashboard."""
        profiles_table = DataTable()
        profiles_table.cursor_type = "row"
        profiles_table.add_columns("Profile", "Services", "Status")
        
        # Add data from JSON
        if self.mock_data.get("profiles"):
            for profile in self.mock_data["profiles"]:
                profiles_table.add_row(
                    profile["profile"],
                    profile["services"],
                    profile["status"]
                )
        
        return profiles_table
    
    def _create_services_panel(self) -> DataTable:
        """Create the services panel for the dashboard."""
        services_table = DataTable()
        services_table.cursor_type = "row"
        services_table.add_columns("Service", "Status", "Ports", "CPU", "Memory")
        
        # Add data from JSON
        if self.mock_data.get("services"):
            for service in self.mock_data["services"]:
                services_table.add_row(
                    service["service"],
                    service["status"],
                    service["ports"],
                    service["cpu"],
                    service["memory"]
                )
        
        return services_table
    
    def _create_status_panel(self) -> Vertical:
        """Create the system status panel for the dashboard."""
        metrics = self.mock_data.get("system_metrics", {})
        
        return Vertical(
            Horizontal(
                Label("Active Profiles:", classes="data-label"),
                Label(metrics.get("active_profiles", "N/A"), classes="data-value")
            ),
            Horizontal(
                Label("Running Containers:", classes="data-label"),
                Label(metrics.get("running_containers", "N/A"), classes="data-value")
            ),
            Rule(),
            Horizontal(
                Label("CPU Usage:", classes="data-label"),
                Label(metrics.get("cpu_usage", "N/A"), classes="data-value-highlight")
            ),
            Horizontal(
                Label("Memory Usage:", classes="data-label"),
                Label(metrics.get("memory_usage", "N/A"), classes="data-value-highlight")
            ),
            Horizontal(
                Label("Disk Usage:", classes="data-label"),
                Label(metrics.get("disk_usage", "N/A"), classes="data-value")
            ),
            Rule(),
            Horizontal(
                Label("Network In:", classes="data-label"),
                Label(metrics.get("network_in", "N/A"), classes="data-value-blue")
            ),
            Horizontal(
                Label("Network Out:", classes="data-label"),
                Label(metrics.get("network_out", "N/A"), classes="data-value-purple")
            ),
            Rule(),
            Horizontal(
                Label("Uptime:", classes="data-label"),
                Label(metrics.get("uptime", "N/A"), classes="data-value")
            ),
            classes="dashboard-data"
        )
    
    def _create_actions_panel(self) -> Vertical:
        """Create the quick actions panel for the dashboard."""
        return Vertical(
            Button("Start All Services", id="start-all-btn", variant="success"),
            Button("Stop All Services", id="stop-all-btn", variant="error"),
            Button("Restart Services", id="restart-all-btn", variant="warning"),
            Button("View Logs", id="view-logs-btn", variant="primary"),
            Button("Service Details", id="details-btn", variant="default"),
            Button("Run Health Checks", id="health-btn", variant="success"),
            classes="action-buttons"
        )
    
    def on_mount(self) -> None:
        """Event handler called when app is mounted."""
        try:
            from sugar.tui.screens.profiles import ProfileScreen
            from sugar.tui.screens.services import ServiceScreen
            from sugar.tui.screens.logs import LogsScreen
            from sugar.tui.screens.details import DetailsScreen
            
            self.install_screen(ProfileScreen(), name="profiles")
            self.install_screen(ServiceScreen(), name="services")
            self.install_screen(LogsScreen(), name="logs")
            self.install_screen(DetailsScreen(), name="details")
            
            print("Screens installed successfully")
        except ImportError as e:
            print(f"Error loading screens: {e}")
            self._create_basic_screens()
    
    def action_refresh(self) -> None:
        """Refresh the dashboard data."""
        self.notify("Refreshing dashboard data...")
        # Reload data from JSON file
        self.mock_data = self.load_mock_data()
        self.app.refresh()
    
    def action_logs(self) -> None:
        """View logs."""
        self.notify("Viewing logs...")
        try:
            self.push_screen("logs")
        except Exception:
            self.notify("Logs screen not available", severity="error")
    
    def action_details(self) -> None:
        """View details."""
        self.notify("Viewing details...")
        try:
            self.push_screen("details")
        except Exception:
            self.notify("Details screen not available", severity="error")
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        try:
            self.pop_screen()
        except Exception:
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses on the dashboard."""
        button = event.button
        button_text = button.label if hasattr(button, 'label') else ""
        
        if "Start" in button_text:
            self.notify("Starting all services...", title="Starting")
        elif "Stop" in button_text:
            self.notify("Stopping all services...", title="Stopping")
        elif "Restart" in button_text:
            self.notify("Restarting all services...", title="Restarting")
        elif "Logs" in button_text:
            self.action_logs()
        elif "Details" in button_text:
            self.action_details()
        elif "Health" in button_text:
            self.notify("Running health checks...", title="Health Check")
    
    def _create_basic_screens(self):
        """Create basic screen files if they don't exist."""
        from textual.screen import Screen
        from textual.widgets import Static
        
        class BasicScreen(Screen):
            def compose(self):
                yield Static("Coming soon...", classes="title")
        
        self.install_screen(BasicScreen(), name="profiles")
        self.install_screen(BasicScreen(), name="services")
        self.install_screen(BasicScreen(), name="logs")
        self.install_screen(BasicScreen(), name="details")
        
        print("Created and installed basic screens")

def run():
    """Run the Sugar TUI application."""
    print("Inside run() function")
    app = SugarTUI()
    app.run()

if __name__ == "__main__":
    run()