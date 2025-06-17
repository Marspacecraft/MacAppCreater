import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFileDialog, QWidget, QApplication, QGroupBox, QRadioButton,
    QComboBox, QListWidget, QListWidgetItem, QDialogButtonBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import subprocess
import json
import os
from PIL import Image
import configparser
import shutil

# def makeCaller():
#     cpp_source_file = "Caller/Caller.cpp"
#     executable_name = "Caller/Caller"  # 生成的可执行文件名称
#
#     if os.path.exists(executable_name):
#         return executable_name
#
#     compile_command = [
#         "g++",
#         cpp_source_file,
#         "-I/opt/homebrew/include",
#         "-L/opt/homebrew/lib",
#         "-lboost_system",
#         "-o",
#         executable_name
#     ]
#
#     try:
#         print(f"正在编译 {cpp_source_file}...")
#         # `check=True` 表示如果命令返回非零退出码（即出错），会抛出 CalledProcessError
#         # `capture_output=True` 捕获标准输出和标准错误
#         # `text=True` 将输出解码为文本（字符串）
#         compile_result = subprocess.run(compile_command, check=True, capture_output=True, text=True)
#         print("编译成功！")
#         return executable_name
#
#     except subprocess.CalledProcessError as e:
#         print(f"编译或执行过程中发生错误: {e}")
#         print("命令的退出码:", e.returncode)
#         print("标准输出:\n", e.stdout)
#         print("标准错误:\n", e.stderr)
#
#     except FileNotFoundError:
#         print("错误: 找不到编译器或可执行文件。请确保 g++ (或你选择的编译器) 已安装并配置到 PATH 环境变量中。")
#     return ""

# Minimal UItemCreaterWindow for demonstration if MyUI.py is not present
try:
    from MyUI import UItemCreaterWindow, ButtonConfigDialog, ComboConfigDialog
except ImportError:
    print("MyUI.py not found. Using a minimal UItemCreaterWindow for demonstration.")
    class UItemCreaterWindow:
        def _parse_ui_elements_data_and_create_widgets(self, ui_elements_data, layout):
            generated_widgets = []
            for item_data in ui_elements_data:
                item_type = item_data.get("type")
                description = item_data.get("description", "No description")
                if item_type == "Button":
                    btn = QPushButton(description)
                    layout.addWidget(btn)
                    generated_widgets.append(btn)
                elif item_type == "ComboBox":
                    combo = QComboBox()
                    combo.addItems(item_data.get("items", []))
                    combo.setCurrentIndex(item_data.get("default_index", 0))
                    layout.addWidget(QLabel(description))
                    layout.addWidget(combo)
                    generated_widgets.append(combo)
                # Add other types as needed by your actual MyUI.py
            return generated_widgets
    class ButtonConfigDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Button Config (Dummy)")
            self.setLayout(QVBoxLayout())
            self.layout().addWidget(QLabel("Dummy Button Config"))
            self.layout().addWidget(QPushButton("OK"))
    class ComboConfigDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("ComboBox Config (Dummy)")
            self.setLayout(QVBoxLayout())
            self.layout().addWidget(QLabel("Dummy ComboBox Config"))
            self.layout().addWidget(QPushButton("OK"))


