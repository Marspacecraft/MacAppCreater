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


# --- UiBuilderMixin 基类 (更正: 不再继承 QDialog) ---
class UItemCreaterWindow: # <--- 这里移除了 QDialog 继承
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

            if widget_type == "Button":
                name = element.get("name", "未知参数")
                description = element.get("description", "")
                initial_enabled = element.get("initial_enabled", True)

                widget_group = QGroupBox(f"{description}")
                group_inner_layout = QHBoxLayout()
                widget_group.setLayout(group_inner_layout)
                group_inner_layout.setAlignment(Qt.AlignLeft)

                enabled_toggle_btn = QRadioButton('启用')
                enabled_toggle_btn.setChecked(initial_enabled)

                btn = QPushButton(name)
                btn.setEnabled(initial_enabled)
                enabled_toggle_btn.toggled.connect(btn.setEnabled)

                group_inner_layout.addWidget(enabled_toggle_btn)
                group_inner_layout.addWidget(btn)
                target_layout.addWidget(widget_group)
                all_widgets_for_preview.append((btn, name))

            elif widget_type == "ComboBox":
                description = element.get("description", "未知有参参数")
                items = element.get("items", [])
                default_index = element.get("default_index", 0)
                initial_enabled = element.get("initial_enabled", True) # 这个initial_enabled变量在这个作用域内是局部变量，不是问题所在

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

                combo.setEnabled(initial_enabled) # 这里也是对的，因为上面已经定义了initial_enabled
                enabled_toggle_btn.toggled.connect(combo.setEnabled)

                group_inner_layout.addWidget(enabled_toggle_btn)
                group_inner_layout.addWidget(combo)
                target_layout.addWidget(widget_group)
                all_widgets_for_preview.append((combo, f"有参参数: {description}"))
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
                    enabled_items_info.append(f"{name_or_desc.replace('下拉菜单', '有参参数')} (选中: {widget_instance.currentText()})")
                else:
                    enabled_items_info.append(name_or_desc)

        if enabled_items_info:
            display_label.setText("启用的参数: " + ", ".join(enabled_items_info))
        else:
            display_label.setText("没有启用的参数。")