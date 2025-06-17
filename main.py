import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QGroupBox, QLabel, QRadioButton, QMessageBox, QFileDialog,
    QLineEdit, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from Launcher import LauncherDesigner # 确保从 Launcher.py 导入 LauncherDesigner
from AppCreater import AppCreaterWindow
from MyUI import UItemCreaterWindow

class MainWindow(QWidget, UItemCreaterWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exe_path = ""
        self.png_path = ""

        self.setWindowTitle('MacAppCreater')
        self.setGeometry(50, 80, 450, 400) # 设置初始大小
        self.center_on_screen()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 顶部标签
        top_label = QLabel("欢迎使用Mac app生成器")
        top_label.setAlignment(Qt.AlignCenter)
        top_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(top_label)

        # 执行文件选择区域
        executable_selection_layout = QHBoxLayout()
        self.executable_path_display = QLineEdit()
        self.executable_path_display.setPlaceholderText("未选择执行文件")
        self.executable_path_display.setReadOnly(True) # 设置为只读
        executable_selection_layout.addWidget(self.executable_path_display)

        self.select_file_button = QPushButton("选择执行文件") # 将按钮保存为实例属性
        self.select_file_button.clicked.connect(self.select_executable_file)
        executable_selection_layout.addWidget(self.select_file_button)

        main_layout.addLayout(executable_selection_layout)

        # 实例化 Designer 作为组件
        self.launcherdesigner = LauncherDesigner(self) # 将 self 作为父级传入
        main_layout.addWidget(self.launcherdesigner)

        # 图标选择区域
        icon_selection_layout = QHBoxLayout()
        self.icon_path_display = QLineEdit()
        self.icon_path_display.setPlaceholderText("未选择图标文件 (仅支持PNG)")
        self.icon_path_display.setReadOnly(True) # 设置为只读
        icon_selection_layout.addWidget(self.icon_path_display)

        self.select_icon_button = QPushButton("选择图标图片") # 将按钮保存为实例属性
        self.select_icon_button.clicked.connect(self.select_icon_file)
        icon_selection_layout.addWidget(self.select_icon_button)

        main_layout.addLayout(icon_selection_layout)

        # 默认禁用图标选择控件
        self.icon_path_display.setEnabled(False)
        self.select_icon_button.setEnabled(False)

        # --- 新增的生成APP按钮 ---
        self.generate_app_button = QPushButton("生成APP")
        self.generate_app_button.clicked.connect(self.show_appcreater_window)
        self.generate_app_button.setEnabled(False) # 初始禁用
        main_layout.addWidget(self.generate_app_button)
        # --- 结束新增 ---

    def center_on_screen(self):
        """
        将 QMainWindow 窗口居中显示在主屏幕上。
        """
        # 获取屏幕的几何信息
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # 获取窗口自身的几何信息（包括边框、标题栏等）
        qr = self.frameGeometry()
        window_width = qr.width()
        window_height = qr.height()

        # 计算新的左上角 x 和 y 坐标
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # 移动窗口到计算出的位置
        self.move(x, y)

    def select_executable_file(self):
        """
        打开文件对话框以选择可执行文件（Python、Shell 或系统命令）。
        选定的路径随后显示在 QLineEdit 中。
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择执行文件",
            "", # 从当前目录或上次使用的目录开始
            "所有可执行文件 (*.py *.sh *.command);;Python 脚本 (*.py);;Shell 脚本 (*.sh *.command);;所有文件 (*)",
            options=options
        )
        if file_path:
            self.exe_path = file_path
            self.executable_path_display.setText(file_path)

            # 成功选择执行文件后，禁用选择执行文件按钮
            self.select_file_button.setEnabled(False)
            self.executable_path_display.setReadOnly(True) # 确保路径显示框也是只读的

            # 启用 LauncherDesigner、图标选择控件和生成APP按钮
            self.launcherdesigner.set_designer_enabled(True)
            self.icon_path_display.setEnabled(True)
            self.select_icon_button.setEnabled(True)
            self.generate_app_button.setEnabled(True) # 启用生成APP按钮
        else:
            self.exe_path = ""
            self.executable_path_display.clear() # 清空显示

            # 如果用户取消选择，重新启用选择执行文件按钮
            self.select_file_button.setEnabled(True) # 重新启用
            self.executable_path_display.setReadOnly(True) # 保持只读

            # 禁用 LauncherDesigner、图标选择控件和生成APP按钮
            self.launcherdesigner.set_designer_enabled(False)
            self.icon_path_display.setEnabled(False)
            self.select_icon_button.setEnabled(False)
            self.icon_path_display.clear() # 清空图标路径显示
            self.generate_app_button.setEnabled(False) # 禁用生成APP按钮


    def select_icon_file(self):
        """
        打开文件对话框以选择图标文件（仅限PNG）。
        选定的路径随后显示在 QLineEdit 中。
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图标图片",
            "", # 从当前目录或上次使用的目录开始
            "PNG 图片 (*.png);;所有文件 (*)", # 仅支持PNG文件
            options=options
        )
        if file_path:
            self.icon_path_display.setText(file_path)
            self.png_path = file_path
        # 如果用户取消选择，通常保持上次选择或不做额外处理。

    def show_appcreater_window(self):
        """
        创建并显示 AppCreaterWindow 实例。
        """
        uijson=""
        if self.launcherdesigner.is_enable_widgets_radio_checked():
            uijson = self.launcherdesigner.get_ui_description_data()

        # 弹出新的内容窗口
        # Make sure 'self.root' is defined or use 'self' if AppCreaterWindow
        # expects the main window instance directly for its parent.
        # Assuming 'self' is the correct parent for a new dialog.
        app_creator_dialog = AppCreaterWindow(
            self, # Pass the MainWindow instance as the parent
            executable_path=self.exe_path,
            image_path=self.png_path,
            json_data=uijson
        )
        app_creator_dialog.exec_() # Use exec_() for modal dialogs


# --- 主应用类，封装整个应用程序的启动逻辑 ---
class PyQtUIDesignerApp:
    def __init__(self):
        self._app = None
        self._main_window = None # 现在持有的是 MainWindow 实例

    def run(self):
        """启动 PyQt UI Designer 应用程序。"""
        if QApplication.instance():
            self._app = QApplication.instance()
        else:
            self._app = QApplication(sys.argv)

        self._main_window = MainWindow() # 创建 MainWindow 实例
        self._main_window.show() # 显示 MainWindow
        sys.exit(self._app.exec_())

# 在你的脚本中启动 Designer 应用
if __name__ == '__main__':
    app_instance = PyQtUIDesignerApp()
    app_instance.run()