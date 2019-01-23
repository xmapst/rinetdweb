# rinetdweb
rinet代理web界面<br />
使用方法：<br />
在Linux系统输入下面的命令，一行一个：<br />
#安装依赖
yum -y install gcc gcc-c++
#下载rinetd
wget https://boutell.com/rinetd/http/rinetd.tar.gz
#解压
tar -zxvf rinetd.tar.gz
#创建手册目录
mkdir -p /usr/man/man8
#进入目录
cd rinetd
#编译安装
make && make install
#安装python-pip，uwsgi
yum install python-pip python-devel uwsgi
#安装web.py
pip install web.py
