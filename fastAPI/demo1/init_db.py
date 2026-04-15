import sqlite3
import os

# 获取数据库路径
db_path = os.path.join(os.path.dirname(__file__), 'demo1.db')
print(f"Creating database at: {db_path}")

# 连接数据库（如果不存在会自动创建）
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建项目表
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        项目名称 TEXT NOT NULL,
        申请原因 TEXT NOT NULL,
        预计完成时间 TEXT NOT NULL,
        申请经理 TEXT NOT NULL,
        状态 TEXT NOT NULL DEFAULT '待审核',
        申请时间 TEXT NOT NULL,
        批复意见 TEXT,
        批复时间 TEXT
    )
    ''')
    
    # 插入示例数据
    sample_data = [
        (
            '透明化管理系统开发',
            '为了提升项目管理透明度，开发一套透明化管理系统',
            '2024-12-31',
            'John',
            '已审核',
            '2024-11-01T10:00:00',
            '同意开发',
            '2024-11-02T14:30:00'
        ),
        (
            '数据可视化功能',
            '添加数据可视化图表功能，提升数据分析能力',
            '2024-12-15',
            'John',
            '待审核',
            '2024-11-10T09:00:00',
            None,
            None
        )
    ]
    
    cursor.executemany('''
    INSERT INTO team_projects (项目名称, 申请原因, 预计完成时间, 申请经理, 状态, 申请时间, 批复意见, 批复时间)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    print("Database created successfully!")
    print("Sample data inserted successfully!")
    
    # 验证数据
    cursor.execute('SELECT * FROM team_projects')
    projects = cursor.fetchall()
    print(f"Total projects: {len(projects)}")
    for project in projects:
        print(f"Project: {project[1]}, Status: {project[5]}")
        
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
    print("Database connection closed.")