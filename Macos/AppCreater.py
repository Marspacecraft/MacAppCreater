import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFileDialog, QWidget, QApplication, QGroupBox, QRadioButton,
    QComboBox, QListWidget
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import subprocess
import json
import os
from PIL import Image
import configparser
import shutil

# Minimal UItemCreaterWindow for demonstration if MyUI.py is not present

from Macos.MyUI import UItemCreaterWindow


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
        # Apply the shared style sheet
        self.setStyleSheet(self.WIDGET_GROUP_STYLE)

        self.executable_path = executable_path
        self.image_path = image_path
        self.json_data = json_data
        self.resources_path = os.path.join(self._get_resource_base_path() , "../Resources")

        # Add instance variable to store run mode
        self.run_in_terminal = True  # Default to terminal run

        self._create_widgets()

        # 调用 adjustSize() 方法，在所有控件和布局都设置好后，
        # 让窗口根据内容的最佳大小提示进行调整。
        self.adjustSize()

    def _get_resource_base_path(self):
        """
        获取打包后应用的资源根路径。
        在开发环境中，它返回当前脚本所在的目录。
        在 PyInstaller 打包的应用中，它返回 _MEIPASS。
        """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            # For development environment, use the directory where the script is located
            base_path = os.path.dirname(os.path.abspath(__file__))

        return base_path
    def _create_runmode_widgets(self, main_layout):
        # --- Add Run Mode Selection when no JSON data is provided ---
        run_mode_group_box = QGroupBox("运行模式")
        # run_mode_group_box.setStyleSheet("font-size: 14px; font-weight: bold;") # Style applied via self.setStyleSheet
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
        app_name_group = QGroupBox("App程序名设置")  # Wrap in QGroupBox
        # app_name_group.setStyleSheet("font-size: 14px; font-weight: bold;") # Style applied via self.setStyleSheet
        app_name_group_layout = QHBoxLayout()
        app_name_group.setLayout(app_name_group_layout)

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
        # app_name_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;") # Style applied via self.setStyleSheet
        app_name_group_layout.addWidget(app_name_label)
        self.app_name_edit = QLineEdit()
        self.app_name_edit.setPlaceholderText("请输入 App 程序名称")
        self.app_name_edit.editingFinished.connect(self._set_app_name_read_only)
        self.app_name_edit.setStyleSheet("color: red;")
        app_name_group_layout.addWidget(self.app_name_edit)
        main_layout.addWidget(app_name_group)  # Add the group box

        # 显示脚本路径
        executable_path_group = QGroupBox("可执行文件")  # Wrap in QGroupBox
        # executable_path_group.setStyleSheet("font-size: 14px; font-weight: bold;") # Style applied via self.setStyleSheet
        exe_layout = QHBoxLayout()
        executable_path_group.setLayout(exe_layout)
        exe_label = QLabel(f"{self.executable_path}")  # Removed bold tag and padding as group box title handles it
        # exe_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;") # Style applied via self.setStyleSheet
        exe_layout.addWidget(exe_label)
        main_layout.addWidget(executable_path_group)  # Add the group box

        # --- Python Environment Selection ---
        if self.executable_path and self.executable_path.lower().endswith(".py"):
            python_env_group_box = QGroupBox("Python 环境选择")
            # python_env_group_box.setStyleSheet("font-size: 14px; font-weight: bold;") # Style applied via self.setStyleSheet
            python_env_layout = QVBoxLayout()
            python_env_group_box.setLayout(python_env_layout)

            radio_button_layout = QHBoxLayout()
            self.local_python_radio = QRadioButton("本地 Python")
            self.conda_radio = QRadioButton("Conda")
            radio_button_layout.addWidget(self.local_python_radio)
            radio_button_layout.addWidget(self.conda_radio)
            radio_button_layout.addStretch(1)  # Push buttons to the left
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
            self.local_python_radio.setChecked(True)  # Default to Local Python

            main_layout.addWidget(python_env_group_box)

        # --- UI Controls Section ---
        self.generated_ui_widgets = []
        if self.json_data and self.json_data != '[]':
            # 选择启动器的python

            # 显示UI编辑界面
            ui_controls_group_box = QGroupBox("配置参数")
            # ui_controls_group_box.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;") # Style applied via self.setStyleSheet
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
                    ui_elements_data_to_parse,self.ui_controls_layout)
                main_layout.addWidget(ui_controls_group_box)
            else:
                self._create_runmode_widgets(main_layout)

        else:
            self._create_runmode_widgets(main_layout)

        # --- Generate Button ---
        generate_button = QPushButton("生成App")
        generate_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;") # Style applied via self.setStyleSheet
        generate_button.clicked.connect(self._create_app)
        main_layout.addWidget(generate_button)

    def _set_app_name_read_only(self):
        """
        Sets the application name QLineEdit to read-only after editing is finished.
        """
        if self.app_name_edit.text():
            # font = QFont("Arial", 14) # No longer needed due to CSS
            # font.setBold(True)
            # self.app_name_edit.setFont(font)
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
                encoding='utf-8'  # Ensure correct encoding
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
                    if env_path == conda_data["envs"][0]:  # Check if it's the base path
                        env_names.append("base")
                    else:
                        env_names.append(os.path.basename(env_path))
                self.conda_env_combo.addItems(sorted(list(set(env_names))))  # Sort and remove duplicates

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
        print(f"Run in terminal: {self.run_in_terminal}")  # For demonstration/debugging

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

        # Create directories
        try:
            os.makedirs(macos_path, exist_ok=True)
            os.makedirs(resources_path, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, "目录创建失败", f"无法创建应用程序目录: {e}")
            return

        self._write_config(resources_path)
        self._create_icns(resources_path)
        self._create_uifile(resources_path)

        if not self._mv_caller2app(macos_path):
            QMessageBox.critical(self, "macOS生成失败", "应用程序生成已取消。")
            return

        if not self._create_infoplist(contents_path):
            return

        QMessageBox.information(self, "生成成功", f"'{app_name}.app' 已成功生成在:\n{output_dir}")

    def _write_config(self, resources_path):
        """
        Writes the configuration file to Resources/config.ini.
        """
        config = configparser.ConfigParser()

        # Ensure the Resources directory exists (redundant with create_app but good practice)
        if not os.path.exists(resources_path):
            os.makedirs(resources_path)

        if self.generated_ui_widgets:
            config['launchermode'] = {'enabled': 'True'}  # Use a section for launchermode
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

    def _create_icns(self, resources_path):

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
                    (256, "icon_256x256.png"), (512, "icon_256x512.png"),
                    # Corrected from 256x512@2x to 256x256 and 512x512
                    (512, "icon_512x512@2x.png"), (1024, "icon_512x512@2x.png")
                    # Changed 1024 to 512x512@2x as per Apple guidelines
                ]

                # If the base image is not square, we should probably resize it without distorting aspect ratio,
                # then center it on a square canvas.
                # For simplicity, sips will just stretch, so better to warn or pre-process if image is not square.
                original_image = Image.open(base_image)
                original_width, original_height = original_image.size
                if original_width != original_height:
                    QMessageBox.warning(self, "图标警告",
                                        "提供的图标图片不是正方形，可能会导致拉伸或显示异常。建议使用正方形图片。")

                for size, name in icon_specs:
                    output_png_path = os.path.join(temp_iconset_dir, name)
                    # Use PIL for better resizing and aspect ratio handling
                    img = original_image.copy()
                    img.thumbnail((size, size), Image.Resampling.LANCZOS)  # Use LANCZOS for high quality downsampling

                    # Create a new square image and paste the resized image into its center
                    new_img = Image.new("RGBA", (size, size), (255, 255, 255, 0))  # Transparent background
                    paste_x = (size - img.width) // 2
                    paste_y = (size - img.height) // 2
                    new_img.paste(img, (paste_x, paste_y), img if img.mode == 'RGBA' else None)
                    new_img.save(output_png_path)

                iconutil_cmd = ["iconutil", "-c", "icns", temp_iconset_dir, "-o", icon_path_in_bundle]
                subprocess.run(iconutil_cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "图标生成失败",
                                     f"应用程序图标可能无法正常显示。请确保 'iconutil' 命令可用且图片格式正确。\n错误输出:\n{e.stderr}")
                # Fallback: create a dummy icns if iconutil fails
                with open(icon_path_in_bundle, 'w') as f:
                    f.write("DUMMY_ICNS")
            except FileNotFoundError:
                QMessageBox.critical(self, "图标生成失败",
                                     f"找不到 'iconutil' 命令。请确保 Xcode Command Line Tools 已安装。")
                with open(icon_path_in_bundle, 'w') as f:
                    f.write("DUMMY_ICNS")
            except Exception as e:
                QMessageBox.critical(self, "图标生成失败",
                                     f"应用程序图标可能无法正常显示。请检查图片文件是否有效。\n错误: {e}")
                with open(icon_path_in_bundle, 'w') as f:
                    f.write("DUMMY_ICNS")
            finally:
                if os.path.exists(temp_iconset_dir):
                    if os.path.isdir(temp_iconset_dir):
                        shutil.rmtree(temp_iconset_dir)

    def _mv_caller2app(self, macos_path):
        # 1. 创建目标目录 (already done in _create_app, but idempotent)
        try:
            os.makedirs(macos_path, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, "目录创建失败", f"无法创建 MacOS 目录: {e}")
            return False  # 返回 False 表示操作失败

        # 2. 复制 Caller 脚本到应用包
        caller_source_file = os.path.join(self.resources_path,"Caller/Caller.sh")
        # 统一使用 "Caller" 作为目标文件名
        caller_destination_path = os.path.join(macos_path, "Caller.sh")

        try:
            shutil.copyfile(caller_source_file, caller_destination_path)
        except FileNotFoundError:
            QMessageBox.critical(self, "文件缺失",
                                 f"错误：源文件 '{caller_source_file}' 未找到。请确保 'Caller' 目录及其内容存在。")
            return False
        except PermissionError:
            QMessageBox.critical(self, "权限不足", f"错误：没有权限复制文件到 '{caller_destination_path}'。")
            return False
        except Exception as e:
            QMessageBox.critical(self, "文件复制失败", f"复制 '{caller_source_file}' 时发生意外错误：{e}")
            return False

        # 3. 为 Caller 脚本添加执行权限 (chmod u+x)
        try:
            import stat
            current_mode = os.stat(caller_destination_path).st_mode
            new_mode = current_mode | stat.S_IXUSR  # 添加用户执行权限
            os.chmod(caller_destination_path, new_mode)
            # print(f"已为 '{caller_destination_path}' 设置用户执行权限。新权限：{oct(os.stat(caller_destination_path).st_mode & 0o777)}")
        except FileNotFoundError:
            QMessageBox.critical(self, "文件缺失",
                                 f"错误：已复制的 Caller 文件 '{caller_destination_path}' 未找到，无法修改权限。")
            return False
        except PermissionError:
            QMessageBox.critical(self, "权限不足", f"错误：没有权限修改 '{caller_destination_path}' 的权限。")
            return False
        except Exception as e:
            QMessageBox.critical(self, "权限修改失败", f"修改 '{caller_destination_path}' 权限时发生意外错误：{e}")
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
            QMessageBox.critical(self, "文件缺失", f"错误：主可执行文件源 '{self.executable_path}' 未找到。")
            return False
        except Exception as e:
            QMessageBox.critical(self, "文件复制/权限修改失败",
                                 f"复制或修改 '{self.executable_path}' 权限时发生意外错误：{e}")
            return False

        # 5. 复制启动器文件到应用包
        if self.generated_ui_widgets:
            mylaunch_source_file = os.path.join(self.resources_path,"Caller/MyLauncher.py")
            mylaunch_destination_path = os.path.join(macos_path, "MyLaunch")

            try:
                shutil.copyfile(mylaunch_source_file, mylaunch_destination_path)
                import stat
                current_mode = os.stat(mylaunch_destination_path).st_mode
                new_mode = current_mode | stat.S_IXUSR  # 添加用户执行权限
                os.chmod(mylaunch_destination_path, new_mode)
            except FileNotFoundError:
                QMessageBox.critical(self, "文件缺失",
                                     f"错误：源文件 '{mylaunch_source_file}' 未找到。生成带UI的App需要此文件。")
                return False
            except PermissionError:
                QMessageBox.critical(self, "权限不足", f"错误：没有权限复制文件到 '{mylaunch_destination_path}'。")
                return False
            except Exception as e:
                QMessageBox.critical(self, "文件复制/权限修改失败", f"复制 '{mylaunch_source_file}' 时发生意外错误：{e}")
                return False

        return True  # 所有操作成功完成

    def _create_infoplist(self, contents_path):
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

    def _create_uifile(self, resources_path):
        ui_json_path = os.path.join(resources_path, "UI.json")
        if self.json_data and self.json_data != '[]':
            try:
                with open(ui_json_path, 'w', encoding='utf-8') as f:
                    f.writelines(self.json_data)
            except Exception as e:
                QMessageBox.critical(self, "写ui文件失败", f"写入文件时发生错误: {e}")


