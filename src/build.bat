@REM just a file for quickly building.
@REM don't tell me to use cmake.
clang++ -O3 -Wall -shared -std=c++20 cpp_source/*.cpp -o agent_module.pyd -lpython313 -I"C:\Program Files\Python313\include" -I".\venv\Lib\site-packages\pybind11\include" -I".\venv\Include" -L"C:\Program Files\Python313\libs"