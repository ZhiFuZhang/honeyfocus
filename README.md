# honeyfocus
centos7
0.pip
 yum -y install epel-release
 yum -y install python-pip
 pip install --upgrade pip

1. pip tornado, pycurl, sqlalchemy

2.nginx
rpm -Uvh  http://nginx.org/packages/centos/7/noarch/RPMS/nginx-release-centos-7-0.el7.ngx.noarch.rpm
yum install nginx


3 firewall
http://www.centoscn.com/CentOS/help/2015/0208/4667.html
config firewall
firewall-cmd --zone=public --permanent --add-port=80/tcp

4. mysql
rpm -ivh  http://dev.mysql.com/get/mysql-community-release-el7-5.noarch.rpm
yum install mysql
yum install mysql-server
5. 
 failed (13: Permission denied) while connecting to upstream,

#setsebool -P httpd_can_network_connect 1   ( getsebool -a   Show all SELinux booleans.)
OR
you can turn off the SElinux