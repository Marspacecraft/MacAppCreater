import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QGroupBox, QLabel, QRadioButton, QMessageBox, QFileDialog,
    QLineEdit, QDialog, QDialogButtonBox, QListWidget, QScrollArea
)
from PyQt5.QtCore import Qt


class ButtonConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加无参参数")
        self.layout = QVBoxLayout()

        self.name_label = QLabel("参数:")
        self.name_input = QLineEdit("")
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.desc_label = QLabel("参数说明:")
        self.desc_input = QLineEdit("")
        self.layout.addWidget(self.desc_label)
        self.layout.addWidget(self.desc_input)

        self.enabled_group_box = QGroupBox("初始状态")
        self.enabled_layout = QHBoxLayout()
        self.enabled_radio = QRadioButton("启用")
        self.disabled_radio = QRadioButton("禁用")
        self.enabled_radio.setChecked(True)
        self.enabled_layout.addWidget(self.enabled_radio)
        self.enabled_layout.addWidget(self.disabled_radio)
        self.enabled_group_box.setLayout(self.enabled_layout)
        self.layout.addWidget(self.enabled_group_box)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_config(self):
        return {
            "name": self.name_input.text(),
            "description": self.desc_input.text(),
            "enabled": self.enabled_radio.isChecked()
        }


# --- ComboConfigDialog 类 ---
class ComboConfigDialog(QDialog):
    def __init__(self, parent=None, initial_items=None):
        super().__init__(parent)
        self.setWindowTitle("添加有参参数")
        self.layout = QVBoxLayout()

        self.desc_label = QLabel("参数说明:")
        self.desc_input = QLineEdit("")
        self.layout.addWidget(self.desc_label)
        self.layout.addWidget(self.desc_input)

        self.enabled_group_box = QGroupBox("初始状态")
        self.enabled_layout = QHBoxLayout()
        self.enabled_radio = QRadioButton("启用")
        self.disabled_radio = QRadioButton("禁用")
        self.enabled_radio.setChecked(True)
        self.enabled_layout.addWidget(self.enabled_radio)
        self.enabled_layout.addWidget(self.disabled_radio)
        self.enabled_group_box.setLayout(self.enabled_layout)
        self.layout.addWidget(self.enabled_group_box)

        item_input_layout = QHBoxLayout()
        self.item_label = QLabel("参数内容:")
        self.item_input = QLineEdit()
        self.add_item_btn = QPushButton("添加参数")
        self.add_item_btn.clicked.connect(self.add_item)
        item_input_layout.addWidget(self.item_label)
        item_input_layout.addWidget(self.item_input)
        item_input_layout.addWidget(self.add_item_btn)
        self.layout.addLayout(item_input_layout)

        self.items_list_widget = QListWidget()
        self.layout.addWidget(self.items_list_widget)

        self.remove_item_btn = QPushButton("删除选中参数")
        self.remove_item_btn.clicked.connect(self.remove_item)
        self.layout.addWidget(self.remove_item_btn)

        self.default_combo_label = QLabel("默认参数:")
        self.default_selected_combo = QComboBox()
        self.layout.addWidget(self.default_combo_label)
        self.layout.addWidget(self.default_selected_combo)

        self.items_list_widget.itemChanged.connect(self.update_default_combo)
        self.items_list_widget.model().rowsInserted.connect(self.update_default_combo)
        self.items_list_widget.model().rowsRemoved.connect(self.update_default_combo)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)
        self.update_default_combo()

    def add_item(self):
        item_text = self.item_input.text().strip()
        if item_text and self.items_list_widget.findItems(item_text, Qt.MatchExactly) == []:
            self.items_list_widget.addItem(item_text)
            self.item_input.clear()
            self.update_default_combo()
        elif item_text:
            QMessageBox.warning(self, "重复参数", "该参数已存在。")

    def remove_item(self):
        current_row = self.items_list_widget.currentRow()
        if current_row >= 0:
            self.items_list_widget.takeItem(current_row)
            self.update_default_combo()
        else:
            QMessageBox.warning(self, "未选择", "请选择一个要删除的参数。")

    def update_default_combo(self):
        self.default_selected_combo.clear()
        items = [self.items_list_widget.item(i).text() for i in range(self.items_list_widget.count())]
        self.default_selected_combo.addItems(items)

    def get_config(self):
        items = [self.items_list_widget.item(i).text() for i in range(self.items_list_widget.count())]
        default_index = self.default_selected_combo.currentIndex()
        return {
            "items": items,
            "default_index": default_index if default_index != -1 else 0,
            "description": self.desc_input.text(),
            "enabled": self.enabled_radio.isChecked()
        }


