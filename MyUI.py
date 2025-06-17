# MyUI.py 文件内容

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QGroupBox, QLabel, QRadioButton, QMessageBox, QFileDialog,
    QLineEdit, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QSize


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
            margin-top: 10px; /* 顶部外边距 */
            padding-top: 15px; /* 内部上边距，为标题留出空间 */
            padding-left: 10px;
            padding-right: 10px;
            padding-bottom: 10px;
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

            initial_enabled = element.get("initial_enabled", True)

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
            # display_label 依然可以设置其颜色，因为它是状态显示，需要突出
            display_label.setText("启用的参数: " + ", ".join(enabled_items_info))
        else:
            display_label.setText("没有启用的参数。")