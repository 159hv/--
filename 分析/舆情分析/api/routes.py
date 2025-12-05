from flask_restful import Resource, reqparse
from flask import jsonify, current_app
from app import db
from app.models import Topic, Keyword, User, Role
from datetime import datetime
from flask_login import current_user, login_required

# 解析参数
parser = reqparse.RequestParser()
parser.add_argument('title', type=str, help='舆情标题')
parser.add_argument('content', type=str, help='舆情内容')
parser.add_argument('source', type=str, help='信息来源')
parser.add_argument('url', type=str, help='信息链接')
parser.add_argument('published_at', type=str, help='发布时间')
parser.add_argument('sentiment', type=float, help='情感得分')

class TopicList(Resource):
    """舆情列表接口"""
    def get(self):
        """获取舆情列表，支持分页"""
        # 获取分页参数
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, help='页码')
        parser.add_argument('page_size', type=int, default=10, help='每页数量')
        args = parser.parse_args()
        
        page = args['page']
        page_size = args['page_size']
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取总记录数
        total = Topic.query.count()
        
        # 获取分页数据
        topics = Topic.query.order_by(Topic.published_at.desc()).offset(offset).limit(page_size).all()
        
        # 构造响应数据
        result = {
            'items': [],
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size  # 总页数
        }
        
        for topic in topics:
            topic_data = {
                'id': topic.id,
                'title': topic.title,
                'content': topic.content,
                'source': topic.source,
                'url': topic.url,
                'published_at': topic.published_at.isoformat(),
                'created_at': topic.created_at.isoformat(),
                'sentiment': topic.sentiment
            }
            result['items'].append(topic_data)
        
        return jsonify(result)
    
    def post(self):
        """创建新舆情"""
        args = parser.parse_args()
        
        # 处理发布时间
        published_at = datetime.utcnow()
        if args['published_at']:
            published_at = datetime.fromisoformat(args['published_at'])
        
        new_topic = Topic(
            title=args['title'],
            content=args['content'],
            source=args['source'],
            url=args['url'],
            published_at=published_at,
            sentiment=args['sentiment']
        )
        
        db.session.add(new_topic)
        db.session.commit()
        
        return jsonify({'message': '舆情创建成功', 'id': new_topic.id}), 201

class TopicDetail(Resource):
    """舆情详情接口"""
    def get(self, topic_id):
        """获取单个舆情详情"""
        topic = Topic.query.get_or_404(topic_id)
        topic_data = {
            'id': topic.id,
            'title': topic.title,
            'content': topic.content,
            'source': topic.source,
            'url': topic.url,
            'published_at': topic.published_at.isoformat(),
            'created_at': topic.created_at.isoformat(),
            'sentiment': topic.sentiment
        }
        return jsonify(topic_data)
    
    def put(self, topic_id):
        """更新舆情"""
        args = parser.parse_args()
        topic = Topic.query.get_or_404(topic_id)
        
        # 更新字段
        if args['title']: topic.title = args['title']
        if args['content']: topic.content = args['content']
        if args['source']: topic.source = args['source']
        if args['url']: topic.url = args['url']
        if args['published_at']: 
            topic.published_at = datetime.fromisoformat(args['published_at'])
        if args['sentiment'] is not None: topic.sentiment = args['sentiment']
        
        db.session.commit()
        return jsonify({'message': '舆情更新成功'})
    
    def delete(self, topic_id):
        """删除舆情"""
        topic = Topic.query.get_or_404(topic_id)
        db.session.delete(topic)
        db.session.commit()
        return jsonify({'message': '舆情删除成功'})

class KeywordList(Resource):
    """关键词列表接口"""
    def get(self):
        """获取关键词列表"""
        keywords = Keyword.query.all()
        result = [{'id': keyword.id, 'word': keyword.word, 'created_at': keyword.created_at.isoformat()} for keyword in keywords]
        return jsonify(result)

