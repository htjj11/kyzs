# scr/db.py
import sqlite3
from typing import Any, List, Dict, Optional, Union

import os
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "kyzs.db")
print('已加载sqlLiteExec相对db位置:',DB_PATH)

def sqlite_execute(
        sql: str,
        params: Any = None,
        fetch: str = "all"  # 新增：支持 "all"(默认), "one", "none"
) -> Optional[Union[List[Dict], Dict, None]]:
    """
    万能 SQLite 执行函数（参数化 + 自动返回字典 + 支持 fetchone/fetchall）

    fetch 参数：
        "all"  → 返回 List[Dict]    （默认，适合 SELECT 多行）
        "one"  → 返回单个 Dict 或 None （适合 WHERE id=? 查一行）
        "none" → 不返回数据（适合 INSERT/UPDATE/DELETE）
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # 关键一行！让每行自动变成可按列名访问的字典
        cur = conn.cursor()

        if params is not None:
            if not isinstance(params, (tuple, list, dict)):
                params = (params,)
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        conn.commit()

        if fetch == "none":
            return None
        elif fetch == "one":
            row = cur.fetchone()
            return dict(row) if row else None
        else:  # "all"
            rows = cur.fetchall()
            return [dict(row) for row in rows] if rows else []

    except sqlite3.Error as e:
        print(f"数据库操作失败: {e}")
        print(f"SQL: {sql}")
        print(f"参数: {params}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return None
    finally:
        if conn:
            conn.close()


# ==================== 使用示例（你以后就这么写，太爽了！）====================

if __name__ == '__main__':
    db_path = "../config.db"


    # 2. 读取数据 → 直接得到字典！超爽！
    result = sqlite_execute(
        db_path,
        "SELECT * FROM user_config WHERE id = 1",
    )

    print(result)