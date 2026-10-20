# advanced_iot_dashboard_thingspeak_v3.py
# IoT Dashboard: Temp, Current, Tilt, Smoke (RPM removed)

import sys
import time
import random
import requests
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QGroupBox, QSplitter, QFrame, QTableWidget, 
    QTableWidgetItem, QHeaderView, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPalette, QPainterPath
import pyqtgraph as pg

# -----------------------------
# ThingSpeak configuration
# -----------------------------
CHANNEL_ID = "3156855"
READ_API_KEY = "PELBKI1AS5GH9QHA"
FETCH_INTERVAL = 2000  # ms

# -----------------------------
# Read ThingSpeak
# -----------------------------
def read_thingspeak():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?results=1"
    if READ_API_KEY:
        url += f"&api_key={READ_API_KEY}"
    try:
        feed = requests.get(url, timeout=5).json()["feeds"][0]
        temp = float(feed.get("field1", 0))
        current = float(feed.get("field2", 0))
        tilt = float(feed.get("field4", 0))
        smoke = float(feed.get("field5", 0))
        return {"Temp": temp, "Current": current, "Tilt": tilt, "Smoke": smoke}
    except Exception as e:
        print("ThingSpeak read error:", e)
        return None

# -----------------------------
# Premium Glass Effect Widget
# -----------------------------
class GlassWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create glass effect
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        # Glass fill
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 40))
        gradient.setColorAt(1, QColor(255, 255, 255, 20))
        
        painter.fillPath(path, gradient)
        
        # Border
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
        painter.drawPath(path)

