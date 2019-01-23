# rinetdweb
rinet代理web界面<br />
使用方法：<br />
在Linux系统输入下面的命令，一行一个：<br />
#安装依赖<br />
yum -y install gcc gcc-c++<br />
#下载rinetd<br />
wget https://boutell.com/rinetd/http/rinetd.tar.gz<br />
#解压<br />
tar -zxvf rinetd.tar.gz<br />
#创建手册目录<br />
mkdir -p /usr/man/man8<br />
#进入目录<br />
cd rinetd<br />
#编译安装<br />
make && make install<br />
#安装python-pip，uwsgi<br />
yum install python-pip python-devel uwsgi<br />
#安装web.py<br />
pip install web.py<br />

#运行程序
git clone 
