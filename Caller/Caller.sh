#!/bin/bash

set -e # 任何命令失败立即退出

# 读取脚本路径
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
SCRIPT_DIR="${SCRIPT_DIR:-.}" # 如果 SCRIPT_DIR 为空或未设置，则将其设置为 "."

INI_FILE="$SCRIPT_DIR/../Resources/config.ini"
SCRIPT_PATH="$SCRIPT_DIR/Callor"

callerlog(){
  echo $1
#  echo $1 >> ~/Desktop/log.txt
}


callerlog "当前脚本目录: $SCRIPT_DIR"

get_ini_value() {
    local section=$1
    local key=$2
    local file=$3
    awk -F '=' '
        $0 ~ /^\['"$section"'\]/ { in_section=1; next }
        in_section && $0 ~ /^\[/ { in_section=0 }
        in_section && $1 ~ "^ *'"$key"' *$" { gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2; exit }
    ' "$file"
}

launchermode_enabled=$(get_ini_value launchermode enabled "$INI_FILE")
runmode_mode=$(get_ini_value runmode mode "$INI_FILE")
script_ispython=$(get_ini_value script ispython "$INI_FILE")
script_python_env_type=$(get_ini_value script python_env_type "$INI_FILE")
script_python_executable=$(get_ini_value script python_executable "$INI_FILE")
script_conda_env_name=$(get_ini_value script conda_env_name "$INI_FILE")

callerlog "launchermode.enabled=$launchermode_enabled"
callerlog "runmode.mode=$runmode_mode"
callerlog "script.ispython=$script_ispython"
callerlog "script.python_env_type=$script_python_env_type"
callerlog "script.python_executable=$script_python_executable"
callerlog "script.conda_env_name=$script_conda_env_name"


callerlog "主程序路径: $SCRIPT_PATH"

# 读取 [launchermode] enabled
if [ "$launchermode_enabled" == "True" ]; then
	  callerlog "启动器启动"
	  if [ -f "/opt/homebrew/bin/brew" ]; then
		    brewpython=$(/opt/homebrew/bin/brew --prefix python)/bin/python3
		    if [ -f "$brewpython" ]; then
			      callerlog "使用$brewpython运行"
			      `$brewpython "$SCRIPT_DIR/MyLaunch"`
			      exit 0
		    fi
	  fi
	  callerlog "使用默认python运行"
	  python3 "$SCRIPT_DIR/MyLaunch"
    exit 0
fi

# 检查 RUN_MODE
if [ "$runmode_mode" == "terminal" ]; then
    callerlog "运行模式: 终端运行"
else
    callerlog "运行模式: 静默运行"
fi



# 读取 [script] ispython
if [ "$script_ispython" == "True" ]; then
    callerlog "脚本类型: Python"
    # 读取 [script] python_env_type
    if [ "$script_python_env_type" == "local" ]; then
        callerlog "Python环境类型: 本地"
        # 读取 [script] python_executable (如果适用)
        if [ -n "$script_python_executable" ]; then
            callerlog "Python 可执行文件: $script_python_executable"

            if [ "$runmode_mode" == "terminal" ]; then
                # local终端模式下执行
                osascript <<EOF
tell application "Terminal"
		do script "$script_python_executable '$SCRIPT_PATH'"
		activate
end tell
EOF
            else
                 # local静默模式下执行
                "$script_python_executable" "$SCRIPT_PATH"
            fi
        else
            callerlog "Python 路径未定义。退出。"
            exit 0
        fi
    else # 否则为 conda
        callerlog "Python环境类型: Conda"
        # 读取 [script] conda_env_name (如果适用)
        if [ -n "$script_conda_env_name" ]; then
            callerlog "Conda 环境名称: $script_conda_env_name"

            # 更新环境变量，才能找到conda命令
            source "$HOME/.zshrc"
            # 拼接出 conda.sh 的完整路径
            CONDA_ROOT=$(conda info --base)
            CONDA_SH_PATH="$CONDA_ROOT/etc/profile.d/conda.sh"
            callerlog "Conda.sh: $CONDA_SH_PATH"

            if [ "$runmode_mode" == "terminal" ]; then
                # conda终端模式下执行
                # 构建不包含外部双引号的命令
                INNER_COMMAND="source \"$CONDA_SH_PATH\" && conda activate \"$script_conda_env_name\" && python \"$SCRIPT_PATH\""
                # NNER_COMMAND 中的所有双引号替换为 AppleScript 可以识别的转义双引号 \"
                # 这会生成一个适合在 AppleScript 中作为字符串内容的值
                ESCAPED_COMMAND=$(echo "$INNER_COMMAND" | sed 's/"/\\"/g')
                callerlog "将在终端中执行的命令 (AppleScript 转义后): /bin/bash -c \"$ESCAPED_COMMAND\""

                osascript <<EOF
tell application "Terminal"
    do script "/bin/bash -c \"$ESCAPED_COMMAND\""
    activate # 激活 Terminal 应用，使其显示在最前面
end tell
EOF
            else
                 # conda静默模式下执行
                if [ -f "$CONDA_SH_PATH" ]; then
                    callerlog "正在 source Conda 初始化脚本: $CONDA_SH_PATH"
                    source "$CONDA_SH_PATH"
                else
                    callerlog "错误: Conda 初始化脚本 '$CONDA_SH_PATH' 未找到。"
                    callerlog "请检查你的 Conda 安装路径，并将其更新到脚本中。"
                    exit 1
                fi
                # 静默模式下，先激活 Conda 环境，再运行 Python 脚本
                conda activate "$script_conda_env_name"
                python "$SCRIPT_PATH"
            fi
        else
            callerlog "Conda 虚拟环境未定义。退出。"
            exit 0
        fi
    fi
else # 如果 ispython 是 False 或者其他非 True 的值，则进入这里
    callerlog "脚本类型: Shell (非 Python)"
    if [ "$runmode_mode" == "terminal" ]; then
         # 终端模式下执行
        osascript <<EOF
tell application "Terminal"
    do script "bash '$SCRIPT_PATH'"
    activate
end tell
EOF
    else
        # 静默模式下执行
        bash "$SCRIPT_PATH"
    fi
fi