# Assuming LauncherDesigner and MyUI are in separate files as per the original structure
# For testing the AppCreaterWindow independently, we'll keep the dummy classes.

# The provided MainWindow and PyQtUIDesignerApp will remain mostly the same,
# but ensure LauncherDesigner.py and MyUI.py are correctly structured
# and include the WIDGET_GROUP_STYLE.

# --- MainWindow and PyQtUIDesignerApp (from your second block) ---
# Assuming Launcher.py contains LauncherDesigner and MyUI.py contains UItemCreaterWindow
# and the WIDGET_GROUP_STYLE.
# I'm including a simplified version here for self-containment if Launcher.py/MyUI.py aren't available.

# --- Start of the second provided code block (MainWindow) ---
# Minimal LauncherDesigner and MyUI classes for demonstration
try:
    from Macos.Launcher import LauncherDesigner
    from Macos.MyUI import UItemCreaterWindow  # Import UItemCreaterWindow (which should contain WIDGET_GROUP_STYLE)
except ImportError:
    print("Launcher.py or MyUI.py not found. Using minimal dummy classes for demonstration.")


    class LauncherDesigner(QGroupBox):
        def __init__(self, parent=None):
            super().__init__("配置启动器 UI 控件", parent)
            self.setLayout(QVBoxLayout())
            self.radio_enable = QRadioButton("启用 UI 控件")
            self.radio_disable = QRadioButton("禁用 UI 控件")
            self.radio_enable.setChecked(True)
            self.layout().addWidget(self.radio_enable)
            self.layout().addWidget(self.radio_disable)
            self.list_widget = QListWidget()
            self.layout().addWidget(self.list_widget)
            self.set_designer_enabled(False)  # Initially disabled

        def set_designer_enabled(self, enabled):
            self.setEnabled(enabled)
            self.radio_enable.setEnabled(enabled)
            self.radio_disable.setEnabled(enabled)

        def is_enable_widgets_radio_checked(self):
            return self.radio_enable.isChecked()

        def get_ui_description_data(self):
            return "[]"  # Dummy data


    # UItemCreaterWindow from above, needs to be consistently defined
    # If MyUI.py exists, it should define UItemCreaterWindow and the style.
    # If not, the dummy UItemCreaterWindow defined at the top of AppCreaterWindow.py
    # would be used, which also includes the WIDGET_GROUP_STYLE.
    pass  # No need to redefine UItemCreaterWindow if it's already defined


