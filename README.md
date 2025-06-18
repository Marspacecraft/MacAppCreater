# 使用说明

## 作用

- 把shell脚本和python脚本打包成mac app格式的程序

- 系统命令可以通过shell脚本封装一层运行

- python支持conda

- 支持拖动到docker栏和应用程序

- 支持配置运行参数

- 支持打开终端运行

## 安装

- 程序默认都是运行brew安装的python，如果没有用brew安装过python，使用系统自带python
- 默认python环境如果没有安装依赖，参数配置的启动器无法运行
- 查看默认python

```bash
which python3

# 显示类似 /opt/homebrew/bin/python3 说明默认用的是brew安装的python
# 显示类似 /usr/bin/python3 说明默认用的是系统自带的python
```

- brew安装

```bash
brew install PyQt5
brew install Pillow
# 安装conda，可选
brew install  --cask miniconda
```

- 系统自带python

```bash
pip3 install PyQt5
pip3 install Pillow
```

## 使用

![](https://github.com/Marspacecraft/MacAppCreater/blob/main/pic/1.png)

- step1:运行`main.py`

- step2:选择需要运行的程序

- step3:如果需要参数，设置参数

- step4:如果需要设置图片，选择图片

- step5点击生成

![](https://github.com/Marspacecraft/MacAppCreater/blob/main/pic/2.png)

- step6:设置App名称

- step7:如果是无参数运行python，可以选择本地python还是conda环境

- step8:如果是无参数运行，可以选择静默运行还是打开终端运行

- step9:点击生成App

![](https://github.com/Marspacecraft/MacAppCreater/blob/main/pic/5.png)

## 运行

![](https://github.com/Marspacecraft/MacAppCreater/blob/main/pic/3.png)

- 第一次运行会失败，再次运行即可

- 如果配置了参数，会启动启动器，配置完参数即可选择静默运行还是终端运行

## 实例

- 上面图片为配置ffmpeg截取视频的配置

- ffmpegcut.sh

```bash
#!/bin/bash
# 运行其它系统命令的shell脚本类似
# 如果运行 ls 命令可以改成 ls $@
# app启动的bash非常干净，如果不能运行可能需要生效环境变量
# 生成环境变量
# source $HOME/.bashrc

ffmpeg $@
```

![](https://github.com/Marspacecraft/MacAppCreater/blob/main/pic/4.png)

## 打包

```bash
# 生成app
pyinstaller main.py --windowed --noconsole --icon=AppIcon.icns --add-data "Resources/Caller:Caller" --name "MacAppCreater"
# 生成dmg
create-dmg --volname "MacAppCreator Installer" --background "Resources/1.png" --window-pos 200 120 --window-size 800 500 --icon-size 100 --text-size 14 --icon "MacAppCreater.app" 200 200 --app-drop-link 600 200 --eula "LICENSE" "dist/MacAppCreaterInstaller.dmg" "dist/MacAppCreater.app"
```

## 安装包

[V1.01](https://github.com/Marspacecraft/MacAppCreater/releases/tag/1.01)