# --- 新增 FileSelectConfigDialog 类 ---
class FileSelectConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加文件选择参数")
        self.layout = QVBoxLayout()

        self.desc_label = QLabel("参数说明:")
        self.desc_input = QLineEdit("")
        self.layout.addWidget(self.desc_label)
        self.layout.addWidget(self.desc_input)

        self.initial_path_label = QLabel("默认路径 (可选):")
        self.initial_path_input = QLineEdit("")
        self.layout.addWidget(self.initial_path_label)
        self.layout.addWidget(self.initial_path_input)

        self.enabled_group_box = QGroupBox("初始状态")
        self.enabled_layout = QHBoxLayout()
        self.enabled_radio = QRadioButton("启用")
        self.disabled_radio = QRadioButton("禁用")
        self.enabled_radio.setChecked(True)
        self.enabled_layout.addWidget(self.enabled_radio)
        self.enabled_layout.addWidget(self.disabled_radio)
        self.enabled_group_box.setLayout(self.enabled_layout)
        self.layout.addWidget(self.enabled_group_box)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_config(self):
        return {
            "description": self.desc_input.text(),
            "initial_path": self.initial_path_input.text(),
            "enabled": self.enabled_radio.isChecked()
        }


# --- 新增 TextInputConfigDialog 类 ---
class TextInputConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加文本输入参数")
        self.layout = QVBoxLayout()

        self.desc_label = QLabel("参数说明:")
        self.desc_input = QLineEdit("")
        self.layout.addWidget(self.desc_label)
        self.layout.addWidget(self.desc_input)

        self.default_text_label = QLabel("默认文本 (可选):")
        self.default_text_input = QLineEdit("")
        self.layout.addWidget(self.default_text_label)
        self.layout.addWidget(self.default_text_input)

        self.enabled_group_box = QGroupBox("初始状态")
        self.enabled_layout = QHBoxLayout()
        self.enabled_radio = QRadioButton("启用")
        self.disabled_radio = QRadioButton("禁用")
        self.enabled_radio.setChecked(True)
        self.enabled_layout.addWidget(self.enabled_radio)
        self.enabled_layout.addWidget(self.disabled_radio)
        self.enabled_group_box.setLayout(self.enabled_layout)
        self.layout.addWidget(self.enabled_group_box)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_config(self):
        return {
            "description": self.desc_input.text(),
            "default_text": self.default_text_input.text(),
            "enabled": self.enabled_radio.isChecked()
        }