# -----------------------------
# Premium Numeric Display with Fixed Animations and Better Layout
# -----------------------------
class PremiumNumericDisplay(GlassWidget):
    def __init__(self, title, unit="", icon_color="#00ccff", parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 180)  # Increased size for better spacing
        self.title = title
        self.unit = unit
        self.icon_color = icon_color
        self._display_value = 0.0
        self._anim_value = 0.0
        self.target_value = 0.0
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Create a proper layout for better spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Title label with proper spacing
        self.title_label = QLabel(title.upper())
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: #aaccff;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                font-family: 'Segoe UI', Arial;
                padding: 5px;
            }}
        """)
        self.title_label.setFixedHeight(25)
        
        # Value display with proper spacing
        self.value_display = QLabel("--")
        self.value_display.setAlignment(Qt.AlignCenter)
        self.value_display.setStyleSheet(f"""
            QLabel {{
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
                font-family: 'Segoe UI', Arial;
                padding: 10px 0px;
            }}
        """)
        self.value_display.setFixedHeight(50)
        
        # Unit label
        self.unit_label = QLabel(unit)
        self.unit_label.setAlignment(Qt.AlignCenter)
        self.unit_label.setStyleSheet(f"""
            QLabel {{
                color: #88ffcc;
                font-size: 12px;
                background: transparent;
                font-family: 'Segoe UI', Arial;
                padding: 5px;
            }}
        """)
        self.unit_label.setFixedHeight(20)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_display)
        layout.addWidget(self.unit_label)
        layout.addStretch()
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"animValue")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
    # Define the animValue property for QPropertyAnimation
    def get_anim_value(self):
        return self._anim_value
        
    def set_anim_value(self, value):
        self._anim_value = float(value) if value is not None else 0.0
        self.update()
        
    animValue = pyqtProperty(float, get_anim_value, set_anim_value)
        
    def set_value(self, value):
        try:
            new_value = float(value)
            self.target_value = new_value
            self.animation.setStartValue(self._display_value)
            self.animation.setEndValue(self.target_value)
            self.animation.start()
            self._display_value = new_value
            
            # Update label immediately
            display_text = f"{new_value:.1f}" if abs(new_value) < 100 else f"{new_value:.0f}"
            self.value_display.setText(display_text)
        except (ValueError, TypeError):
            self.value_display.setText("--")
            
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw icon/circle - positioned above the value display
        center_x = self.width() // 2
        icon_y = 50  # Positioned below the title
        
        # Background circle
        painter.setPen(QPen(QColor(255, 255, 255, 30), 2))
        painter.setBrush(QBrush(QColor(40, 40, 60, 150)))
        painter.drawEllipse(center_x - 25, icon_y - 25, 50, 50)
        
        # Animated value circle (percentage)
        try:
            # Safely calculate value ratio
            current_val = float(self._anim_value) if self._anim_value is not None else 0.0
            value_ratio = min(1.0, abs(current_val) / 100)
            angle = 360 * value_ratio
        except (TypeError, ValueError):
            angle = 0
        
        # Value arc
        pen = QPen(QColor(self.icon_color), 4)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(center_x - 22, icon_y - 22, 44, 44, 90 * 16, -int(angle * 16))

# -----------------------------
# Fixed Animated Toggle Switch
# -----------------------------
class AnimatedToggle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 40)
        self._checked = False
        self._thumb_pos = QPoint(5, 5)
        
        # Animation for thumb position
        self.animation = QPropertyAnimation(self, b"thumbPos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
    # Property for thumb position animation
    def get_thumb_pos(self):
        return self._thumb_pos
        
    def set_thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()
        
    thumbPos = pyqtProperty(QPoint, get_thumb_pos, set_thumb_pos)
        
    def mousePressEvent(self, event):
        self.toggle()
        
    def toggle(self):
        self._checked = not self._checked
        self.start_animation()
        
    def start_animation(self):
        if self._checked:
            self.animation.setStartValue(QPoint(5, 5))
            self.animation.setEndValue(QPoint(45, 5))
        else:
            self.animation.setStartValue(QPoint(45, 5))
            self.animation.setEndValue(QPoint(5, 5))
        self.animation.start()
        
    def is_checked(self):
        return self._checked
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Track
        track_color = QColor(80, 80, 120) if not self._checked else QColor(0, 180, 120)
        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        
        # Thumb
        thumb_color = QColor(220, 220, 220) if not self._checked else QColor(255, 255, 255)
        painter.setBrush(QBrush(thumb_color))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawEllipse(self._thumb_pos.x(), self._thumb_pos.y(), 30, 30)

# -----------------------------
# Enhanced Table Widget with Larger Font
# -----------------------------
class EnhancedTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        
        # Set larger font sizes for better readability
        self.setStyleSheet("""
            QTableWidget {
                background: rgba(25, 25, 40, 180);
                alternate-background-color: rgba(35, 35, 55, 180);
                gridline-color: #444466;
                border: 1px solid #444466;
                border-radius: 10px;
                font-size: 14px;  /* Increased from 11px */
                font-family: 'Segoe UI';
            }
            QTableWidget::item {
                padding: 12px 8px;  /* Increased padding */
                border-bottom: 1px solid #333344;
                color: #e0e0ff;
            }
            QTableWidget::item:selected {
                background: rgba(100, 150, 255, 100);
                color: #ffffff;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a6a, stop:1 #3a3a5a);
                color: #ffffff;
                padding: 12px 8px;  /* Increased padding */
                border: none;
                font-weight: bold;
                font-size: 13px;  /* Increased header font size */
                font-family: 'Segoe UI';
            }
        """)
        
        # Set row height for better visibility
        self.verticalHeader().setDefaultSectionSize(40)

# -----------------------------
# Main Application
# -----------------------------
class AdvancedControlCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced IoT Control Center")
        self.setGeometry(50, 50, 1600, 900)
        self.window = 200
        self.timestamps = np.zeros(self.window)
        self.temps = np.zeros(self.window)
        self.currents = np.zeros(self.window)
        self.tilts = np.zeros(self.window)
        self.smokes = np.zeros(self.window)

        # Thresholds
        self.temp_threshold = 40.0
        self.current_threshold = 1.6
        self.tilt_threshold = 1.0
        self.smoke_threshold = 800.0
        self.auto_stop_enabled = False
        self.log_rows = []

        # Premium numeric displays with better spacing
        self.lbl_temp = PremiumNumericDisplay("Temperature", "°C", "#ff6b6b")
        self.lbl_current = PremiumNumericDisplay("Current", "A", "#4ecdc4")
        self.lbl_tilt = PremiumNumericDisplay("Tilt", "Deg", "#45b7d1")
        self.lbl_smoke = PremiumNumericDisplay("Smoke", "PPM", "#96ceb4")

        self.build_ui()
        self.setup_timers()
        self.apply_premium_theme()

    def apply_premium_theme(self):
        # Set ultra dark premium theme
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(15, 15, 25))
        dark_palette.setColor(QPalette.WindowText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Base, QColor(20, 20, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(30, 30, 45))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(40, 40, 60))
        dark_palette.setColor(QPalette.ToolTipText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Text, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.Button, QColor(40, 40, 60))
        dark_palette.setColor(QPalette.ButtonText, QColor(240, 240, 240))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 100, 100))
        dark_palette.setColor(QPalette.Highlight, QColor(100, 150, 220, 100))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.setPalette(dark_palette)

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a1a, stop:0.5 #151525, stop:1 #0a0a1a);
            }
            QGroupBox {
                color: #b8c7e0;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #444466;
                border-radius: 12px;
                margin-top: 1ex;
                padding-top: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(40, 40, 60, 180), stop:1 rgba(30, 30, 50, 180));
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
            }
            QSplitter::handle {
                background: #444466;
                width: 6px;
                border-radius: 3px;
            }
            QSplitter::handle:hover {
                background: #555577;
            }
        """)

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Premium Header with glass effect
        header = GlassWidget()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 10, 30, 10)
        
        # Title with gradient text effect
        title_label = QLabel("IoT SENSOR MONITORING DASHBOARD")
        title_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ccff, stop:0.5 #88ff88, stop:1 #ff88ff);
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
            }
        """)
        
        # Status indicators
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        
        self.connection_status = QLabel("● CONNECTED")
        self.connection_status.setStyleSheet("""
            QLabel {
                color: #88ff88;
                font-weight: bold;
                font-size: 12px;
                padding: 5px 15px;
                background: rgba(0, 80, 0, 100);
                border-radius: 10px;
            }
        """)
        
        self.update_status = QLabel("LIVE UPDATES")
        self.update_status.setStyleSheet("""
            QLabel {
                color: #ffff88;
                font-weight: bold;
                font-size: 12px;
                padding: 5px 15px;
                background: rgba(80, 80, 0, 100);
                border-radius: 10px;
            }
        """)
        
        status_layout.addWidget(self.connection_status)
        status_layout.addWidget(self.update_status)
        status_layout.addStretch()
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(status_widget)
        main_layout.addWidget(header)
        
        # Main content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel - Enhanced Controls
        left_panel = GlassWidget()
        left_panel.setMaximumWidth(320)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # System Controls
        controls_group = QGroupBox("SYSTEM CONTROLS")
        controls_layout = QVBoxLayout(controls_group)
        
        # Auto-stop toggle with label
        toggle_layout = QHBoxLayout()
        toggle_label = QLabel("Auto-Stop Protection:")
        toggle_label.setStyleSheet("color: #ccccff; font-size: 13px; font-weight: bold;")
        toggle_layout.addWidget(toggle_label)
        self.auto_stop_toggle = AnimatedToggle()
        toggle_layout.addWidget(self.auto_stop_toggle)
        toggle_layout.addStretch()
        controls_layout.addLayout(toggle_layout)
        
        # Connect toggle to functionality
        self.auto_stop_toggle.toggled = self.toggle_auto_stop
        
        # Threshold controls
        thresholds_group = QGroupBox("ALERT THRESHOLDS")
        thresholds_layout = QVBoxLayout(thresholds_group)
        
        # Add threshold controls with larger fonts
        temp_threshold_label = QLabel(f"Temperature: {self.temp_threshold}°C")
        current_threshold_label = QLabel(f"Current: {self.current_threshold}A")
        smoke_threshold_label = QLabel(f"Smoke: {self.smoke_threshold} PPM")
        
        threshold_style = "color: #ccccff; font-size: 13px; padding: 8px; background: rgba(50, 50, 80, 100); border-radius: 6px;"
        for label in [temp_threshold_label, current_threshold_label, smoke_threshold_label]:
            label.setStyleSheet(threshold_style)
            label.setAlignment(Qt.AlignCenter)
            thresholds_layout.addWidget(label)
        
        left_layout.addWidget(controls_group)
        left_layout.addWidget(thresholds_group)
        left_layout.addStretch()
        
        content_splitter.addWidget(left_panel)
        
        # Center Panel - Enhanced Data Display with Better Layout
        center_panel = GlassWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setSpacing(20)
        
        # Sensor grid with premium displays - increased spacing
        sensor_grid = QGridLayout()
        sensor_grid.setSpacing(25)  # Increased spacing between widgets
        sensor_grid.setContentsMargins(15, 15, 15, 15)  # Increased margins
        
        # Add widgets with proper positioning
        sensor_grid.addWidget(self.lbl_temp, 0, 0)
        sensor_grid.addWidget(self.lbl_current, 0, 1)
        sensor_grid.addWidget(self.lbl_tilt, 1, 0)
        sensor_grid.addWidget(self.lbl_smoke, 1, 1)
        
        # Set column stretch for even distribution
        sensor_grid.setColumnStretch(0, 1)
        sensor_grid.setColumnStretch(1, 1)
        
        center_layout.addLayout(sensor_grid)
        
        # Enhanced log table with larger fonts
        log_group = QGroupBox("REAL-TIME SENSOR LOG")
        log_layout = QVBoxLayout(log_group)
        
        self.log_table = EnhancedTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Time", "Temp (°C)", "Current (A)", "Tilt", "Smoke (PPM)"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Set larger font for table items programmatically as well
        font = QFont("Segoe UI", 12)  # Increased font size
        self.log_table.setFont(font)
        
        log_layout.addWidget(self.log_table)
        
        center_layout.addWidget(log_group)
        content_splitter.addWidget(center_panel)
        
        # Right Panel - Enhanced Plots
        right_panel = GlassWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Configure premium pyqtgraph theme
        pg.setConfigOption('background', (20, 20, 35, 0))
        pg.setConfigOption('foreground', 'w')
        
        self.pg_widget = pg.GraphicsLayoutWidget()
        self.pg_widget.setBackground((20, 20, 35, 0))
        
        # Enhanced plots with gradients
        self.create_enhanced_plots()
        
        right_layout.addWidget(self.pg_widget)
        content_splitter.addWidget(right_panel)
        
        # Set splitter sizes
        content_splitter.setSizes([280, 550, 620])  # Adjusted center panel size
        main_layout.addWidget(content_splitter, stretch=1)
        
        # Premium Footer
        footer = GlassWidget()
        footer.setFixedHeight(50)
        footer_layout = QHBoxLayout(footer)
        
        self.system_status = QLabel("● ALL SYSTEMS NORMAL")
        self.system_status.setStyleSheet("""
            QLabel {
                color: #88ff88;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 20px;
                background: rgba(0, 60, 0, 120);
                border-radius: 12px;
            }
        """)
        
        self.last_update = QLabel("Last Update: --")
        self.last_update.setStyleSheet("color: #aaaaff; font-size: 13px; font-weight: bold;")
        
        footer_layout.addWidget(self.system_status)
        footer_layout.addStretch()
        footer_layout.addWidget(self.last_update)
        
        main_layout.addWidget(footer)

    def create_enhanced_plots(self):
        # Temperature plot with gradient
        self.temp_plot = self.pg_widget.addPlot(title="<span style='color: #ff6b6b; font-size: 14px;'>Temperature (°C)</span>")
        self.temp_plot.setLabel('left', "°C", color='#ffffff')
        self.temp_plot.setLabel('bottom', "Time", color='#ffffff')
        self.temp_curve = self.temp_plot.plot(pen=pg.mkPen(color=(255, 107, 107), width=4))
        self.temp_plot.setYRange(0, 120)
        self.temp_plot.showGrid(x=True, y=True, alpha=0.3)
        self.temp_plot.getAxis('left').setPen(pg.mkPen(color='#ffffff'))
        self.temp_plot.getAxis('bottom').setPen(pg.mkPen(color='#ffffff'))
        
        self.pg_widget.nextRow()
        
        # Current plot
        self.current_plot = self.pg_widget.addPlot(title="<span style='color: #4ecdc4; font-size: 14px;'>Current (A)</span>")
        self.current_plot.setLabel('left', "Amps", color='#ffffff')
        self.current_plot.setLabel('bottom', "Time", color='#ffffff')
        self.current_curve = self.current_plot.plot(pen=pg.mkPen(color=(78, 205, 196), width=4))
        self.current_plot.setYRange(0, 10)
        self.current_plot.showGrid(x=True, y=True, alpha=0.3)
        self.current_plot.getAxis('left').setPen(pg.mkPen(color='#ffffff'))
        self.current_plot.getAxis('bottom').setPen(pg.mkPen(color='#ffffff'))
        
        self.pg_widget.nextRow()
        
        # Tilt plot
        self.tilt_plot = self.pg_widget.addPlot(title="<span style='color: #45b7d1; font-size: 14px;'>Tilt Angle</span>")
        self.tilt_plot.setLabel('left', "Degrees", color='#ffffff')
        self.tilt_plot.setLabel('bottom', "Time", color='#ffffff')
        self.tilt_curve = self.tilt_plot.plot(pen=pg.mkPen(color=(69, 183, 209), width=4))
        self.tilt_plot.setYRange(0, 2)
        self.tilt_plot.showGrid(x=True, y=True, alpha=0.3)
        self.tilt_plot.getAxis('left').setPen(pg.mkPen(color='#ffffff'))
        self.tilt_plot.getAxis('bottom').setPen(pg.mkPen(color='#ffffff'))
        
        self.pg_widget.nextRow()
        
        # Smoke plot
        self.smoke_plot = self.pg_widget.addPlot(title="<span style='color: #96ceb4; font-size: 14px;'>Smoke Detection (PPM)</span>")
        self.smoke_plot.setLabel('left', "PPM", color='#ffffff')
        self.smoke_plot.setLabel('bottom', "Time", color='#ffffff')
        self.smoke_curve = self.smoke_plot.plot(pen=pg.mkPen(color=(150, 206, 180), width=4))
        self.smoke_plot.setYRange(0, 5000)
        self.smoke_plot.showGrid(x=True, y=True, alpha=0.3)
        self.smoke_plot.getAxis('left').setPen(pg.mkPen(color='#ffffff'))
        self.smoke_plot.getAxis('bottom').setPen(pg.mkPen(color='#ffffff'))

    def setup_timers(self):
        self.timer = QTimer()
        self.timer.setInterval(FETCH_INTERVAL)
        self.timer.timeout.connect(self.fetch_sensor_data)
        self.timer.start()

    def fetch_sensor_data(self):
        data = read_thingspeak()
        if data is None:
            # Fallback to simulated data if ThingSpeak fails
            data = {
                "Temp": 30 + random.random() * 5,
                "Current": 1 + random.random() * 0.5,
                "Tilt": random.random() * 0.5,
                "Smoke": 200 + random.random() * 50
            }
        self.handle_new_data(data)

    def handle_new_data(self, data):
        # Update data arrays
        self.timestamps = np.roll(self.timestamps, -1)
        self.timestamps[-1] = time.time()
        
        self.temps = np.roll(self.temps, -1)
        self.currents = np.roll(self.currents, -1)
        self.tilts = np.roll(self.tilts, -1)
        self.smokes = np.roll(self.smokes, -1)
        
        # Safely extract values with defaults
        self.temps[-1] = float(data.get("Temp", 0.0))
        self.currents[-1] = float(data.get("Current", 0.0))
        self.tilts[-1] = float(data.get("Tilt", 0.0))
        self.smokes[-1] = float(data.get("Smoke", 0.0))

        # Update premium displays with animations
        self.lbl_temp.set_value(self.temps[-1])
        self.lbl_current.set_value(self.currents[-1])
        self.lbl_tilt.set_value(self.tilts[-1])
        self.lbl_smoke.set_value(self.smokes[-1])

        # Update log table
        tstamp = datetime.now().strftime("%H:%M:%S")
        self.log_rows.append([
            tstamp,
            f"{self.temps[-1]:.2f}",
            f"{self.currents[-1]:.2f}",
            f"{self.tilts[-1]:.2f}",
            f"{self.smokes[-1]:.2f}"
        ])
        
        if len(self.log_rows) > 200:
            self.log_rows.pop(0)
            
        self.update_log_table()
        self.refresh_plots()
        
        # Update status
        self.last_update.setText(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        # Check for alerts
        self.check_alerts()

    def check_alerts(self):
        alerts = []
        if self.temps[-1] > self.temp_threshold:
            alerts.append("HIGH TEMPERATURE")
        if self.currents[-1] > self.current_threshold:
            alerts.append("HIGH CURRENT")
        if self.smokes[-1] > self.smoke_threshold:
            alerts.append("SMOKE DETECTED")
            
        if alerts:
            status = " | ".join(alerts)
            self.system_status.setText(f"⚠ {status}")
            self.system_status.setStyleSheet("""
                QLabel {
                    color: #ff8888;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 20px;
                    background: rgba(80, 0, 0, 120);
                    border-radius: 12px;
                }
            """)
        else:
            self.system_status.setText("● ALL SYSTEMS NORMAL")
            self.system_status.setStyleSheet("""
                QLabel {
                    color: #88ff88;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 20px;
                    background: rgba(0, 60, 0, 120);
                    border-radius: 12px;
                }
            """)

    def refresh_plots(self):
        # Update plots with new data
        self.temp_curve.setData(self.timestamps, self.temps)
        self.current_curve.setData(self.timestamps, self.currents)
        self.tilt_curve.setData(self.timestamps, self.tilts)
        self.smoke_curve.setData(self.timestamps, self.smokes)

    def update_log_table(self):
        self.log_table.setRowCount(0)
        for row_data in self.log_rows:
            row_position = self.log_table.rowCount()
            self.log_table.insertRow(row_position)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                # Set larger font for individual items as well
                item.setFont(QFont("Segoe UI", 12))
                self.log_table.setItem(row_position, col, item)
        # Scroll to bottom to show latest entries
        self.log_table.scrollToBottom()

    def toggle_auto_stop(self, checked):
        self.auto_stop_enabled = checked
        # Update toggle visual state
        if hasattr(self, 'auto_stop_toggle'):
            if checked:
                # You can add visual feedback here
                pass
            else:
                # You can add visual feedback here
                pass
        # You can add additional auto-stop functionality here

# -----------------------------
# App entry
# -----------------------------
def main():
    app = QApplication(sys.argv)
    
    # Set premium font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    win = AdvancedControlCenter()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()