class AppCreaterWindow(QDialog, UItemCreaterWindow):
    """
    A standalone QDialog window to display an executable file, an image, and JSON data.
    Now, JSON data will be parsed to create UI controls, and the window will be self-adjusting.
    """

    def __init__(self, parent=None, executable_path=None, image_path=None, json_data=None):
        """
        Initializes the custom content window.

        Args:
            parent (QWidget, optional): The parent widget.
            executable_path (str, optional): Path to the executable file.
            image_path (str, optional): Path to the image file.
            json_data (dict or str, optional): JSON data, expected to be a list of UI element descriptions.
        """
        super().__init__(parent)

        self.setWindowTitle("App设置及生成")
        # 移除或注释掉下一行，让窗口大小自适应
        # self.setGeometry(200, 200, 600, 700) # Increased height to accommodate UI controls

        self.executable_path = executable_path
        self.image_path = image_path
        self.json_data = json_data

        # Add instance variable to store run mode
        self.run_in_terminal = True # Default to terminal run

        self._create_widgets()

        # 调用 adjustSize() 方法，在所有控件和布局都设置好后，
        # 让窗口根据内容的最佳大小提示进行调整。
        self.adjustSize()

    def _create_runmode_widgets(self,main_layout):
        # --- Add Run Mode Selection when no JSON data is provided ---
        run_mode_group_box = QGroupBox("运行模式")
        run_mode_group_box.setStyleSheet("font-size: 14px; font-weight: bold;")
        run_mode_layout = QHBoxLayout()
        run_mode_group_box.setLayout(run_mode_layout)

        self.terminal_run_radio = QRadioButton("终端运行")
        self.silent_run_radio = QRadioButton("静默运行")

        # Set default and connect signals
        self.terminal_run_radio.setChecked(True)  # Default to terminal run
        self.terminal_run_radio.toggled.connect(self._update_run_mode)
        self.silent_run_radio.toggled.connect(self._update_run_mode)

        run_mode_layout.addWidget(self.terminal_run_radio)
        run_mode_layout.addWidget(self.silent_run_radio)
        run_mode_layout.addStretch(1)  # Push buttons to the left

        main_layout.addWidget(run_mode_group_box)

    def _create_widgets(self):
        """
        Creates and arranges the widgets within the window.
        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # App程序名设置 with optional image
        app_name_group_layout = QHBoxLayout()

        # Check if image path exists and is valid
        if self.image_path and os.path.exists(self.image_path):
            try:
                pixmap = QPixmap(self.image_path)
                if not pixmap.isNull():
                    image_label = QLabel()
                    image_label.setPixmap(
                        pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Scale image
                    app_name_group_layout.addWidget(image_label)
            except Exception as e:
                print(f"Error loading image: {e}")
                # Fallback to no image if loading fails
                pass

        app_name_label = QLabel("<b>App 程序名称:</b>")
        app_name_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        app_name_group_layout.addWidget(app_name_label)
        self.app_name_edit = QLineEdit()
        self.app_name_edit.setPlaceholderText("请输入 App 程序名称")
        self.app_name_edit.editingFinished.connect(self._set_app_name_read_only)
        app_name_group_layout.addWidget(self.app_name_edit)
        main_layout.addLayout(app_name_group_layout)

        # 显示脚本路径
        exe_layout = QHBoxLayout()
        exe_label = QLabel(f"<b>可执行文件:</b> {self.executable_path}")
        exe_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        exe_layout.addWidget(exe_label)
        main_layout.addLayout(exe_layout)

        # --- Python Environment Selection ---
        if self.executable_path and self.executable_path.lower().endswith(".py"):
            python_env_group_box = QGroupBox("Python 环境选择")
            python_env_group_box.setStyleSheet("font-size: 14px; font-weight: bold;")
            python_env_layout = QVBoxLayout()
            python_env_group_box.setLayout(python_env_layout)

            radio_button_layout = QHBoxLayout()
            self.local_python_radio = QRadioButton("本地 Python")
            self.conda_radio = QRadioButton("Conda")
            radio_button_layout.addWidget(self.local_python_radio)
            radio_button_layout.addWidget(self.conda_radio)
            radio_button_layout.addStretch(1) # Push buttons to the left
            python_env_layout.addLayout(radio_button_layout)

            # Local Python ComboBox
            self.local_python_combo = QComboBox()
            self._populate_local_python_paths()
            python_env_layout.addWidget(self.local_python_combo)

            # Conda ComboBox
            self.conda_env_combo = QComboBox()
            self._populate_conda_environments()
            python_env_layout.addWidget(self.conda_env_combo)

            # Connect radio buttons to update combobox visibility
            self.local_python_radio.toggled.connect(self._update_python_env_visibility)
            self.conda_radio.toggled.connect(self._update_python_env_visibility)

            # Set initial selection and visibility
            self.local_python_radio.setChecked(True) # Default to Local Python

            main_layout.addWidget(python_env_group_box)

        # --- UI Controls Section ---
        self.generated_ui_widgets = []
        if self.json_data and self.json_data != '[]':
            # 选择启动器的python

            # 显示UI编辑界面
            ui_controls_group_box = QGroupBox("配置参数")
            # ui_controls_group_box.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
            self.ui_controls_layout = QVBoxLayout()
            ui_controls_group_box.setLayout(self.ui_controls_layout)


            ui_elements_data_to_parse = self.json_data
            if isinstance(self.json_data, str):
                try:
                    ui_elements_data_to_parse = json.loads(self.json_data)
                except json.JSONDecodeError as e:
                    QMessageBox.critical(self, "JSON 解析错误", f"无法解析 UI 元素 JSON 数据: {e}")
                    ui_elements_data_to_parse = []

            if isinstance(ui_elements_data_to_parse, list):
                self.generated_ui_widgets = self._parse_ui_elements_data_and_create_widgets(
                    ui_elements_data_to_parse,
                    self.ui_controls_layout
                )
                main_layout.addWidget(ui_controls_group_box)
            else:
                self._create_runmode_widgets(main_layout)

        else:
            self._create_runmode_widgets(main_layout)


        # --- Generate Button ---
        generate_button = QPushButton("生成App")
        generate_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        generate_button.clicked.connect(self._create_app)
        main_layout.addWidget(generate_button)


    def _set_app_name_read_only(self):
        """
        Sets the application name QLineEdit to read-only after editing is finished.
        """
        if self.app_name_edit.text():
            font = QFont("Arial", 14)
            font.setBold(True)
            self.app_name_edit.setFont(font)
            self.app_name_edit.setReadOnly(True)

    def _populate_local_python_paths(self):
        """
        Populates the local Python ComboBox with common Python executable paths.
        """
        potential_paths = []

        # Add current interpreter (if applicable)
        potential_paths.append(sys.executable)

        # Common executable names
        python_exec_names = ["python", "python3"]

        # Check PATH environment variable
        path_env = os.environ.get("PATH", "").split(os.pathsep)
        for p in path_env:
            for name in python_exec_names:
                full_path = os.path.join(p, name)
                if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                    potential_paths.append(full_path)

        # Remove duplicates and add to combo box
        unique_paths = sorted(list(set(potential_paths)))
        if not unique_paths:
            self.local_python_combo.addItem("未找到本地 Python 环境")
            self.local_python_combo.setEnabled(False)
        else:
            self.local_python_combo.addItems(unique_paths)

    def _populate_conda_environments(self):
        """
        Populates the Conda environment ComboBox by running `conda env list --json`.
        """
        try:
            result = subprocess.run(
                ["conda", "env", "list", "--json"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8' # Ensure correct encoding
            )
            conda_data = json.loads(result.stdout)
            environments = [os.path.basename(env_path) if env_path != conda_data.get("envs")[0] else "base"
                            for env_path in conda_data.get("envs", [])]
            if not environments:
                self.conda_env_combo.addItem("未找到 Conda 环境")
                self.conda_env_combo.setEnabled(False)
            else:
                # Conda environments usually start with the base environment full path
                # and then just the names for others. We want just the names.
                # The first item in envs is typically the base environment's full path.
                # We'll special-case it to "base".
                env_names = []
                for env_path in conda_data.get("envs", []):
                    if env_path == conda_data["envs"][0]: # Check if it's the base path
                        env_names.append("base")
                    else:
                        env_names.append(os.path.basename(env_path))
                self.conda_env_combo.addItems(sorted(list(set(env_names)))) # Sort and remove duplicates

        except FileNotFoundError:
            self.conda_env_combo.addItem("Conda 未安装或不在 PATH 中")
            self.conda_env_combo.setEnabled(False)
            QMessageBox.warning(self, "Conda 错误", "Conda 命令未找到。请确保 Conda 已安装并配置到系统 PATH 中。")
        except subprocess.CalledProcessError as e:
            self.conda_env_combo.addItem("获取 Conda 环境失败")
            self.conda_env_combo.setEnabled(False)
            QMessageBox.critical(self, "Conda 错误", f"执行 'conda env list --json' 失败: {e.stderr}")
        except json.JSONDecodeError as e:
            self.conda_env_combo.addItem("解析 Conda 输出失败")
            self.conda_env_combo.setEnabled(False)
            QMessageBox.critical(self, "Conda 错误", f"解析 Conda JSON 输出失败: {e}")
        except Exception as e:
            self.conda_env_combo.addItem("获取 Conda 环境时发生未知错误")
            self.conda_env_combo.setEnabled(False)
            QMessageBox.critical(self, "Conda 错误", f"获取 Conda 环境时发生未知错误: {e}")


    def _update_python_env_visibility(self):
        """
        Updates the visibility of the Python environment ComboBoxes based on radio button selection.
        """
        self.local_python_combo.setVisible(self.local_python_radio.isChecked())
        self.conda_env_combo.setVisible(self.conda_radio.isChecked())

    def _update_run_mode(self):
        """
        Updates the run_in_terminal flag based on the radio button selection.
        """
        self.run_in_terminal = self.terminal_run_radio.isChecked()
        print(f"Run in terminal: {self.run_in_terminal}") # For demonstration/debugging

    def _create_app(self):
        """
        Creates the MacOS application.
        """
        if sys.platform != 'darwin':
            QMessageBox.critical(self, "平台不支持", "此功能仅支持 macOS 平台。")
            return

        app_name = self.app_name_edit.text().strip()
        if not app_name:
            QMessageBox.warning(self, "输入错误", "请输入应用程序名称。")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "选择保存 .app 的目录", os.path.expanduser("~"))
        if not output_dir:
            QMessageBox.information(self, "取消", "应用程序生成已取消。")
            return

        app_bundle_path = os.path.join(output_dir, f"{app_name}.app")
        contents_path = os.path.join(app_bundle_path, "Contents")
        macos_path = os.path.join(contents_path, "MacOS")
        resources_path = os.path.join(contents_path, "Resources")

        self._write_config(resources_path)
        self._create_icns(resources_path)
        self._create_uifile(resources_path)

        if not self._mv_caller2app(macos_path):
            QMessageBox.information(self, "MaoOS生成失败", "应用程序生成已取消。")
            return

        if not self._create_infoplist(contents_path):
            return

    def _write_config(self, resources_path):
        """
        Writes the configuration file to Resources/config.ini.
        """
        config = configparser.ConfigParser()

        # Ensure the Resources directory exists
        if not os.path.exists(resources_path):
            os.makedirs(resources_path)

        if self.generated_ui_widgets:
            config['launchermode'] = {'enabled': 'True'} # Use a section for launchermode
        else:
            config['launchermode'] = {'enabled': 'False'}
            if self.terminal_run_radio.isChecked():
                config['runmode'] = {'mode': 'terminal'}
            else:
                config['runmode'] = {'mode': 'silent'}


        if self.executable_path.lower().endswith(".py"):
            config['script'] = {'ispython': 'True'}
            if self.local_python_radio.isChecked():
                config['script']['python_env_type'] = 'local'
                config['script']['python_executable'] = self.local_python_combo.currentText()
            else:
                config['script']['python_env_type'] = 'conda'
                config['script']['conda_env_name'] = self.conda_env_combo.currentText()
        else:
            config['script'] = {'ispython': 'False'}

        config_path = os.path.join(resources_path, "config.ini")
        try:
            with open(config_path, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"写入配置文件失败: {e}")

    def _create_icns(self,resources_path):

        if self.image_path:
            temp_iconset_dir = os.path.join(resources_path, "icon.iconset")
            icon_path_in_bundle = os.path.join(resources_path, "AppIcon.icns")
            # Ensure the Resources directory exists
            if not os.path.exists(resources_path):
                os.makedirs(resources_path, exist_ok=True)

            os.makedirs(temp_iconset_dir, exist_ok=True)
            base_image = self.image_path

            try:
                icon_specs = [
                    (16, "icon_16x16.png"), (32, "icon_16x16@2x.png"),
                    (32, "icon_32x32.png"), (64, "icon_32x32@2x.png"),
                    (128, "icon_128x128.png"), (256, "icon_128x128@2x.png"),
                    (256, "icon_256x256.png"), (512, "icon_256x512@2x.png"),
                    (512, "icon_512x512.png"), (1024, "icon_512x512@2x.png")
                ]

                for size, name in icon_specs:
                    output_png_path = os.path.join(temp_iconset_dir, name)
                    sips_cmd = ["sips", "-z", str(size), str(size), base_image, "--out", output_png_path]
                    subprocess.run(sips_cmd, check=True, capture_output=True)

                iconutil_cmd = ["iconutil", "-c", "icns", temp_iconset_dir, "-o", icon_path_in_bundle]
                subprocess.run(iconutil_cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "图标生成失败", f"应用程序图标可能无法正常显示({e}).\n请提供 .icns 文件或手动替换 AppIcon.icns")
                with open(icon_path_in_bundle, 'w') as f:
                    f.write("DUMMY_ICNS")
            except Exception as e:
                QMessageBox.critical(self, "图标生成失败", f"应用程序图标可能无法正常显示({e}).\n请提供 .icns 文件或手动替换 AppIcon.icns")
                with open(icon_path_in_bundle, 'w') as f:
                    f.write("DUMMY_ICNS")
            finally:
                if os.path.exists(temp_iconset_dir):
                    if os.path.isdir(temp_iconset_dir):
                        shutil.rmtree(temp_iconset_dir)

    def _mv_caller2app (self, macos_path):
        # 1. 创建目标目录
        try:
            os.makedirs(macos_path, exist_ok=True)
        except OSError as e:
            return False  # 返回 False 表示操作失败

        # 2. 复制 Caller 脚本到应用包
        caller_source_file = "Caller/Caller.sh"
        # 统一使用 "Caller" 作为目标文件名，避免 Callor 混淆
        caller_destination_path = os.path.join(macos_path, "Caller.sh")

        try:
            shutil.copyfile(caller_source_file, caller_destination_path)
        except FileNotFoundError:
            print(f"错误：源文件 '{caller_source_file}' 未找到。")
            return False
        except PermissionError:
            print(f"错误：没有权限复制文件到 '{caller_destination_path}'。")
            return False
        except Exception as e:
            print(f"复制 '{caller_source_file}' 时发生意外错误：{e}")
            return False

        # 3. 为 Caller 脚本添加执行权限 (chmod u+x)
        try:
            import stat
            current_mode = os.stat(caller_destination_path).st_mode
            new_mode = current_mode | stat.S_IXUSR  # 添加用户执行权限
            os.chmod(caller_destination_path, new_mode)
            # 打印八进制形式的权限，更直观
            print(f"已为 '{caller_destination_path}' 设置用户执行权限。新权限：{oct(os.stat(caller_destination_path).st_mode & 0o777)}")
        except FileNotFoundError:
            print(f"错误：已复制的 Caller 文件 '{caller_destination_path}' 未找到，无法修改权限。")
            return False
        except PermissionError:
            print(f"错误：没有权限修改 '{caller_destination_path}' 的权限。")
            return False
        except Exception as e:
            print(f"修改 '{caller_destination_path}' 权限时发生意外错误：{e}")
            return False

        # 4. 复制主脚本/可执行文件到应用包
        try:
            callor_destination_path = os.path.join(macos_path, "Callor")
            shutil.copyfile(self.executable_path, callor_destination_path)
            import stat
            current_mode = os.stat(callor_destination_path).st_mode
            new_mode = current_mode | stat.S_IXUSR  # 添加用户执行权限
            os.chmod(callor_destination_path, new_mode)
        except FileNotFoundError:
            print(f"错误：主可执行文件源 '{self.executable_path}' 未找到。")
            return False
        except Exception as e:
            print(f"复制或修改 '{self.executable_path}' 权限时发生意外错误：{e}")
            return False

        # 5. 复制启动器文件到应用包
        if self.generated_ui_widgets:
            mylaunch_source_file = "Caller/MyLauncher.py"
            # 统一使用 "Caller" 作为目标文件名，避免 Callor 混淆
            mylaunch_destination_path = os.path.join(macos_path, "MyLaunch")

            try:
                shutil.copyfile(mylaunch_source_file, mylaunch_destination_path)
            except FileNotFoundError:
                print(f"错误：源文件 '{mylaunch_source_file}' 未找到。")
                return False
            except PermissionError:
                print(f"错误：没有权限复制文件到 '{mylaunch_destination_path}'。")
                return False
            except Exception as e:
                print(f"复制 '{mylaunch_source_file}' 时发生意外错误：{e}")
                return False

        return True  # 所有操作成功完成

    def _create_infoplist(self,contents_path):
        info_plist_path = os.path.join(contents_path, "Info.plist")
        app_name = self.app_name_edit.text().strip()
        info_plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Caller.sh</string>
    <key>CFBundleIdentifier</key>
    <string>com.marspacecraft.{app_name.lower().replace(" ", "")}</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13.0</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon.icns</string>
</dict>
</plist>
"""
        try:
            with open(info_plist_path, 'w') as f:
                f.write(info_plist_content)
        except Exception as e:
            QMessageBox.critical(self, "生成Info.plist失败", f"生成 macOS 应用程序时发生错误：\n{e}")
            return False

        return True
    def _create_uifile(self,resources_path):
        ui_json_path = os.path.join(resources_path, "UI.json")
        if self.json_data and self.json_data != '[]':
            try:
                with open(ui_json_path, 'w', encoding='utf-8') as f:
                    f.writelines(self.json_data)
            except Exception as e:
                QMessageBox.critical(self, "写ui文件失败", f"写入文件时发生错误: {e}")
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Prepare some dummy data for testing
    dummy_exe = "test_script.sh"
    dummy_python_script = "test_script.py"

    # Create dummy shell script
    if os.name == 'nt':
        dummy_exe = "test_script.bat"
        with open(dummy_exe, "w") as f:
            f.write("@echo off\necho This is a dummy script.\npause")
    else:
        with open(dummy_exe, "w") as f:
            f.write("#!/bin/bash\necho \"This is a dummy script.\"\nsleep 2")
        os.chmod(dummy_exe, 0o755)

    # Create dummy Python script
    with open(dummy_python_script, "w") as f:
        f.write("import sys\nprint(f'Hello from Python! Interpreter: {sys.executable}')\n")

    dummy_png = "test_icon.png"
    try:
        img = Image.new('RGB', (60, 30), color='red')
        img.save(dummy_png)
    except ImportError:
        print("Pillow not installed. Cannot create dummy PNG. Please install with 'pip install Pillow'")
        dummy_png = None

    # --- 测试用例：现在 json_data 需要是 UI 元素描述的列表 ---

    # Test case 1: JSON data as a dictionary (list of dicts) for UI elements
    # sample_ui_elements_dict = [
    #     {
    #         "type": "Button",
    #         "name": "--verbose",
    #         "description": "详细输出模式",
    #         "initial_enabled": True
    #     },
    #     {
    #         "type": "ComboBox",
    #         "description": "选择日志级别",
    #         "items": ["DEBUG", "INFO", "WARNING", "ERROR"],
    #         "default_index": 1,
    #         "initial_enabled": True
    #     },
    #     {
    #         "type": "Button",
    #         "name": "--dry-run",
    #         "description": "模拟运行",
    #         "initial_enabled": False
    #     },
    #     {
    #         "type": "ComboBox",
    #         "description": "选择主题颜色",
    #         "items": ["Light", "Dark", "Blue"],
    #         "default_index": 0,
    #         "initial_enabled": True
    #     }
    # ]
    #
    # print("\n--- Test Case: Standard Executable (Non-Python) with UI Elements ---")
    # dialog_with_ui_elements = AppCreaterWindow(
    #     executable_path=dummy_exe,
    #     image_path=dummy_png,
    #     json_data=sample_ui_elements_dict
    # )
    # dialog_with_ui_elements.setWindowTitle("UI 控件显示 (字典列表) - 非 Python")
    # dialog_with_ui_elements.exec_()
    #
    # print("\n--- Test Case: Python Executable with UI Elements and Environment Selection ---")
    # dialog_python_exe = AppCreaterWindow(
    #     executable_path=dummy_python_script,
    #     image_path=dummy_png,
    #     json_data=sample_ui_elements_dict
    # )
    # dialog_python_exe.setWindowTitle("Python 脚本及环境选择")
    # dialog_python_exe.exec_()
    #
    # Test case 2: JSON data as a string (representing a list of dicts) for UI elements
    sample_ui_elements_string = """
    [
        {
            "type": "Button",
            "name": "--force",
            "description": "强制执行",
            "initial_enabled": false
        },
        {
            "type": "ComboBox",
            "description": "选择输出格式",
            "items": ["JSON", "XML", "CSV"],
            "default_index": 0,
            "initial_enabled": true
        }
    ]
    """
    print("\n--- Test Case: Python Executable with JSON String and Environment Selection ---")
    dialog_with_ui_elements_string = AppCreaterWindow(
        executable_path=dummy_python_script,
        image_path=dummy_png,
        json_data=sample_ui_elements_string
    )
    dialog_with_ui_elements_string.setWindowTitle("UI 控件显示 (JSON 字符串) - Python")
    dialog_with_ui_elements_string.exec_()

    # Test case 3: No JSON data (应显示“未提供...UI 控件数据”)
    # print("\n--- Test Case: No UI Controls JSON Data ---")
    # dialog_no_json = AppCreaterWindow(
    #     executable_path=dummy_exe,
    #     image_path=dummy_png,
    #     json_data=None  # No JSON data
    # )
    # dialog_no_json.setWindowTitle("无 UI 控件数据")
    # dialog_no_json.exec_()

    # Test case 4: Invalid JSON string (应弹出错误消息框)
    # print("\n--- Test Case: Invalid UI Controls JSON String ---")
    # invalid_json_string = "{'key': 'value'}"  # 使用单引号，这是无效的 JSON
    # dialog_invalid_json = AppCreaterWindow(
    #     executable_path=dummy_exe,
    #     image_path=dummy_png,
    #     json_data=invalid_json_string
    # )
    # dialog_invalid_json.setWindowTitle("无效 UI 控件 JSON")
    # dialog_invalid_json.exec_()

    # Clean up dummy files
    if os.path.exists(dummy_exe):
        os.remove(dummy_exe)
    if os.path.exists(dummy_python_script):
        os.remove(dummy_python_script)
    if dummy_png and os.path.exists(dummy_png):
        os.remove(dummy_png)

    sys.exit(app.exec_())