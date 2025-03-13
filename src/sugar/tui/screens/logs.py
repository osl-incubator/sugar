# src/sugar/tui/screens/logs.py
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Header, Footer, Input
from textual.containers import Container, Horizontal, Vertical
from pathlib import Path
from datetime import datetime
import time
import random

class LogsScreen(Screen):
    """Screen to display service logs with filtering and real-time updates."""
    
    # Match the same CSS path
    CSS_PATH = Path(__file__).parent.parent / "styles/screens.css"
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("f", "toggle_follow", "Follow"),
        ("c", "clear_logs", "Clear"),
        ("r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        self.following = False
        self.service_name = "frontend"
        self.log_levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    
    def compose(self) -> ComposeResult:
        """Compose the logs screen layout."""
        yield Header()
        
        yield Container(
            Vertical(
                Static("SERVICE LOGS", classes="title"),
                
                Horizontal(
                    Static("Real-time container logs", classes="subtitle"),
                    Static("Auto-refresh: On", id="refresh-status", classes="auto-refresh-on"),
                    id="screen-header"
                ),
                
                Horizontal(
                    Button("All", id="filter-all", variant="primary"),
                    Button("INFO", id="filter-info", variant="default"),
                    Button("WARN", id="filter-warn", variant="warning"),
                    Button("ERROR", id="filter-error", variant="error"),
                    Button("DEBUG", id="filter-debug", variant="success"),
                    id="log-level-filters"
                ),
                
                # Simple logs display using a Static widget instead of Log
                Static(id="logs-display", classes="logs-display"),
                
                Horizontal(
                    Button("Back", id="back-btn", variant="default"),
                    Button("Follow", id="follow-btn", variant="primary"),
                    Button("Clear", id="clear-btn", variant="warning"),
                    id="logs-actions"
                ),
                
                id="screen-content"
            ),
            id="screen-container"
        )
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle mounting of the screen."""
        self.notify("Logs screen loaded")
        self.generate_sample_logs()
        
        # Set up auto-refresh timer for log updates
        self.set_interval(3, self.add_new_log_entry)
    
    def generate_sample_logs(self):
        """Generate sample log entries."""
        logs_display = self.query_one("#logs-display", Static)
        
        # Sample log entries with varied severity levels and timestamps
        sample_logs = [
            self.format_log_entry("2024-03-09 10:00:01", "INFO", "Application starting..."),
            self.format_log_entry("2024-03-09 10:00:02", "INFO", "Loading configuration from /etc/config.json"),
            self.format_log_entry("2024-03-09 10:00:03", "DEBUG", "Configuration loaded: { \"port\": 3000, \"env\": \"production\" }"),
            self.format_log_entry("2024-03-09 10:00:05", "INFO", "Connecting to database at db:5432"),
            self.format_log_entry("2024-03-09 10:00:07", "INFO", "Database connection established"),
            self.format_log_entry("2024-03-09 10:00:10", "INFO", "Starting web server on port 3000"),
            self.format_log_entry("2024-03-09 10:00:15", "INFO", "Server listening at http://0.0.0.0:3000"),
            self.format_log_entry("2024-03-09 10:01:02", "INFO", "Received request GET /api/status"),
            self.format_log_entry("2024-03-09 10:01:03", "DEBUG", "Request headers: { \"auth\": \"***\" }"),
            self.format_log_entry("2024-03-09 10:01:04", "INFO", "Response sent: 200 OK (15ms)")
        ]
        
        # Join log entries with newlines and update the display
        logs_text = "\n".join(sample_logs)
        logs_display.update(logs_text)
    
    def format_log_entry(self, timestamp, level, message):
        """Format a log entry."""
        timestamp_color = "cyan"
        level_color = {
            "INFO": "green",
            "WARN": "yellow",
            "ERROR": "red",
            "DEBUG": "blue"
        }.get(level, "white")
        
        # Use simple colorization for the timestamp and level
        return f"[{timestamp_color}]{timestamp}[/] [{level_color}]{level:7}[/] {message}"
    
    def add_new_log_entry(self) -> None:
        """Add a new log entry if following is enabled."""
        if not self.following:
            return
            
        logs_display = self.query_one("#logs-display", Static)
        current_logs = logs_display.render()
        
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Random log level
        level = random.choice(self.log_levels)
        
        # Sample messages based on log level
        messages = {
            "INFO": [
                "Received request GET /api/status",
                "Processing batch job #" + str(random.randint(1000, 9999)),
                "Response sent: 200 OK (" + str(random.randint(5, 150)) + "ms)"
            ],
            "WARN": [
                "High CPU usage detected: " + str(random.randint(70, 95)) + "%",
                "Slow query detected (" + str(random.randint(1, 10)) + "s)"
            ],
            "ERROR": [
                "Failed to connect to service: connection refused",
                "Database query timeout after " + str(random.randint(10, 60)) + "s"
            ],
            "DEBUG": [
                "Request parameters: { \"id\": " + str(random.randint(1, 1000)) + " }",
                "Cache hit ratio: " + str(random.randint(60, 95)) + "%"
            ]
        }
        
        # Select a random message based on the level
        message = random.choice(messages[level])
        
        # Format and add the log entry
        log_entry = self.format_log_entry(timestamp, level, message)
        
        # Add to current logs and update the display
        # Keep only the last 20 lines to avoid overwhelming the display
        log_lines = current_logs.split("\n")
        log_lines.append(log_entry)
        if len(log_lines) > 20:
            log_lines = log_lines[-20:]
        
        logs_display.update("\n".join(log_lines))
    
    def action_toggle_follow(self) -> None:
        """Toggle log following."""
        self.following = not self.following
        button = self.query_one("#follow-btn", Button)
        button.variant = "success" if self.following else "primary"
        button.label = "Following" if self.following else "Follow"
        
        status_label = "Auto-refresh: On" if self.following else "Auto-refresh: Off"
        self.query_one("#refresh-status", Static).update(status_label)
        self.query_one("#refresh-status").set_classes(
            "auto-refresh-on" if self.following else "auto-refresh-off"
        )
        
        status = "enabled" if self.following else "disabled"
        self.notify(f"Log following {status}")
    
    def action_clear_logs(self) -> None:
        """Clear all logs."""
        logs_display = self.query_one("#logs-display", Static)
        logs_display.update("")
        self.notify("Logs cleared")
    
    def apply_filter(self, level=None):
        """Apply a log level filter."""
        # Reset button variants
        for btn_id in ["filter-all", "filter-info", "filter-warn", "filter-error", "filter-debug"]:
            btn = self.query_one(f"#{btn_id}", Button)
            btn.variant = "default"
        
        # Set active filter button
        if level:
            self.query_one(f"#filter-{level.lower()}", Button).variant = "primary"
        else:
            self.query_one("#filter-all", Button).variant = "primary"
        
        # Apply filter logic here (in a real implementation)
        filter_text = f"level: {level}" if level else "all levels"
        self.notify(f"Filter applied: {filter_text}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        if button_id == "follow-btn":
            self.action_toggle_follow()
        elif button_id == "clear-btn":
            self.action_clear_logs()
        elif button_id == "back-btn":
            self.app.pop_screen()
        elif button_id == "filter-all":
            self.apply_filter()
        elif button_id == "filter-info":
            self.apply_filter("INFO")
        elif button_id == "filter-warn":
            self.apply_filter("WARN")
        elif button_id == "filter-error":
            self.apply_filter("ERROR")
        elif button_id == "filter-debug":
            self.apply_filter("DEBUG")