class UItemCreaterWindow:
    # 定义通用的样式表字符串
    WIDGET_GROUP_STYLE = """
        QGroupBox {
            border: 1px solid #c0c0c0; /* 柔和的边框 */
            border-radius: 5px; /* 圆角 */
            margin-top: 5px; /* 顶部外边距 */
            padding-top: 8px; /* 内部上边距，为标题留出空间 */
            padding-left: 8px;
            padding-right: 8px;
            padding-bottom: 8px;
            font-size: 14px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left; /* 标题位置 */
            padding: 0 5px; /* 标题内边距 */
            /* color: #333333; */ /* 移除标题颜色 */
            border-radius: 3px;
        }
        QRadioButton {
            spacing: 5px;
            font-size: 13px;
            /* color: #555555; */ /* 移除文字颜色 */
        }
        QPushButton {
            min-width: 80px; /* 调整按键的最小宽度 */
            padding: 5px 10px;
            border-radius: 4px;
            border: 1px solid #cccccc;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #d0d0d0; /* 悬停时仍可有背景色 */
        }
        QPushButton:pressed {
            background-color: #c0c0c0; /* 按下时仍可有背景色 */
        }
        QPushButton:disabled {
            color: #aaaaaa;
            border-color: #e0e0e0;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            font-size: 13px;
        }
        QLineEdit:read-only {
            background-color: #eeeeee; /* 只读文本框可以保留浅背景色 */
            /* color: #666666; */ /* 移除只读文本框的颜色 */
        }
        QComboBox {
            min-width: 120px; /* 调整下拉菜单的最小宽度 */
            padding: 5px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            font-size: 13px;
        }
        QComboBox::drop-down {
            border-left: 1px solid #cccccc;
        }
        QLabel {
            /* color: black; */ /* 移除 QLabel 的默认颜色设置 */
        }
    """

    def _parse_ui_elements_data_and_create_widgets(self, ui_elements_data, target_layout):
        """
        从UI元素数据创建并添加相应的QWidgets到给定的布局。
        此方法可以被继承此Mixin的类调用以生成UI。
        Args:
            ui_elements_data (list): 包含UI元素描述字典的列表。
            target_layout (QLayout): 要添加生成控件的布局。
        Returns:
            list: 包含所有生成的 widget 实例及其名称或描述的元组列表。
        """
        all_widgets_for_preview = []

        for element in ui_elements_data:
            widget_type = element.get("type")

            # 所有组件都将包裹在一个QGroupBox中，并应用统一的样式
            widget_group = QGroupBox(f"{element.get('description', '未知参数')}")
            widget_group.setStyleSheet(self.WIDGET_GROUP_STYLE)
            # 设置最小宽度以确保大小一致，可以根据需要调整
            widget_group.setMinimumWidth(350)
            widget_group.setMaximumWidth(500)  # 可以限制最大宽度，防止过宽

            group_inner_layout = QHBoxLayout()
            widget_group.setLayout(group_inner_layout)
            group_inner_layout.setAlignment(Qt.AlignLeft)  # 内部元素左对齐

            initial_enabled = element.get("enabled", True)

            enabled_toggle_btn = QRadioButton('启用')
            enabled_toggle_btn.setChecked(initial_enabled)
            group_inner_layout.addWidget(enabled_toggle_btn)

            if widget_type == "Button":
                name = element.get("name", "未知参数")
                btn = QPushButton(name)
                btn.setEnabled(initial_enabled)
                enabled_toggle_btn.toggled.connect(btn.setEnabled)
                group_inner_layout.addWidget(btn)
                group_inner_layout.addStretch(1)  # 添加伸缩空间，让按钮靠左
                all_widgets_for_preview.append((btn, name))

            elif widget_type == "ComboBox":
                items = element.get("items", [])
                default_index = element.get("default_index", 0)

                combo = QComboBox()
                combo.addItems(items)
                if default_index < len(items) and default_index >= 0:
                    combo.setCurrentIndex(default_index)
                combo.setEnabled(initial_enabled)
                enabled_toggle_btn.toggled.connect(combo.setEnabled)

                group_inner_layout.addWidget(combo)
                group_inner_layout.addStretch(1)  # 添加伸缩空间
                all_widgets_for_preview.append((combo, f"有参参数: {element.get('description')}"))

            elif widget_type == "FileSelectButton":
                initial_path = element.get("initial_path", "")

                file_path_display = QLineEdit(initial_path)
                file_path_display.setReadOnly(True)
                file_path_display.setPlaceholderText("未选择文件")  # 占位符文本
                file_path_display.setEnabled(initial_enabled)

                select_file_btn = QPushButton("选择文件")
                select_file_btn.setEnabled(initial_enabled)

                def open_file_dialog_for_preview():
                    options = QFileDialog.Options()
                    file_name, _ = QFileDialog.getOpenFileName(widget_group, "选择文件",
                                                               file_path_display.text() if file_path_display.text() else "",
                                                               "所有文件 (*);;文本文件 (*.txt)", options=options)
                    if file_name:
                        file_path_display.setText(file_name)

                select_file_btn.clicked.connect(open_file_dialog_for_preview)  # 注意连接的是预览窗口中的函数

                group_inner_layout.addWidget(file_path_display, 1)  # 1代表伸缩因子，让路径显示框占据更多空间
                group_inner_layout.addWidget(select_file_btn)
                all_widgets_for_preview.append((file_path_display, f"文件路径: {element.get('description')}"))

            elif widget_type == "TextInput":
                default_text = element.get("default_text", "")

                text_input_field = QLineEdit(default_text)
                text_input_field.setPlaceholderText("请输入文本")  # 占位符文本
                text_input_field.setEnabled(initial_enabled)
                enabled_toggle_btn.toggled.connect(text_input_field.setEnabled)

                group_inner_layout.addWidget(text_input_field, 1)  # 1代表伸缩因子
                all_widgets_for_preview.append((text_input_field, f"文本输入: {element.get('description')}"))

            # 将QGroupBox添加到目标布局
            target_layout.addWidget(widget_group)
        return all_widgets_for_preview

    def _run_preview_action(self, widgets_info, display_label):
        """
        处理预览窗口中的“运行所有功能”按钮点击事件，显示启用的参数信息。
        此方法也移至Mixin，方便共享。
        """
        enabled_items_info = []
        for widget_instance, name_or_desc in widgets_info:
            if widget_instance.isEnabled():
                if isinstance(widget_instance, QComboBox):
                    enabled_items_info.append(
                        f"{name_or_desc.replace('下拉菜单', '有参参数')} (选中: {widget_instance.currentText()})")
                elif isinstance(widget_instance, QLineEdit) and "文件路径" in name_or_desc:  # 针对文件选择的QLineEdit
                    enabled_items_info.append(
                        f"{name_or_desc} (路径: {widget_instance.text() if widget_instance.text() else '未选择'})")
                elif isinstance(widget_instance, QLineEdit) and "文本输入" in name_or_desc:  # 针对文本输入的QLineEdit
                    enabled_items_info.append(
                        f"{name_or_desc} (内容: {widget_instance.text() if widget_instance.text() else '空'})")
                elif isinstance(widget_instance, QPushButton) and "无参参数" in name_or_desc:  # 针对无参按钮
                    enabled_items_info.append(name_or_desc)
                else:
                    enabled_items_info.append(name_or_desc)

        if enabled_items_info:
            display_label.setText("启用的参数: " + ", ".join(enabled_items_info))
        else:
            display_label.setText("没有启用的参数。")