class UserList(Resource):
    """用户列表接口"""
    @login_required
    def get(self):
        """获取用户列表，支持分页和搜索"""
        # 检查用户是否为管理员
        if not current_user.is_admin:
            return jsonify({'code': 403, 'msg': '权限不足'}), 403
        # 获取分页和搜索参数，明确指定参数来源为查询字符串
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, help='页码', location='args')
        parser.add_argument('limit', type=int, default=10, help='每页数量', location='args')
        parser.add_argument('search_username', type=str, help='用户名搜索', location='args')
        args = parser.parse_args()
        
        page = args['page']
        limit = args['limit']
        search_username = args['search_username']
        
        # 构建查询
        query = User.query
        
        # 添加搜索条件
        if search_username:
            query = query.filter(User.username.like(f'%{search_username}%'))
        
        # 分页查询
        pagination = query.order_by(User.id.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        # 构造响应数据
        result = {
            'code': 0,
            'msg': '',
            'count': pagination.total,
            'data': []
        }
        
        for user in pagination.items:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role_id': user.role_id,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': user.status
            }
            result['data'].append(user_data)
        
        return jsonify(result)
    
    @login_required
    def post(self):
        """创建新用户"""
        # 检查用户是否为管理员
        if not current_user.is_admin:
            return jsonify({'code': 403, 'msg': '权限不足'}), 403
            
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='用户名', location='json')
        parser.add_argument('password', type=str, required=True, help='密码', location='json')
        parser.add_argument('email', type=str, required=True, help='邮箱', location='json')
        parser.add_argument('role_id', type=int, default=2, help='角色ID', location='json')
        args = parser.parse_args()
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=args['username']).first():
            return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=args['email']).first():
            return jsonify({'code': 400, 'msg': '邮箱已存在'}), 400
            
        # 创建新用户
        try:
            new_user = User(
                username=args['username'],
                password=args['password'],  # 密码会自动哈希
                email=args['email'],
                role_id=args['role_id']
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'code': 0, 'msg': '用户创建成功', 'data': {'id': new_user.id}}), 201
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建用户失败: {str(e)}")
            return jsonify({'code': 500, 'msg': '创建用户失败'}), 500

class UserDetail(Resource):
    """用户详情接口"""
    @login_required
    def put(self, user_id):
        """更新用户信息"""
        # 检查用户是否为管理员
        if not current_user.is_admin:
            return jsonify({'code': 403, 'msg': '权限不足'}), 403
            
        # 查找用户
        user = User.query.get_or_404(user_id)
        
        # 解析参数
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, help='用户名', location='json')
        parser.add_argument('email', type=str, help='邮箱', location='json')
        parser.add_argument('role_id', type=int, help='角色ID', location='json')
        parser.add_argument('password', type=str, help='密码', location='json')
        parser.add_argument('status', type=bool, help='用户状态', location='json')
        args = parser.parse_args()
        
        try:
            # 更新用户信息
            if args['username']:
                # 检查用户名是否已被其他用户使用
                existing_user = User.query.filter_by(username=args['username']).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({'code': 400, 'msg': '用户名已存在'}), 400
                user.username = args['username']
                
            if args['email']:
                # 检查邮箱是否已被其他用户使用
                existing_user = User.query.filter_by(email=args['email']).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({'code': 400, 'msg': '邮箱已存在'}), 400
                user.email = args['email']
                
            if args['role_id'] is not None:
                user.role_id = args['role_id']
                
            if args['password']:
                user.password = args['password']  # 密码会自动哈希
                
            if args['status'] is not None:
                user.status = args['status']
                
            db.session.commit()
            return jsonify({'code': 0, 'msg': '用户信息更新成功'}), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新用户信息失败: {str(e)}")
            return jsonify({'code': 500, 'msg': '更新用户信息失败'}), 500
    
    @login_required
    def delete(self, user_id):
        """删除用户"""
        # 检查用户是否为管理员
        if not current_user.is_admin:
            return jsonify({'code': 403, 'msg': '权限不足'}), 403
            
        # 查找用户
        user = User.query.get_or_404(user_id)
        
        # 不允许删除自己
        if user.id == current_user.id:
            return jsonify({'code': 400, 'msg': '不能删除自己'}), 400
            
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'code': 0, 'msg': '用户删除成功'}), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除用户失败: {str(e)}")
            return jsonify({'code': 500, 'msg': '删除用户失败'}), 500

# 注册路由
def register_routes(api):
    """注册所有API路由"""
    api.add_resource(TopicList, '/api/topics')
    api.add_resource(TopicDetail, '/api/topics/<int:topic_id>')
    api.add_resource(KeywordList, '/api/keywords')
    api.add_resource(UserList, '/api/v1/users')
    api.add_resource(UserDetail, '/api/v1/users/<int:user_id>')
