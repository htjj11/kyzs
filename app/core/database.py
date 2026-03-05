import pymysql
from app.config import settings


class MysqlClient:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def mysql_exec(self, sentence: str = None):
        """
        执行 SQL 语句，返回 list[dict]；失败返回 0
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cursor.execute(sentence)
            conn.commit()
            result = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"{self.host} 数据库语句执行出现异常: {e}")
            return 0
        return result


db = MysqlClient(
    settings.sql_ip,
    settings.sql_port,
    settings.sql_user,
    settings.sql_password,
    settings.sql_database,
)
