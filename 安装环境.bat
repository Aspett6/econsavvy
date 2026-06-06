@echo off
chcp 65001 >nul
echo ================================================
echo   经世智用 v3 - 环境安装
echo ================================================
echo.
echo 正在安装依赖，请稍候...
echo.
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo ================================================
echo   安装完成！
echo   下一步：复制 .env.example 为 .env，填入 API Key
echo   然后双击 启动.bat 即可使用
echo ================================================
pause
