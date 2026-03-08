import pymysql
from dbutils.pooled_db import PooledDB
from app.config import settings


class MysqlClient:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        # PooledDB 在模块加载时创建连接池，避免每次请求重新建连
        # mincached=2 保持 2 个空闲连接，maxconnections=10 限制最大并发连接数
        # blocking=True 表示连接数达上限时排队等待，而不是直接报错
        self._pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=2,
            maxcached=5,
            blocking=True,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def mysql_exec(self, sql: str, params=None):
        """
        执行 SQL 语句，返回 list[dict]；失败返回 0。

        始终使用参数化查询，params 为 tuple 或 list，
        对应 SQL 中的 %s 占位符，由驱动层自动转义，防止 SQL 注入。

        示例：
            db.mysql_exec("SELECT * FROM user WHERE id = %s", (user_id,))
            db.mysql_exec("INSERT INTO label (name) VALUES (%s)", (name,))
        """
        conn = None
        cursor = None
        try:
            conn = self._pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            result = cursor.fetchall()
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"数据库语句执行出现异常: {e}\nSQL: {sql}\nParams: {params}")
            return 0
        finally:
            # 归还连接到池，而非真正关闭
            if cursor:
                cursor.close()
            if conn:
                conn.close()


db = MysqlClient(
    settings.sql_ip,
    settings.sql_port,
    settings.sql_user,
    settings.sql_password,
    settings.sql_database,
)
