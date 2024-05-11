#!/bin/bash

# 切换到指定目录
cd /home/用户名/domains || exit

# 运行Python脚本
python auto-pm2-renewal.py