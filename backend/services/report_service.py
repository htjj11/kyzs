from core.sqlLiteExec import sqlite_execute
import base64
#修改综述
def modify_review_new_api(review_id: int, review_body: str):
    sqlite_execute(
        "UPDATE review_records SET review_body=? WHERE id=?", (review_body, review_id)
    )
    return 1

#删除综述
def delete_summary(id: int):
    sqlite_execute("DELETE FROM review_records WHERE id=?", (id,))
    return 1