class LauncherDesigner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 一个示例标签，表示 LauncherDesigner 的内容
        self.title_label = QLabel("启动参数")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px; color: red;")
        self.main_layout.addWidget(self.title_label)

        # 创建一个 QScrollArea 来包裹动态生成的UI元素
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # 允许滚动区域内的widget调整大小以适应

        # 创建一个QWidget作为scroll_area的内部widget
        self.scroll_content_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_content_layout.setAlignment(Qt.AlignTop)  # 确保内容顶部对齐

        self.scroll_area.setWidget(self.scroll_content_widget)
        self.main_layout.addWidget(self.scroll_area)  # 将滚动区域添加到LauncherDesigner的主布局中

        # Label to display preview information
        self.preview_display_label = QLabel("启用的参数: 无")
        self.preview_display_label.setWordWrap(True)
        self.main_layout.addWidget(self.preview_display_label)

        # 保存生成的widgets，以便在运行动作时访问它们
        self.generated_widgets_info = []

    def load_ui_elements(self, ui_elements_data):
        """
        根据提供的UI数据创建并加载UI元素到LauncherDesigner的界面。
        """
        # 清空现有布局中的所有控件，防止重复加载
        while self.scroll_content_layout.count():
            item = self.scroll_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # 如果是嵌套布局，需要递归清理
                self._clear_layout(item.layout())

        self.generated_widgets_info = self._parse_ui_data_and_create_widgets(
            ui_elements_data, self.scroll_content_layout)
        self.run_preview_action() # Update preview after loading elements

    def _clear_layout(self, layout):
        """递归清理布局中的所有控件和子布局"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _parse_ui_data_and_create_widgets(self, ui_elements_data, target_layout):
        """
        从UI元素数据创建并添加相应的QWidgets到给定的布局。
        此方法现在是LauncherDesigner的内部方法，因为它负责创建和管理其UI。
        """
        all_widgets_for_preview = []

        for element in ui_elements_data:
            widget_type = element.get("type")

            if widget_type == "Button":
                name = element.get("name", "未知参数")
                description = element.get("description", "")
                initial_enabled = element.get("enabled", True)

                widget_group = QGroupBox(f"{description}")
                group_inner_layout = QHBoxLayout()
                widget_group.setLayout(group_inner_layout)
                group_inner_layout.setAlignment(Qt.AlignLeft)

                enabled_toggle_btn = QRadioButton('启用')
                enabled_toggle_btn.setChecked(initial_enabled)

                btn = QPushButton(name)
                btn.setEnabled(initial_enabled)
                enabled_toggle_btn.toggled.connect(btn.setEnabled)
                enabled_toggle_btn.toggled.connect(self.run_preview_action) # Connect to update preview

                group_inner_layout.addWidget(enabled_toggle_btn)
                group_inner_layout.addWidget(btn)
                target_layout.addWidget(widget_group)
                all_widgets_for_preview.append((btn, description))

            elif widget_type == "ComboBox":
                description = element.get("description", "未知有参参数")
                items = element.get("items", [])
                default_index = element.get("default_index", 0)
                initial_enabled = element.get("enabled", True)

                widget_group = QGroupBox(f"{description}")
                group_inner_layout = QHBoxLayout()
                widget_group.setLayout(group_inner_layout)
                group_inner_layout.setAlignment(Qt.AlignLeft)

                enabled_toggle_btn = QRadioButton('启用')
                enabled_toggle_btn.setChecked(initial_enabled)

                combo = QComboBox()
                combo.addItems(items)
                if default_index < len(items) and default_index >= 0:
                    combo.setCurrentIndex(default_index)

                combo.setEnabled(initial_enabled)
                enabled_toggle_btn.toggled.connect(combo.setEnabled)
                enabled_toggle_btn.toggled.connect(self.run_preview_action) # Connect to update preview
                combo.currentIndexChanged.connect(self.run_preview_action) # Connect to update preview

                group_inner_layout.addWidget(enabled_toggle_btn)
                group_inner_layout.addWidget(combo)
                target_layout.addWidget(widget_group)
                all_widgets_for_preview.append((combo, f"{description}"))

            elif widget_type == "FileSelectButton":
                description = element.get("description", "未知文件选择")
                initial_path = element.get("initial_path", "")
                initial_enabled = element.get("enabled", True)

                widget_group = QGroupBox(f"{description}")
                group_inner_layout = QHBoxLayout()
                widget_group.setLayout(group_inner_layout)
                group_inner_layout.setAlignment(Qt.AlignLeft)

                enabled_toggle_btn = QRadioButton('启用')
                enabled_toggle_btn.setChecked(initial_enabled)

                file_path_input = QLineEdit(initial_path)
                file_path_input.setPlaceholderText("选择文件路径...")
                file_path_input.setReadOnly(True) # Make it read-only
                file_path_input.setStyleSheet("color: red;")

                select_file_btn = QPushButton("选择文件")
                # 使用lambda捕获file_path_input，确保clicked信号连接到正确的QLineEdit
                select_file_btn.clicked.connect(lambda _, input_field=file_path_input: self._select_file(input_field))

                file_path_input.setEnabled(initial_enabled)
                select_file_btn.setEnabled(initial_enabled)

                enabled_toggle_btn.toggled.connect(file_path_input.setEnabled)
                enabled_toggle_btn.toggled.connect(select_file_btn.setEnabled)
                enabled_toggle_btn.toggled.connect(self.run_preview_action)
                file_path_input.textChanged.connect(self.run_preview_action) # Update preview if path changes

                group_inner_layout.addWidget(enabled_toggle_btn)
                group_inner_layout.addWidget(file_path_input)
                group_inner_layout.addWidget(select_file_btn)
                target_layout.addWidget(widget_group)
                # 将QLineEdit和描述添加到预览列表
                all_widgets_for_preview.append((file_path_input, f"{description}"))

            elif widget_type == "TextInput":
                description = element.get("description", "未知文本输入")
                default_text = element.get("default_text", "")
                initial_enabled = element.get("enabled", True)

                widget_group = QGroupBox(f"{description}")
                group_inner_layout = QHBoxLayout()
                widget_group.setLayout(group_inner_layout)
                group_inner_layout.setAlignment(Qt.AlignLeft)

                enabled_toggle_btn = QRadioButton('启用')
                enabled_toggle_btn.setChecked(initial_enabled)

                text_input = QLineEdit(default_text)
                text_input.setPlaceholderText("请输入参数...")
                text_input.setStyleSheet("color: red;")

                text_input.setEnabled(initial_enabled)
                enabled_toggle_btn.toggled.connect(text_input.setEnabled)
                enabled_toggle_btn.toggled.connect(self.run_preview_action)
                text_input.textChanged.connect(self.run_preview_action) # Update preview on text change

                group_inner_layout.addWidget(enabled_toggle_btn)
                group_inner_layout.addWidget(text_input)
                target_layout.addWidget(widget_group)
                # 将QLineEdit和描述添加到预览列表
                all_widgets_for_preview.append((text_input, f"{description}"))
        return all_widgets_for_preview

    def _select_file(self, file_path_input_widget):
        """Opens a file dialog and sets the selected file path to the QLineEdit."""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path:
            file_path_input_widget.setText(file_path)

    def run_preview_action(self):
        """
        处理LauncherDesigner中的“运行所有功能”按钮点击事件，显示启用的参数信息。
        """
        enabled_items_info = []
        for widget_instance, name_or_desc in self.generated_widgets_info:
            # 检查父QGroupBox中的QRadioButton是否被选中
            parent_group_box = widget_instance.parentWidget()
            if parent_group_box and isinstance(parent_group_box, QGroupBox):
                # 在QGroupBox中查找“启用”QRadioButton
                radio_button_found = False
                for child in parent_group_box.findChildren(QRadioButton):
                    if child.text() == '启用':
                        if child.isChecked():
                            radio_button_found = True
                            break
                if radio_button_found:
                    if isinstance(widget_instance, QComboBox):
                        enabled_items_info.append(
                            f"{name_or_desc} ({widget_instance.currentText()})")
                    elif isinstance(widget_instance, QPushButton):
                        # 对于按钮，我们通常只关心它被启用，其name就是参数本身
                        enabled_items_info.append(widget_instance.text())
                    elif isinstance(widget_instance, QLineEdit): # 对于FileSelectButton和TextInput
                        if widget_instance.text(): # 只有当QLineEdit有文本时才添加
                            enabled_items_info.append(f"{name_or_desc} ({widget_instance.text()})")

        if enabled_items_info:
            self.preview_display_label.setText("启用的参数: " + ", ".join(enabled_items_info))
        else:
            self.preview_display_label.setText("没有启用的参数。")

    def get_selected_parameters(self):
        """
        收集当前选中的参数及其值。
        返回一个适合传递给执行逻辑的字典。
        """
        selected_params = {}
        for widget_instance, original_name in self.generated_widgets_info:
            parent_group_box = widget_instance.parentWidget()
            if parent_group_box and isinstance(parent_group_box, QGroupBox):
                radio_button_found = False
                for child in parent_group_box.findChildren(QRadioButton):
                    if child.text() == '启用' and child.isChecked():
                        radio_button_found = True
                        break
                if radio_button_found:
                    if isinstance(widget_instance, QComboBox):
                        # 对于ComboBox，使用其当前选中的文本
                        # 注意：这里可能需要根据实际命令行参数格式进行调整
                        # 如果需要参数名称+值，则可以是 original_name + " " + widget_instance.currentText()
                        selected_params[widget_instance.currentText()] = True
                    elif isinstance(widget_instance, QPushButton):
                        # 对于Button，使用其按钮文本作为参数
                        selected_params[widget_instance.text()] = True
                    elif isinstance(widget_instance, QLineEdit):
                        # 对于FileSelectButton和TextInput，使用其文本内容
                        if widget_instance.text():
                            selected_params[widget_instance.text()] = True
        return selected_params

if __name__ == '__main__':
    def ReadUiFile():
        # 获取当前文件所在的目录
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 UI.json 的完整路径
        uifile_path = os.path.join(current_script_dir, "../Resources/UI.json")

        try:
            with open(uifile_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content
        except FileNotFoundError:
            QMessageBox.critical(None, "文件未找到", f"配置文件未找到: {uifile_path}\n请确保 'Resources/UI.json' 存在。")
            return None
        except json.JSONDecodeError as e:
            QMessageBox.critical(None, "JSON 解析错误", f"配置文件 'UI.json' 不是有效的JSON格式: {e}")
            return None
        except Exception as e:
            QMessageBox.critical(None, "读取文件失败", f"读取配置文件时发生未知错误: {e}")
            return None


    class MainWindow(QWidget,UItemCreaterWindow):
        def __init__(self):
            super().__init__()
            self.is_python_script = False
            self.is_local_python = True
            self.python_param = ""
            self.initUI()
        def initUI(self):
            # 设置窗口标题
            self.setWindowTitle('启动器')
            # 设置窗口大小
            self.setGeometry(50, 300, 500, 700)
            self.center_on_screen()
            self.setStyleSheet(self.WIDGET_GROUP_STYLE)
            # 创建主布局
            main_layout = QVBoxLayout()

            # 创建 LauncherDesigner 实例并添加到主布局
            self.launcherdesigner = LauncherDesigner(self)
            main_layout.addWidget(self.launcherdesigner)

            run_buttons_layout = QHBoxLayout()

            self.silent_run_button = QPushButton('静默运行')
            # Apply blue style
            self.silent_run_button.setStyleSheet("background-color: #4CAF50; color: white;")
            self.silent_run_button.clicked.connect(self.run_silent)
            run_buttons_layout.addWidget(self.silent_run_button)

            self.terminal_run_button = QPushButton('终端运行')
            # Apply blue style
            self.terminal_run_button.setStyleSheet("background-color: #008CBA; color: white;")
            self.terminal_run_button.clicked.connect(self.run_terminal)
            run_buttons_layout.addWidget(self.terminal_run_button)

            main_layout.addLayout(run_buttons_layout)

            # 设置窗口的主布局
            self.setLayout(main_layout)

            # 读取并加载UI配置
            ui_json_str = ReadUiFile()
            if ui_json_str:
                try:
                    ui_elements_data = json.loads(ui_json_str)
                    self.launcherdesigner.load_ui_elements(ui_elements_data)
                except json.JSONDecodeError as e:
                    QMessageBox.critical(self, "JSON 解析错误", f"配置文件 'UI.json' 不是有效的JSON格式: {e}")
                except Exception as e:
                    QMessageBox.critical(self, "加载UI失败", f"加载UI元素时发生错误: {e}")
            else:
                pass

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
        def get_runcmd(self):
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建 UI.json 的完整路径
            cmd = [os.path.join(current_script_dir, "Callor")] # 假设这是你的可执行文件
            selected_params = self.launcherdesigner.get_selected_parameters()
            if selected_params:
                param_strings = [f"{k}" for k, v in selected_params.items()]
                cmd.append(f"{' '.join(param_strings)}")
            else:
                QMessageBox.information(self, "静默运行", "无参数运行。")
                cmd.append(" ")
            return cmd

        def read_config(self):
            import configparser

            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            resources_path = os.path.join(current_script_dir, "../Resources")
            config_file_path = os.path.join(resources_path, "config.ini")

            config = configparser.ConfigParser()

            # 尝试读取配置文件
            try:
                config.read(config_file_path)
            except configparser.Error as e:
                print(f"Error reading config file: {e}")
                # 可以选择退出程序或采取其他错误处理措施
                return False

            # 检查文件是否成功读取（如果文件不存在或为空，read() 不会报错，但 sections 会是空的）
            if not config.sections():
                print(f"Warning: Config file '{config_file_path}' is empty or does not exist.")
                # 如果文件是空的，你可能需要设置默认值或引导用户
                return False

            if 'script' in config:
                is_python_script = config['script'].getboolean('ispython')
                if is_python_script:
                    self.is_python_script = True
                    python_env_type = config['script'].get('python_env_type')
                    if python_env_type == 'local':
                        self.is_local_python = True
                        self.python_param = config['script'].get('python_executable')
                    elif python_env_type == 'conda':
                        self.is_local_python = False
                        self.python_param = config['script'].get('conda_env_name')
                else:
                    self.is_python_script = False
                    print("Script is not a Python script (no Python environment details).")
            else:
                print("Section [script] not found.")
                return False
            return True

        def run_cmd(self, cmd):
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                return result
            except subprocess.CalledProcessError as e:
                QMessageBox.information(self, "执行出错", f"执行报错\n{e.stderr}")
            except FileNotFoundError:
                QMessageBox.information(self, "执行出错", f"执行异常\n{' '.join(cmd)}")
            return None

        def run_terminal_cmd(self, cmd):
            import shlex
            script_command = ' '.join(cmd)
            # 适用于macOS的AppleScript，用于在终端中运行命令
            apple_script = f'''
                tell application "Terminal"
                    do script "{script_command}"
                    activate
                end tell
                '''
            return self.run_cmd(['osascript', '-e', apple_script])

        def run_cmd_in_conda(self,env_name, cmd):
            """
            在指定的 Conda 环境中运行 Python 脚本。
            Args:
                env_name (str): 要激活的 Conda 环境的名称。
                cmd (list): 要运行的 Python 脚本的路径和参数。
            """
            # 查找 Conda 的初始化脚本
            result = self.run_cmd(['bash', '-c', 'source $HOME/.zshrc && conda info --base'])
            if result is None:
                QMessageBox.information(self, "Conda 启动失败", "无法获取 Conda 基础路径。")
                return None

            conda_base_path = result.stdout.strip()
            conda_sh_path = os.path.join(conda_base_path, 'etc', 'profile.d', 'conda.sh')

            if not os.path.exists(conda_sh_path):
                print(f"Error: conda.sh not found at {conda_sh_path}", file=sys.stderr)
                QMessageBox.information(self, "Conda 启动失败", f"无法读取 conda.sh 文件: {conda_sh_path}")
                return None

            # 构建激活环境和运行脚本的命令
            # 注意：cmd[0] 是脚本路径，cmd[1]是参数字符串
            command_str = f"source {conda_sh_path} && conda activate {env_name} && python {cmd[0]} {cmd[1]}"
            command = ['bash', '-c', command_str]
            return self.run_cmd(command)

        def run_terminal_in_conda(self, env_name, cmd):
            """
            在指定的 Conda 环境的终端中运行 Python 脚本。
            Args:
                env_name (str): 要激活的 Conda 环境的名称。
                cmd (list): 要运行的 Python 脚本的路径和参数。
            """
            result = self.run_cmd(['bash', '-c', 'source $HOME/.zshrc && conda info --base'])
            if result is None:
                QMessageBox.information(self, "Conda 启动失败", "无法获取 Conda 基础路径。")
                return None

            conda_base_path = result.stdout.strip()
            conda_sh_path = os.path.join(conda_base_path, 'etc', 'profile.d', 'conda.sh')

            if not os.path.exists(conda_sh_path):
                print(f"Error: conda.sh not found at {conda_sh_path}", file=sys.stderr)
                QMessageBox.information(self, "Conda 启动失败", f"无法读取 conda.sh 文件: {conda_sh_path}")
                return None

            # 构建在终端中运行的 AppleScript 命令
            command_str = f"source {conda_sh_path} && conda activate {env_name} && python {cmd[0]} {cmd[1]}"
            # 将整个命令字符串作为 do script 的参数传递
            apple_script = f'''
                tell application "Terminal"
                    do script "{command_str}"
                    activate
                end tell
            '''
            return self.run_cmd(['osascript', '-e', apple_script])


        def run_silent(self):
            """
            处理“静默运行”按钮点击事件
            收集启用的参数并执行相应逻辑
            """
            cmd = self.get_runcmd()
            if self.read_config() is False:
                QMessageBox.information(self, "文件损坏", "无法读取配置文件。")
                return

            if self.is_python_script:
                if self.is_local_python:
                    sub_run = [self.python_param, cmd[0], cmd[1]]
                    result = self.run_cmd(sub_run)
                    if result is not None:
                        QMessageBox.information(self, "执行完成", f"执行结果:\n{result.stdout}")
                else:
                    result = self.run_cmd_in_conda(self.python_param, cmd)
                    if result is not None:
                        QMessageBox.information(self, "执行完成", f"执行结果:\n{result.stdout}")
            else:
                # 对于非Python脚本，直接运行 cmd
                sub_run = ["bash", "-c", ' '.join(cmd)]
                result = self.run_cmd(sub_run)
                if result is not None:
                    QMessageBox.information(self, "执行完成", f"执行结果:\n{result.stdout}")

        def run_terminal(self):
            """
            处理“终端运行”按钮点击事件
            收集启用的参数并执行相应逻辑
            """
            cmd = self.get_runcmd()
            if self.read_config() is False:
                QMessageBox.information(self, "文件损坏", "无法读取配置文件。")
                return

            if self.is_python_script:
                if self.is_local_python:
                    sub_run = [self.python_param, cmd[0], cmd[1]]
                    self.run_terminal_cmd(sub_run)
                else:
                    self.run_terminal_in_conda(self.python_param, cmd)
            else:
                # 对于非Python脚本，直接在终端中运行
                # 如此复杂的表达式是为了将“”穿透到终端，执行传递到bash -c "xxx"
                sub_run = ["bash", "-c", f"\\\"{' '.join(cmd)}\\\""] # 使用 -c 确保命令被正确解释
                self.run_terminal_cmd(sub_run)

    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())