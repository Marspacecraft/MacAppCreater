#include <mach-o/dyld.h>
#include <libgen.h>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/ini_parser.hpp>
#include <iostream>
#include <string>
// g++ Caller.cpp -I/opt/homebrew/include -L/opt/homebrew/lib -lboost_system -o Caller


struct config
{
    bool launchermode;        // 表示启动模式是否启用 (True/False)
    bool ispython;            // 表示是否为 Python 脚本 (True/False)
    bool python_local;        // 表示 Python 环境是否为本地环境 (True/False)
    bool runmode_terminal;    // 开启终端运行
    std::string python_param; // 存储 Python 相关的参数

} 
sg_config =
{
    .launchermode=false,
    .ispython=false,
    .python_local=true,
    .runmode_terminal=true,
    .python_param=std::string("")
};
std::string sg_CallerPath = "";

std::string getExecutablePath()
{
    uint32_t size = 0;
    _NSGetExecutablePath(NULL, &size);
    char *buf = new char[size];
    _NSGetExecutablePath(buf, &size);
    std::string path = buf;
    delete[] buf;
    // 去掉可执行文件名，得到目录
    char *dirc = strdup(path.c_str());
    std::string dir = dirname(dirc);
    free(dirc);
    return dir;
}

//std::string getExecutablePath()
//{
//    char buf[PATH_MAX];
//    if (getcwd(buf, sizeof(buf)) != NULL)
//    {
//        std::cout << "Current working directory: " << buf << std::endl;
//        return buf;
//    }
//    else
//    {
//        perror("getcwd() error");
//    }
//    return ""; // 失败返回空
//}

bool parserini()
{
	boost::property_tree::ptree pt;
    std::string configPath = sg_CallerPath + "/../Resources/config.ini"; 

    try 
    {
        // 读取INI文件
        boost::property_tree::ini_parser::read_ini(configPath, pt);

        // --- 访问配置数据 ---

        // 访问 'launchermode' 部分
        // 使用 get_optional 可以安全地获取值，如果不存在则返回一个空 optional
        boost::optional<std::string> launchermode_enabled = pt.get_optional<std::string>("launchermode.enabled");
        if (launchermode_enabled) 
        {
            std::cout << "launchermode enabled: " << *launchermode_enabled << std::endl;

            // 如果 launchermode.enabled 为 False，则访问 runmode
            if (*launchermode_enabled == "False") 
            {
                sg_config.launchermode = false;
                boost::optional<std::string> runmode_mode = pt.get_optional<std::string>("runmode.mode");
                if (*runmode_mode == "silent") 
                {
                    std::cout << "runmode mode: " << *runmode_mode << std::endl;
                    sg_config.runmode_terminal = false;
                } 
            }
            else
                sg_config.launchermode = true;
        } 
        else 
        {
            std::cout << "launchermode enabled: 未找到" << std::endl;
            return false;
        }


        // 访问 'script' 部分
        boost::optional<std::string> script_ispython = pt.get_optional<std::string>("script.ispython");
        if (script_ispython) 
        {
            std::cout << "script ispython: " << *script_ispython << std::endl;

            if (*script_ispython == "True") 
            {
                sg_config.ispython = true;
                boost::optional<std::string> python_env_type = pt.get_optional<std::string>("script.python_env_type");
                if (python_env_type) 
                {
                    std::cout << "script python_env_type: " << *python_env_type << std::endl;

                    if (*python_env_type == "local") 
                    {
                        boost::optional<std::string> python_executable = pt.get_optional<std::string>("script.python_executable");
                        if (python_executable) 
                        {
                            sg_config.python_param = *python_executable;
                            std::cout << "script python_executable: " << *python_executable << std::endl;
                        } 
                        else 
                        {
                            std::cout << "script python_executable: 未找到" << std::endl;
                            return false;
                        }
                    } 
                    else if (*python_env_type == "conda") 
                    {
                        boost::optional<std::string> conda_env_name = pt.get_optional<std::string>("script.conda_env_name");
                        if (conda_env_name) 
                        {
                            sg_config.python_param = *conda_env_name;
                            std::cout << "script conda_env_name: " << *conda_env_name << std::endl;
                        } 
                        else 
                        {
                            std::cout << "script conda_env_name: 未找到" << std::endl;
                            return false;
                        }
                    }
                } 
                else 
                {
                    std::cout << "script python_env_type: 未找到" << std::endl;
                    return false;
                }
            }
        } 
        else 
        {
            std::cout << "script ispython: 未找到" << std::endl;
            return false;
        }

    } 
    catch (const boost::property_tree::ini_parser_error& e) 
    {
        std::cerr << "INI 文件解析错误: " << e.what() << std::endl;
        return false;
    } 
    catch (const std::exception& e)
    {
        std::cerr << "发生未知错误: " << e.what() << std::endl;
        return false;
    }

    return true;
}

void runCmd(const std::string& cmd) 
{
    std::cout << "\nRunning script with interpreter: " << cmd << std::endl;
    int result_interpret = system(cmd.c_str());
}

void runScriptWithTerminal(const std::string& script_name) 
{
    // 构建脚本的完整路径（AppleScript需要完整路径）
    // 注意：如果脚本路径中包含空格或其他特殊字符，需要进行适当的转义。
    // 在这里，我们假设脚本名不包含特殊字符。
    std::string full_script_path = sg_CallerPath + "/" + script_name;

    // AppleScript 命令
    // 'tell application "Terminal"' 告诉 Terminal 应用程序
    // 'do script "..." in window 0' 在第一个窗口中执行脚本（如果已经有打开的窗口）
    // 或者 'do script "..."' 会在新窗口中执行
    // 注意双引号的转义：AppleScript 字符串内部的引号需要用 \ 来转义。
    // 'read -p ""' 在脚本末尾等待用户输入，以防止终端立即关闭
    std::string apple_script_command = "osascript -e 'tell application \"Terminal\" to do script \"" +
    full_script_path +  "; exit\"'"; //

    runCmd(apple_script_command);
}


void startlauncher()
{

}

void startscript()
{
    if(sg_config.ispython)
    {

    }
    else
    {
        if(sg_config.runmode_terminal)
            runScriptWithTerminal("./Callor");
        else    
            runCmd("./Callor");
    }
}


int main()
{
    sg_CallerPath = getExecutablePath();
    if (!parserini())
        return 1;

    std::cout << "是否启动加载器:" << sg_config.launchermode << std::endl;
    std::cout << "是否是python:" << sg_config.ispython << std::endl;
    std::cout << "是否是本地python:" << sg_config.python_local << std::endl;
    std::cout << "python 参数:" << sg_config.python_param << std::endl;
    std::cout << "是否启动终端:" << sg_config.runmode_terminal << std::endl;

    if (sg_config.launchermode)
        startlauncher();
    else
        startscript();

    return 0;
}