# -*- encoding: utf-8 -*-
#-------------------------------------------------#
# Date created          : 2020. 8. 18.
# Date last modified    : 2020. 8. 19.
# Author                : chamadams@gmail.com
# Site                  : http://wandlab.com
# License               : GNU General Public License(GPL) 2.0
# Version               : 0.1.0
# Python Version        : 3.6+
#-------------------------------------------------#

from sls.server import app

version = '0.1.0'

if __name__ == '__main__' :
    
    print('sls_server' + version)
    
    app.run( host='203.253.25.48', port=5000 )