from app import create_app, db
from app.models.models import User, Role
import os
import logging

# 从环境变量获取配置名称，默认使用开发环境
config_name = os.getenv('FLASK_CONFIG', 'development')

# 创建应用实例
app = create_app(config_name=config_name)

# 命令行上下文处理器
@app.shell_context_processor
def make_shell_context():
    return {'app': app, 'db': db, 'User': User}

# 初始化数据库
@app.cli.command()
def initdb():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        logging.info('数据库初始化完成！')
        print('数据库初始化完成！')
        
        # 检查是否已存在角色
        admin_role = Role.query.filter_by(name='admin').first()
        user_role = Role.query.filter_by(name='user').first()
        
        if not admin_role:
            logging.info("创建管理员角色...")
            print("创建管理员角色...")
            admin_role = Role(name='admin', description='管理员角色')
            db.session.add(admin_role)
        else:
            logging.info("管理员角色已存在")
            print("管理员角色已存在")
        
        if not user_role:
            logging.info("创建普通用户角色...")
            print("创建普通用户角色...")
            user_role = Role(name='user', description='普通用户角色')
            db.session.add(user_role)
        else:
            logging.info("普通用户角色已存在")
            print("普通用户角色已存在")
        
        db.session.commit()
        
        # 检查是否已存在管理员用户
        logging.info("检查并创建默认管理员用户...")
        print("检查并创建默认管理员用户...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            logging.info("创建管理员用户...")
            print("创建管理员用户...")
            admin_user = User(
                username='admin',
                password='admin123',  # 密码会通过密码设置器自动哈希
                email='admin@example.com',
                role_id=admin_role.id
            )
            db.session.add(admin_user)
            db.session.commit()
            logging.info('默认管理员用户创建完成：用户名：admin，密码：admin123')
            print('默认管理员用户创建完成：\n用户名：admin\n密码：admin123')
        else:
            logging.info("管理员用户已存在")
            print("管理员用户已存在")

def init_database():
    """初始化数据库和默认用户"""
    with app.app_context():
        db.create_all()
        logging.info("数据库表创建完成")
        
        # 创建默认角色和管理员用户
        logging.info("开始创建默认角色和管理员用户...")
        print("开始创建默认角色和管理员用户...")
        
        # 检查是否已存在角色
        admin_role = Role.query.filter_by(name='admin').first()
        user_role = Role.query.filter_by(name='user').first()
        
        if not admin_role:
            logging.info("创建管理员角色...")
            print("创建管理员角色...")
            admin_role = Role(name='admin', description='管理员角色')
            db.session.add(admin_role)
        else:
            logging.info("管理员角色已存在")
            print("管理员角色已存在")
        
        if not user_role:
            logging.info("创建普通用户角色...")
            print("创建普通用户角色...")
            user_role = Role(name='user', description='普通用户角色')
            db.session.add(user_role)
        else:
            logging.info("普通用户角色已存在")
            print("普通用户角色已存在")
        
        db.session.commit()
        
        # 检查是否已存在管理员用户
        logging.info("检查并创建默认管理员用户...")
        print("检查并创建默认管理员用户...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            logging.info("创建管理员用户...")
            print("创建管理员用户...")
            admin_user = User(
                username='admin',
                password='admin123',  # 密码会通过密码设置器自动哈希
                email='admin@example.com',
                role_id=admin_role.id
            )
            db.session.add(admin_user)
            db.session.commit()
            logging.info('默认管理员用户创建完成：用户名：admin，密码：admin123')
            print('默认管理员用户创建完成：\n用户名：admin\n密码：admin123')
        else:
            logging.info("管理员用户已存在")
            print("管理员用户已存在")

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 从环境变量获取端口，默认使用5000
    port = int(os.getenv('FLASK_PORT', 5000))
    
    # 从环境变量获取是否开启调试模式
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    logging.info(f"应用启动，配置：{config_name}，端口：{port}，调试模式：{debug}")
    print(f"应用启动，配置：{config_name}，端口：{port}，调试模式：{debug}")
    
    # 启动应用
    app.run(debug=debug, port=port)
