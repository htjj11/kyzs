import pymysql
import sqlite3
import re
import os

# 删除旧的 output.db
db_path = r'C:\Users\shuxi\Desktop\kyzsnew\kyzs\backend\output.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("已删除旧的 output.db")

# MySQL 连接
mysql = pymysql.connect(host='127.0.0.1', user='root', password='Xxzx@123', db='kyzs', charset='utf8mb4')
mysql_cursor = mysql.cursor()

# SQLite 连接
sqlite = sqlite3.connect(db_path)
sqlite_cursor = sqlite.cursor()

# 获取所有表
mysql_cursor.execute("SHOW TABLES")
tables = [row[0] for row in mysql_cursor.fetchall()]

def convert_sql(create_sql):
    create_sql = re.sub(r'`', '"', create_sql)
    create_sql = re.sub(r'CHARACTER SET \w+ COLLATE \w+', '', create_sql)
    create_sql = re.sub(r'COLLATE \w+', '', create_sql)
    create_sql = re.sub(r'CHARACTER SET \w+', '', create_sql)
    create_sql = re.sub(r'USING BTREE', '', create_sql)
    create_sql = re.sub(r'\) ENGINE=.*', ')', create_sql, flags=re.DOTALL)
    create_sql = re.sub(r'\bAUTO_INCREMENT\b', '', create_sql)
    create_sql = re.sub(r'\bUNSIGNED\b', '', create_sql)
    create_sql = re.sub(r"COMMENT\s+'[^']*'", '', create_sql)
    create_sql = re.sub(r',\s*KEY\s+"[^"]*"\s*\([^)]*\)', '', create_sql)
    create_sql = re.sub(r',\s*CONSTRAINT\s+.*?(?=,|\n\s*\))', '', create_sql, flags=re.DOTALL)
    create_sql = re.sub(r'  +', ' ', create_sql)
    return create_sql

for table in tables:
    print(f"正在迁移表: {table}")
    
    mysql_cursor.execute(f"SHOW CREATE TABLE `{table}`")
    create_sql = mysql_cursor.fetchone()[1]
    create_sql = convert_sql(create_sql)
    
    try:
        sqlite_cursor.execute(create_sql)
    except Exception as e:
        print(f"  建表失败: {e}")
        print(f"  SQL:\n{create_sql}")
        continue
    
    mysql_cursor.execute(f"SELECT * FROM `{table}`")
    rows = mysql_cursor.fetchall()
    if rows:
        placeholders = ','.join(['?'] * len(rows[0]))
        sqlite_cursor.executemany(f'INSERT INTO "{table}" VALUES ({placeholders})', rows)
    
    print(f"  完成，共 {len(rows)} 条记录")

sqlite.commit()
mysql.close()
sqlite.close()
print(f"\n迁移完成！输出文件: {db_path}")

# ========== 验证 DB 文件是否正常 ==========
print("\n开始验证 output.db ...")
try:
    # 检查文件是否存在
    if not os.path.exists(db_path):
        print("❌ 文件不存在！")
    else:
        size = os.path.getsize(db_path)
        print(f"✅ 文件存在，大小: {size} 字节")

    # 检查文件头（SQLite文件前16字节应为 'SQLite format 3'）
    with open(db_path, 'rb') as f:
        header = f.read(16)
    if header[:15] == b'SQLite format 3':
        print("✅ 文件头验证通过，是合法的 SQLite 文件")
    else:
        print(f"❌ 文件头异常: {header}")

    # 尝试连接并查询所有表
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables_in_db = cur.fetchall()
    print(f"✅ 成功连接，共有 {len(tables_in_db)} 张表:")
    for t in tables_in_db:
        cur.execute(f'SELECT COUNT(*) FROM "{t[0]}"')
        count = cur.fetchone()[0]
        print(f"   - {t[0]}: {count} 条记录")
    conn.close()

except Exception as e:
    print(f"❌ 验证失败: {e}")