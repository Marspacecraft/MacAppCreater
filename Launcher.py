# Launcher.py文件
import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QGroupBox, QLabel, QRadioButton, QMessageBox, QFileDialog,
    QLineEdit, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QSize
# 从 MyUI.py 导入所需的类
from MyUI import UItemCreaterWindow, ComboConfigDialog, ButtonConfigDialog, FileSelectConfigDialog, \
    TextInputConfigDialog


# --- LauncherDesigner 类 (现在继承 UiBuilderMixin) ---
class LauncherDesigner(QWidget, UItemCreaterWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 应用通用样式
        self.setStyleSheet(self.WIDGET_GROUP_STYLE)

        self.main_v_layout = QVBoxLayout()
        self.setLayout(self.main_v_layout)

        self.top_h_layout = QHBoxLayout()

        self.controls_group_box = QGroupBox('参数命令启动器UI编辑')
        self.controls_v_layout = QVBoxLayout()
        self.controls_group_box.setLayout(self.controls_v_layout)

        # 应用局部样式到 controls_group_box，可以覆盖通用样式
        self.controls_group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #a0a0a0;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 15px;
                padding-left: 5px;
                padding-right: 5px;
                padding-bottom: 5px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                /* color: #222222; */ /* 移除标题颜色 */
                border-radius: 3px;
            }
            QPushButton {
                min-height: 25px; /* 统一按钮高度 */
            }
        """)

        self.enable_widgets_radio = QRadioButton('开启启动器功能')
        self.enable_widgets_radio.setChecked(False)
        self.enable_widgets_radio.toggled.connect(self.toggle_full_capability)
        self.controls_v_layout.addWidget(self.enable_widgets_radio)

        self.add_btn = QPushButton('添加无参参数')
        self.add_btn.clicked.connect(lambda: self.add_widget('button'))
        self.controls_v_layout.addWidget(self.add_btn)

        self.add_combo = QPushButton('添加有参参数')
        self.add_combo.clicked.connect(lambda: self.add_widget('combo'))
        self.controls_v_layout.addWidget(self.add_combo)

        # --- 新增：添加文件选择按钮 ---
        self.add_file_select_btn = QPushButton('添加文件参数')
        self.add_file_select_btn.clicked.connect(lambda: self.add_widget('file_select'))
        self.controls_v_layout.addWidget(self.add_file_select_btn)

        # --- 新增：添加文本输入参数按钮 ---
        self.add_text_input_btn = QPushButton('添加文本参数')
        self.add_text_input_btn.clicked.connect(lambda: self.add_widget('text_input'))
        self.controls_v_layout.addWidget(self.add_text_input_btn)

        self.generate_ui_desc_btn = QPushButton('导出UI描述文件')
        self.generate_ui_desc_btn.clicked.connect(self.generate_ui_description_file)
        self.controls_v_layout.addWidget(self.generate_ui_desc_btn)

        self.show_current_ui_btn = QPushButton('显示当前UI描述')
        self.show_current_ui_btn.clicked.connect(self.show_current_ui)
        self.controls_v_layout.addWidget(self.show_current_ui_btn)

        self.controls_v_layout.addStretch()

        self.top_h_layout.addWidget(self.controls_group_box)

        self.design_area = QGroupBox('生成窗口区')
        self.design_layout = QVBoxLayout()
        self.design_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.design_area.setLayout(self.design_layout)
        # 为 design_area 设置样式，确保内部的 QGroupBox 组件有合适的空间
        self.design_area.setStyleSheet("""
            QGroupBox {
                border: 1px dashed #cccccc; /* 虚线边框 */
                border-radius: 5px;
                margin-top: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                /* color: #555555; */ /* 移除标题颜色 */
            }
        """)
        self.top_h_layout.addWidget(self.design_area)

        self.main_v_layout.addLayout(self.top_h_layout)

        self._set_main_sections_enabled_state(self.enable_widgets_radio.isChecked())
        self.preview_window = None

    def _set_main_sections_enabled_state(self, enabled):
        """
        控制 LauncherDesigner 组件的整体启用/禁用状态。
        """
        self.controls_group_box.setEnabled(enabled)
        self.design_area.setEnabled(enabled)
        self.toggle_full_capability(self.enable_widgets_radio.isChecked())

    def toggle_full_capability(self, enabled):
        """
        切换“添加无参参数”、“添加有参参数”、“导出UI描述文件”和“显示当前UI描述”按钮的启用状态，
        以及整个“生成窗口区”组框的启用状态。
        此方法由“开启启动器功能”单选按钮控制。
        """
        self.add_btn.setEnabled(enabled)
        self.add_combo.setEnabled(enabled)
        self.add_file_select_btn.setEnabled(enabled)
        self.add_text_input_btn.setEnabled(enabled)
        self.generate_ui_desc_btn.setEnabled(enabled)
        self.show_current_ui_btn.setEnabled(enabled)
        self.design_area.setEnabled(enabled)

    def set_designer_enabled(self, enabled: bool):
        """
        设置 LauncherDesigner 组件的启用或禁用状态。
        此方法会直接控制 _set_main_sections_enabled_state。
        """
        self.enable_widgets_radio.setChecked(enabled)
        self._set_main_sections_enabled_state(enabled)

    def is_designer_enabled(self) -> bool:
        """
        查询 LauncherDesigner 组件的整体启用状态（即其主功能控制组的状态）。
        返回 True 如果设计器被启用，否则返回 False。
        """
        return self.controls_group_box.isEnabled()

    def is_enable_widgets_radio_checked(self) -> bool:
        """
        查询“开启启动器功能”单选按钮的选中状态。
        返回 True 如果单选按钮被选中，否则返回 False。
        """
        return self.enable_widgets_radio.isChecked()

    def set_enable_widgets_radio_state(self, state: bool):
        """
        设置“开启启动器功能”单选按钮的选中状态。
        当此单选按钮的状态改变时，会触发 toggle_full_capability 来更新其控制的控件。
        """
        self.enable_widgets_radio.setChecked(state)

    def add_widget(self, widget_type):
        # 统一处理 QGroupBox 的创建和样式应用
        def create_styled_group_box(description, initial_enabled, widget_property_dict):
            widget_group = QGroupBox(f"{description}")
            widget_group.setStyleSheet(self.WIDGET_GROUP_STYLE)  # 应用通用样式
            widget_group.setMinimumWidth(350)  # 设置最小宽度
            widget_group.setMaximumWidth(500)  # 可以设置最大宽度

            group_inner_layout = QHBoxLayout()
            widget_group.setLayout(group_inner_layout)
            group_inner_layout.setAlignment(Qt.AlignLeft)

            enabled_toggle_btn = QRadioButton('启用')
            enabled_toggle_btn.setChecked(initial_enabled)
            group_inner_layout.addWidget(enabled_toggle_btn)

            for key, value in widget_property_dict.items():
                widget_group.setProperty(key, value)

            return widget_group, group_inner_layout, enabled_toggle_btn

        if widget_type == 'button':
            dialog = ButtonConfigDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                config = dialog.get_config()

                if not config["name"].strip():
                    QMessageBox.warning(self, "无效参数", "无参参数的名称不能为空。")
                    return

                widget_property_dict = {
                    "widget_type": "ConfigurableButton",
                    "button_name": config["name"],
                    "description_text": config["description"],
                    "initial_enabled": config["enabled"]
                }
                widget_group, group_inner_layout, enabled_toggle_btn = create_styled_group_box(
                    config["description"], config["enabled"], widget_property_dict
                )

                btn = QPushButton(config["name"])
                btn.setEnabled(config["enabled"])
                enabled_toggle_btn.toggled.connect(btn.setEnabled)

                group_inner_layout.addWidget(btn)
                group_inner_layout.addStretch(1)  # 增加伸缩空间，使按钮左对齐
                self.design_layout.addWidget(widget_group)

        elif widget_type == 'combo':
            dialog = ComboConfigDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                config = dialog.get_config()

                if not config["items"]:
                    QMessageBox.warning(self, "无效参数", "有参参数必须至少包含一个参数内容。")
                    return

                widget_property_dict = {
                    "widget_type": "ConfigurableComboBox",
                    "combo_items": config["items"],
                    "default_index": config["default_index"],
                    "description_text": config["description"],
                    "initial_enabled": config["enabled"]
                }
                widget_group, group_inner_layout, enabled_toggle_btn = create_styled_group_box(
                    config["description"], config["enabled"], widget_property_dict
                )

                combo = QComboBox()
                combo.addItems(config["items"])
                if config["default_index"] < len(config["items"]) and config["default_index"] >= 0:
                    combo.setCurrentIndex(config["default_index"])

                combo.setEnabled(config["enabled"])
                enabled_toggle_btn.toggled.connect(combo.setEnabled)

                group_inner_layout.addWidget(combo)
                group_inner_layout.addStretch(1)
                self.design_layout.addWidget(widget_group)

        # --- 新增：处理文件选择按钮的添加逻辑 ---
        elif widget_type == 'file_select':
            dialog = FileSelectConfigDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                config = dialog.get_config()

                if not config["description"].strip():
                    QMessageBox.warning(self, "无效参数", "文件选择参数的说明不能为空。")
                    return

                widget_property_dict = {
                    "widget_type": "ConfigurableFileSelect",
                    "description_text": config["description"],
                    "initial_path": config["initial_path"],
                    "initial_enabled": config["enabled"]
                }
                widget_group, group_inner_layout, enabled_toggle_btn = create_styled_group_box(
                    config["description"], config["enabled"], widget_property_dict
                )

                file_path_display = QLineEdit(config["initial_path"])
                file_path_display.setReadOnly(True)
                file_path_display.setPlaceholderText("未选择文件")
                file_path_display.setEnabled(config["enabled"])

                select_file_btn = QPushButton("选择文件")
                select_file_btn.setEnabled(config["enabled"])

                def open_file_dialog():
                    options = QFileDialog.Options()
                    file_name, _ = QFileDialog.getOpenFileName(self, "选择文件",
                                                               file_path_display.text() if file_path_display.text() else "",
                                                               "所有文件 (*);;文本文件 (*.txt)", options=options)
                    if file_name:
                        file_path_display.setText(file_name)

                select_file_btn.clicked.connect(open_file_dialog)
                enabled_toggle_btn.toggled.connect(file_path_display.setEnabled)
                enabled_toggle_btn.toggled.connect(select_file_btn.setEnabled)

                group_inner_layout.addWidget(file_path_display, 1)  # 伸缩因子
                group_inner_layout.addWidget(select_file_btn)
                self.design_layout.addWidget(widget_group)

        # --- 新增：处理文本输入参数的添加逻辑 ---
        elif widget_type == 'text_input':
            dialog = TextInputConfigDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                config = dialog.get_config()

                if not config["description"].strip():
                    QMessageBox.warning(self, "无效参数", "文本输入参数的说明不能为空。")
                    return

                widget_property_dict = {
                    "widget_type": "ConfigurableTextInput",
                    "description_text": config["description"],
                    "default_text": config["default_text"],
                    "initial_enabled": config["enabled"]
                }
                widget_group, group_inner_layout, enabled_toggle_btn = create_styled_group_box(
                    config["description"], config["enabled"], widget_property_dict
                )

                text_input_field = QLineEdit(config["default_text"])
                text_input_field.setPlaceholderText("请输入文本")
                text_input_field.setEnabled(config["enabled"])
                enabled_toggle_btn.toggled.connect(text_input_field.setEnabled)

                group_inner_layout.addWidget(text_input_field, 1)  # 伸缩因子
                self.design_layout.addWidget(widget_group)

    def _collect_ui_elements_data(self):
        """
        辅助方法：从 design_layout 收集所有UI元素的属性数据。
        """
        ui_elements_data = []
        for i in range(self.design_layout.count()):
            item = self.design_layout.itemAt(i)
            if item is None:
                continue

            widget_group = item.widget()
            if widget_group is None:
                continue

            widget_type = widget_group.property("widget_type")
            if widget_type == "ConfigurableButton":
                ui_elements_data.append({
                    "type": "Button",
                    "name": widget_group.property("button_name"),
                    "description": widget_group.property("description_text"),
                    "initial_enabled": widget_group.property("initial_enabled")
                })
            elif widget_type == "ConfigurableComboBox":
                ui_elements_data.append({
                    "type": "ComboBox",
                    "description": widget_group.property("description_text"),
                    "items": widget_group.property("combo_items"),
                    "default_index": widget_group.property("default_index"),
                    "initial_enabled": widget_group.property("initial_enabled")
                })
            # --- 新增：收集文件选择按钮的数据 ---
            elif widget_type == "ConfigurableFileSelect":
                ui_elements_data.append({
                    "type": "FileSelectButton",
                    "description": widget_group.property("description_text"),
                    "initial_path": widget_group.property("initial_path"),
                    "initial_enabled": widget_group.property("initial_enabled")
                })
            # --- 新增：收集文本输入框的数据 ---
            elif widget_type == "ConfigurableTextInput":
                ui_elements_data.append({
                    "type": "TextInput",
                    "description": widget_group.property("description_text"),
                    "default_text": widget_group.property("default_text"),
                    "initial_enabled": widget_group.property("initial_enabled")
                })
        return ui_elements_data

    def get_ui_description_data(self):
        """
        获取当前“生成窗口区”的UI描述数据。
        返回一个列表，其中包含字典，每个字典描述一个UI元素及其属性。
        """
        return json.dumps(self._collect_ui_elements_data(), indent=2, ensure_ascii=False)

    def generate_ui_description_file(self):
        ui_description = self._collect_ui_elements_data()

        if not ui_description:
            QMessageBox.information(self, "无UI元素", "生成窗口区中没有可描述的UI元素。")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存UI描述文件",
                                                   "ui_description.json",
                                                   "JSON Files (*.json);;所有文件 (*)",
                                                   options=options)

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(ui_description, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "保存成功", f"UI描述文件已成功保存到：\n{os.path.abspath(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存UI描述文件时发生错误：\n{e}")
        else:
            QMessageBox.information(self, "保存取消", "UI描述文件保存操作已取消。")

    def show_current_ui(self):
        ui_elements_data = self._collect_ui_elements_data()

        if not ui_elements_data:
            QMessageBox.information(self, "无UI元素", "生成窗口区中没有可显示的UI元素。请先添加参数。")
            return

        if self.preview_window is not None:
            self.preview_window.close()
            self.preview_window = None

        self.preview_window = QWidget()
        self.preview_window.setWindowTitle('当前UI预览')
        preview_layout = QVBoxLayout()
        self.preview_window.setLayout(preview_layout)

        action_display_label = QLabel('点击运行按钮查看启用项')
        # 移除了这里的特定颜色设置，让它继承默认样式
        # action_display_label.setStyleSheet("font-weight: bold; color: blue;")
        action_display_label.setStyleSheet("font-weight: bold;")  # 仅保留粗体
        preview_layout.addWidget(action_display_label)

        # Calling the method inherited from UiBuilderMixin
        all_widgets_for_preview = self._parse_ui_elements_data_and_create_widgets(ui_elements_data, preview_layout)

        run_all_button = QPushButton('运行所有功能')
        run_all_button.clicked.connect(lambda: self._run_preview_action(all_widgets_for_preview, action_display_label))
        preview_layout.addWidget(run_all_button)

        self.preview_window.show()


# --- 新的 MainWindow 类，作为顶层窗口来容纳 Designer 组件 ---
class MainWindow(QWidget, UItemCreaterWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('我的主应用程序 - 参数命令集成')
        self.setGeometry(100, 100, 1000, 700)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        top_label = QLabel("欢迎使用我的集成应用程序！")
        top_label.setAlignment(Qt.AlignCenter)
        # 移除了这里的特定颜色设置
        top_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(top_label)

        self.designer_component = LauncherDesigner(self)
        main_layout.addWidget(self.designer_component)

        control_designer_layout = QHBoxLayout()
        self.enable_designer_btn = QPushButton("启用设计器")
        self.enable_designer_btn.clicked.connect(self._on_enable_designer)
        control_designer_layout.addWidget(self.enable_designer_btn)

        self.disable_designer_btn = QPushButton("禁用设计器")
        self.disable_designer_btn.clicked.connect(self._on_disable_designer)
        control_designer_layout.addWidget(self.disable_designer_btn)

        self.query_designer_state_btn = QPushButton("查询单选按钮状态")
        self.query_designer_state_btn.clicked.connect(self._on_query_enable_radio_state)
        control_designer_layout.addWidget(self.query_designer_state_btn)
        main_layout.addLayout(control_designer_layout)

        control_radio_layout = QHBoxLayout()
        self.check_radio_btn = QPushButton("选中‘开启启动器功能’")
        self.check_radio_btn.clicked.connect(lambda: self._on_set_radio_state(True))
        control_radio_layout.addWidget(self.check_radio_btn)

        self.uncheck_radio_btn = QPushButton("取消选中‘开启启动器功能’")
        self.uncheck_radio_btn.clicked.connect(lambda: self._on_set_radio_state(False))
        control_radio_layout.addWidget(self.uncheck_radio_btn)
        main_layout.addLayout(control_radio_layout)

        self.get_designer_data_btn = QPushButton("获取设计器UI数据")
        self.get_designer_data_btn.clicked.connect(self._on_get_designer_data)
        main_layout.addWidget(self.get_designer_data_btn)

        self.load_ui_file_btn = QPushButton("从文件加载UI并显示")
        self.load_ui_file_btn.clicked.connect(self._on_load_ui_from_file)
        main_layout.addWidget(self.load_ui_file_btn)

        bottom_label = QLabel("这是主窗口的底部区域。")
        bottom_label.setAlignment(Qt.AlignRight)
        # 移除了这里的特定颜色设置
        main_layout.addWidget(bottom_label)

    def _on_enable_designer(self):
        self.designer_component.set_designer_enabled(True)
        QMessageBox.information(self, "状态", "设计器已启用。")

    def _on_disable_designer(self):
        self.designer_component.set_designer_enabled(False)
        QMessageBox.information(self, "状态", "设计器已禁用。")

    def _on_query_enable_radio_state(self):
        is_checked = self.designer_component.is_enable_widgets_radio_checked()
        status_text = "选中" if is_checked else "未选中"
        QMessageBox.information(self, "单选按钮状态", f"‘开启启动器功能’单选按钮当前状态：{status_text}")

    def _on_set_radio_state(self, state: bool):
        self.designer_component.set_enable_widgets_radio_state(state)
        action_text = "选中" if state else "取消选中"
        QMessageBox.information(self, "单选按钮状态", f"‘开启启动器功能’单选按钮已{action_text}。")

    def _on_get_designer_data(self):
        ui_data = self.designer_component.get_ui_description_data()
        if ui_data:
            QMessageBox.information(self, "设计器UI数据",
                                    f"已从设计器获取到UI元素：\n{json.dumps(json.loads(ui_data), indent=2, ensure_ascii=False)}")
        else:
            QMessageBox.information(self, "设计器UI数据", "设计器中当前没有UI元素数据。")

    def _on_load_ui_from_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择UI描述文件", "",
                                                   "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    ui_data = json.load(f)

                loaded_ui_window = QWidget()
                loaded_ui_window.setWindowTitle("加载的UI预览")
                loaded_ui_layout = QVBoxLayout()
                loaded_ui_window.setLayout(loaded_ui_layout)

                action_display_label = QLabel('点击运行按钮查看启用项')
                # 移除了这里的特定颜色设置
                # action_display_label.setStyleSheet("font-weight: bold; color: green;")
                action_display_label.setStyleSheet("font-weight: bold;")  # 仅保留粗体
                loaded_ui_layout.addWidget(action_display_label)

                # Calling the method inherited from UiBuilderMixin
                all_widgets_for_preview = self._parse_ui_elements_data_and_create_widgets(ui_data, loaded_ui_layout)

                run_all_button = QPushButton('运行所有功能')
                # Reuse the _run_preview_action logic from UiBuilderMixin
                run_all_button.clicked.connect(
                    lambda: self._run_preview_action(all_widgets_for_preview, action_display_label))
                loaded_ui_layout.addWidget(run_all_button)

                loaded_ui_window.show()
                QMessageBox.information(self, "加载成功", f"UI描述文件已成功加载并显示：\n{os.path.abspath(file_path)}")

            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "加载失败", f"文件不是有效的JSON格式：\n{e}")
            except Exception as e:
                QMessageBox.critical(self, "加载失败", f"加载UI描述文件时发生错误：\n{e}")
        else:
            QMessageBox.information(self, "加载取消", "UI描述文件加载操作已取消。")


# --- 主应用类，封装整个应用程序的启动逻辑 ---
class PyQtUIDesignerApp:
    def __init__(self):
        self._app = None
        self._main_window = None

    def run(self):
        if QApplication.instance():
            self._app = QApplication.instance()
        else:
            self._app = QApplication(sys.argv)

        self._main_window = MainWindow()
        self._main_window.show()
        sys.exit(self._app.exec_())


# --- 如果 app_core.py 自身作为主程序运行，提供直接启动的入口 ---
if __name__ == '__main__':
    app_instance = PyQtUIDesignerApp()
    app_instance.run()