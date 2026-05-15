"""
第一步：探索 Hive 表结构，找到蓝牙回连相关的表
运行：python hive_explore.py
"""

from pyhive import hive
import pandas as pd

# ── 连接配置 ──────────────────────────────────────────
HOST     = "172.21.80.71"
PORT     = 7001
USERNAME = "hue"
PASSWORD = "Disifanshi123!"
AUTH     = "CUSTOM"
# ─────────────────────────────────────────────────────

def get_conn(database="default"):
    return hive.Connection(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        auth=AUTH,
        database=database,
        configuration={"hive.execution.engine": "tez"},
    )

def query(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [c[0] for c in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=cols)

def main():
    print("正在连接 Hive 国内...")
    conn = get_conn()
    print("连接成功！\n")

    # 1. 列出所有数据库
    print("=" * 60)
    print("【所有数据库】")
    dbs = query(conn, "SHOW DATABASES")
    print(dbs.to_string(index=False))

    # 2. 在每个库里搜索含蓝牙/bluetooth/bt关键字的表
    keywords = ["blue", "bt", "ble", "bluetooth", "蓝牙", "reconnect",
                "connect", "device", "app_log", "event"]

    found_tables = []
    for db in dbs.iloc[:, 0].tolist():
        try:
            conn_db = get_conn(database=db)
            tables = query(conn_db, "SHOW TABLES")
            for tbl in tables.iloc[:, 0].tolist():
                for kw in keywords:
                    if kw.lower() in tbl.lower():
                        found_tables.append({"database": db, "table": tbl})
                        break
            conn_db.close()
        except Exception as e:
            print(f"  跳过 {db}: {e}")

    print("\n" + "=" * 60)
    print("【疑似相关的表（含蓝牙/连接/设备/日志关键字）】")
    if found_tables:
        df = pd.DataFrame(found_tables)
        print(df.to_string(index=False))
    else:
        print("未自动匹配到，尝试手动列出所有表...")
        # fallback：列出 default 库所有表
        all_tables = query(conn, "SHOW TABLES")
        print(all_tables.to_string(index=False))

    # 3. 对找到的表，打印前几列的字段名
    print("\n" + "=" * 60)
    print("【各表字段预览】")
    for item in found_tables[:10]:  # 最多看10张表
        try:
            conn_db = get_conn(database=item["database"])
            desc = query(conn_db, f"DESCRIBE {item['table']}")
            print(f"\n▶ {item['database']}.{item['table']}")
            print(desc[["col_name", "data_type"]].to_string(index=False))
            conn_db.close()
        except Exception as e:
            print(f"  {item['database']}.{item['table']} 描述失败: {e}")

    conn.close()
    print("\n探索完成，请把上面的表名/字段名发给我，我来写正式查询。")

if __name__ == "__main__":
    main()
