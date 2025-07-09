import tkinter as tk
import socket
import psutil
import screeninfo
import json
import os



class SystemInfoOverlay:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("")
        self.root.overrideredirect(True)
        self.root.configure(bg='#f0f0f0')
        self.root.attributes('-topmost', True)

        self.settings = {
            'x_pos': None,
            'y_pos': None,
            'font_size': 10,
            'show_battery': True,
            'show_ip': True,
            'window_width': 130,
            'window_height': 60
        }

        self.load_settings()
        self.create_widgets()
        self.update_info()
        self.update_interval = 1000
        self.schedule_update()
        self.setup_event_bindings()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_settings(self):
        try:
            if os.path.exists('setting.json'):
                with open('setting.json', 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"加载设置失败: {e}")

    def save_settings(self):
        try:
            self.settings['x_pos'] = self.root.winfo_x()
            self.settings['y_pos'] = self.root.winfo_y()
            self.settings['window_width'] = self.root.winfo_width()
            self.settings['window_height'] = self.root.winfo_height()

            with open('setting.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")

    def apply_window_geometry(self):
        if self.settings['x_pos'] is not None and self.settings['y_pos'] is not None:
            self.root.geometry(
                f"{self.settings['window_width']}x{self.settings['window_height']}+"
                f"{self.settings['x_pos']}+{self.settings['y_pos']}"
            )
        else:
            self.position_top_right()

    def position_top_right(self):
        try:
            monitor = screeninfo.get_monitors()[0]
            pos_x = monitor.width - self.settings['window_width']
            pos_y = 0
            self.root.geometry(
                f"{self.settings['window_width']}x{self.settings['window_height']}+"
                f"{pos_x}+{pos_y}"
            )
        except Exception as e:
            print(f"窗口定位错误: {e}")
            self.root.geometry(
                f"{self.settings['window_width']}x{self.settings['window_height']}+100+100"
            )

    def create_widgets(self):
        self.apply_window_geometry()

        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        font_style = ('Arial', self.settings['font_size'])

        if self.settings['show_battery']:
            self.battery_label = tk.Label(
                self.main_frame,
                text="电池: 获取中...",
                font=font_style,
                bg='#f0f0f0',
                anchor='w'
            )
            self.battery_label.pack(fill=tk.X, pady=2)

        if self.settings['show_ip']:
            self.ip_label = tk.Label(
                self.main_frame,
                text="IP: 获取中...",
                font=font_style,
                bg='#f0f0f0',
                anchor='w'
            )
            self.ip_label.pack(fill=tk.X, pady=2)

    def setup_event_bindings(self):
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.on_move)
        self.root.bind("<Button-3>", self.close_app)
        self.root.bind("<Escape>", self.close_app)

    def start_move(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def on_move(self, event):
        if hasattr(self, '_drag_start_x'):
            x = self.root.winfo_x() + (event.x - self._drag_start_x)
            y = self.root.winfo_y() + (event.y - self._drag_start_y)
            self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._initial_width = self.root.winfo_width()
        self._initial_height = self.root.winfo_height()

    def on_resize(self, event):
        if hasattr(self, '_resize_start_x'):
            delta_x = event.x_root - self._resize_start_x
            delta_y = event.y_root - self._resize_start_y
            new_width = max(100, self._initial_width + delta_x)
            new_height = max(50, self._initial_height + delta_y)
            self.root.geometry(f"{new_width}x{new_height}")

    def close_app(self, event=None):
        self.on_close()

    def on_close(self):
        self.save_settings()
        self.root.quit()

    @staticmethod
    def get_ip_address() -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "无网络"

    @staticmethod
    def get_battery_info() -> str:
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return "无电池"

            icon = "⚡" if battery.power_plugged else "🔋"
            return f"{battery.percent}% {icon}"
        except Exception:
            return "未知"

    def update_info(self):
        if self.settings['show_battery']:
            self.battery_label.config(text=f"电池: {self.get_battery_info()}")

        if self.settings['show_ip']:
            self.ip_label.config(text=f"IP: {self.get_ip_address()}")

    def schedule_update(self):
        self.update_info()
        self.root.after(self.update_interval, self.schedule_update)


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemInfoOverlay(root)
    root.mainloop()