class MainWindow(QWidget, UItemCreaterWindow):  # Inherit UItemCreaterWindow to get WIDGET_GROUP_STYLE
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exe_path = ""
        self.png_path = ""

        self.setWindowTitle('MacAppCreater')
        self.setGeometry(50, 80, 400, 400)  # Set initial size
        self.center_on_screen()

        # Apply MyUI.py defined general style (assuming UItemCreaterWindow brings it)
        self.setStyleSheet(self.WIDGET_GROUP_STYLE)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Top label
        top_label = QLabel("欢迎使用Mac app生成器")
        top_label.setAlignment(Qt.AlignCenter)
        top_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; padding: 10px; color: #DC3545;")  # Red color for welcome
        main_layout.addWidget(top_label)

        # Executable file selection area - Wrap in QGroupBox
        executable_group = QGroupBox("选择执行文件")
        # executable_group.setStyleSheet(self.WIDGET_GROUP_STYLE) # Style already applied to self
        executable_selection_layout = QHBoxLayout()
        executable_group.setLayout(executable_selection_layout)

        self.executable_path_display = QLineEdit()
        self.executable_path_display.setPlaceholderText("未选择执行文件")
        self.executable_path_display.setReadOnly(True)  # Set as read-only
        executable_selection_layout.addWidget(self.executable_path_display)
        self.executable_path_display.setStyleSheet("color: #007BFF;")  # Blue color for path text

        self.select_file_button = QPushButton("选择文件")  # Modified button text
        self.select_file_button.clicked.connect(self.select_executable_file)
        executable_selection_layout.addWidget(self.select_file_button)
        main_layout.addWidget(executable_group)

        # Instantiate Designer as a component
        self.launcherdesigner = LauncherDesigner(self)  # Pass self as parent
        main_layout.addWidget(self.launcherdesigner)

        # Icon selection area - Wrap in QGroupBox
        icon_group = QGroupBox("选择应用图标")  # Modified group box title
        # icon_group.setStyleSheet(self.WIDGET_GROUP_STYLE) # Style already applied to self
        icon_selection_layout = QHBoxLayout()
        icon_group.setLayout(icon_selection_layout)

        self.icon_path_display = QLineEdit()
        self.icon_path_display.setPlaceholderText("未选择图标文件 (仅支持PNG)")
        self.icon_path_display.setReadOnly(True)  # Set as read-only
        icon_selection_layout.addWidget(self.icon_path_display)
        self.icon_path_display.setStyleSheet("color: #007BFF;")  # Blue color for path text

        self.select_icon_button = QPushButton("选择图标")  # Modified button text
        self.select_icon_button.clicked.connect(self.select_icon_file)
        icon_selection_layout.addWidget(self.select_icon_button)
        main_layout.addWidget(icon_group)

        # Disable icon selection widgets by default
        self.icon_path_display.setEnabled(False)
        self.select_icon_button.setEnabled(False)

        # --- New Generate App Button ---
        self.generate_app_button = QPushButton("生成APP")
        self.generate_app_button.clicked.connect(self.show_appcreater_window)
        self.generate_app_button.setEnabled(False)  # Initially disabled
        main_layout.addWidget(self.generate_app_button)
        # --- End New ---

    def center_on_screen(self):
        """
        Centers the QMainWindow window on the primary screen.
        """
        # Get screen geometry
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Get window geometry
        qr = self.frameGeometry()
        window_width = qr.width()
        window_height = qr.height()

        # Calculate new top-left x and y coordinates
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Move window to the calculated position
        self.move(x, y)

    def select_executable_file(self):
        """
        Opens a file dialog to select an executable file (Python, Shell, or system command).
        The selected path is then displayed in the QLineEdit.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择执行文件",
            "",  # Start from current directory or last used
            "所有可执行文件 (*.py *.sh *.command);;Python 脚本 (*.py);;Shell 脚本 (*.sh *.command);;所有文件 (*)",
            options=options
        )
        if file_path:
            self.exe_path = file_path
            self.executable_path_display.setText(file_path)

            # After successfully selecting an executable, disable the select file button
            self.select_file_button.setEnabled(False)
            self.executable_path_display.setReadOnly(True)  # Ensure path display is read-only

            # Enable LauncherDesigner, icon selection widgets, and Generate App button
            self.launcherdesigner.set_designer_enabled(True)
            self.icon_path_display.setEnabled(True)
            self.select_icon_button.setEnabled(True)
            self.generate_app_button.setEnabled(True)  # Enable Generate App button
        else:
            self.exe_path = ""
            self.executable_path_display.clear()  # Clear display

            # If user cancels selection, re-enable the select executable file button
            self.select_file_button.setEnabled(True)  # Re-enable
            self.executable_path_display.setReadOnly(True)  # Keep read-only

            # Disable LauncherDesigner, icon selection widgets, and Generate App button
            self.launcherdesigner.set_designer_enabled(False)
            self.icon_path_display.setEnabled(False)
            self.select_icon_button.setEnabled(False)
            self.icon_path_display.clear()  # Clear icon path display
            self.generate_app_button.setEnabled(False)  # Disable Generate App button

    def select_icon_file(self):
        """
        Opens a file dialog to select an icon file (PNG only).
        The selected path is then displayed in the QLineEdit.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图标图片",
            "",  # Start from current directory or last used
            "PNG 图片 (*.png);;所有文件 (*)",  # Only PNG files supported
            options=options
        )
        if file_path:
            self.icon_path_display.setText(file_path)
            self.png_path = file_path
        # If user cancels selection, typically keep previous selection or do nothing extra.

    def show_appcreater_window(self):
        """
        Creates and displays an AppCreaterWindow instance.
        """
        uijson = ""
        if self.launcherdesigner.is_enable_widgets_radio_checked():
            uijson = self.launcherdesigner.get_ui_description_data()

        # Pop up the new content window
        app_creator_dialog = AppCreaterWindow(
            self,  # Pass the MainWindow instance as the parent
            executable_path=self.exe_path,
            image_path=self.png_path,
            json_data=uijson
        )
        app_creator_dialog.exec_()  # Use exec_() for modal dialogs


# --- Main application class, encapsulating the entire application launch logic ---
class PyQtUIDesignerApp:
    def __init__(self):
        self._app = None
        self._main_window = None  # Now holds a MainWindow instance

    def run(self):
        """Starts the PyQt UI Designer application."""
        if QApplication.instance():
            self._app = QApplication.instance()
        else:
            self._app = QApplication(sys.argv)

        self._main_window = MainWindow()  # Create MainWindow instance
        self._main_window.show()  # Show MainWindow
        sys.exit(self._app.exec_())


# Start the Designer app in your script
if __name__ == '__main__':
    app_instance = PyQtUIDesignerApp()
    app_instance.run()