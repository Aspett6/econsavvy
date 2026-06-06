@echo off
echo ================================================
echo   ZhiXue CaiJing v5 - Blue Glass Edition
echo ================================================
echo.
python -m pip install streamlit openai jieba python-dotenv fpdf2 -q -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo Starting: http://localhost:8501
echo.
echo ================================================
python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
