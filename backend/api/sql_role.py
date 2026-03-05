
import pymysql
from config import *

class mysqlRole:
    #一个mysql的对象，通过参数构建数据库地址、端口、用户名等
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """
        :param host: 数据库服务器地址
        :param port: 端口号
        :param user: 用户名
        :param password: 密码
        :param database: 数据库
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def mysql_exec(self, sentence: str = None):
        '''
        1参数是需要查询的语句
        返回的是list中嵌套dict
        '''
        try:
            mysql_conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                         database=self.database)
            mysql_cursor = mysql_conn.cursor(cursor=pymysql.cursors.DictCursor)  #设置游标，且返回格式为字典（键值对）
            mysql_cursor.execute(sentence)
            mysql_conn.commit()
            result = mysql_cursor.fetchall()
            mysql_cursor.close()
            mysql_conn.close()
        except Exception as e:
            print(f"{self.host}数据库语句执行出现异常:{e}")
            return 0
        return result

kyzs_sql = mysqlRole(sql_ip,sql_port,sql_user,sql_password,sql_database)