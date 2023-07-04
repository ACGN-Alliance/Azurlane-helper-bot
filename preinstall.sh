#!/bin/bash
echo 准备安装AZbot, 请确保网络通畅, 请等待3s
sleep 3s

# 检测是否有git
if [ -x "$(command -v git)" ]; then
    echo 检测到 git 环境, 开始clone仓库, 如果速度过慢请使用 git config 配置代理
else
    echo 没有检测到 git 环境, 安装终止
    exit 0
fi

read -p "请选择安装的版本 [release(default) | main | dev] " -n 10 -r -a install_mode
if [ -z "${install_mode[*]}" ]; then
    install_mode=(release)
fi
read -p "是否使用ghproxy加速下载? [y(default)/n]" -n 1 -r -a is_ghproxy
if [ -z "${is_ghproxy[*]}" ]; then
    is_ghproxy=(y)
fi

if [[ ${install_mode[*]} =~ release ]]; then
    echo 正在安装 release 版本
    if [[ ${is_ghproxy[*]} =~ ^[Yy]$ ]]; then
        current_release_url=$(curl -sL https://ghproxy.com/https://api.github.com/repos/ACGN-Alliance/Azurlane-helper-bot/releases/latest | grep "browser_download_url.*zip" | cut -d '"' -f 4)
    else
        current_release_url=$(curl -sL https://api.github.com/repos/ACGN-Alliance/Azurlane-helper-bot/releases/latest | grep "browser_download_url.*zip" | cut -d '"' -f 4)
    fi  # TODO 待商议
    curl --request GET -sL \
         --url "${current_release_url}"\
         --output '.' &&
        tar -zxvf Azurlane-helper-bot-*.tar.gz &&
        mv Azurlane-helper-bot-*/ Azurlane-helper-bot &&
        rm -rf Azurlane-helper-bot-*.tar.gz &&
        cd Azurlane-helper-bot || exit 2
elif [[ ${install_mode[*]} =~ main ]]; then
    echo 正在安装 main 版本
    if [[ ${is_ghproxy[*]} =~ ^[Yy]$ ]]; then
        git clone https://ghproxy.com/https://github.com/ACGN-Alliance/Azurlane-helper-bot
    else
        git clone https://github.com/ACGN-Alliance/Azurlane-helper-bot
    fi
elif [[ ${install_mode[*]} =~ dev ]]; then
    echo 正在安装 dev 版本
    if [[ ${is_ghproxy[*]} =~ ^[Yy]$ ]]; then
      git clone https://ghproxy.com/https://github.com/ACGN-Alliance/Azurlane-helper-bot -b dev --single-branch
    else
      git clone https://github.com/ACGN-Alliance/Azurlane-helper-bot -b dev --single-branch
    fi
fi

cd Azurlane-helper-bot || exit 2

# 检测环境变量是否有 pdm 或 poetry
if [ -x "$(command -v pdm)" ]; then
    echo 检测到 pdm 环境
    env="pdm"
elif [ -x "$(command -v poetry)" ]; then
    echo 检测到 poetry 环境
    env="poetry"
else
    echo 没有检测到 pdm 或 poetry 环境, 开始安装 pdm

    # 询问是否需要安装poetry
    read -p "是否安装 poetry? [y(default)/n] " -n 1 -r -a need_to_install
    if [ -z "${need_to_install[*]}" ]; then
        need_to_install=(y)
    fi

    if [[ ${need_to_install[0]} =~ ^[Yy]$ ]]; then
        echo 正在安装 poetry...
        python3 -m pip install poetry
        env="poetry"
    else
        echo 无 poetry 环境, 安装终止
        exit 0
    fi
fi
sleep 3s

# 配置pdm与poetry
if [ ${env} == "pdm" ]; then
    echo 使用 pdm 安装依赖
    pdm venv create --name azbot --with-pip 3.10
    pdm venv activate azbot
elif [ ${env} == "poetry" ]; then
    echo 使用 poetry 安装依赖
    poetry env use 3.10
    poetry shell
fi

${env} install

read -p "是否需要安装 nonebot-plugin-gocqhttp? [y/n(default)] " -n 1 -r -a install_gocq
  if [ -z "${install_gocq[*]}" ]; then
      install_gocq=(n)
  fi
if [[ ${install_gocq[0]} =~ ^[Yy]$ ]]; then
    echo 正在安装 nonebot-plugin-gocqhttp...
    pip install nonebot-plugin-gocqhttp
fi

echo 安装全部完成, 请修改config.yaml文件适应自己的需求, 完成后请输入 nb run --reload 启动