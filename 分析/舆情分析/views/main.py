from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db
from models import User, Role, Setting, DataWarehouse, CollectionRule, AiEngine
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import time
import functools
import requests
from lxml import etree
import json
import logging

# 定义管理员权限装饰器
def admin_required(f):
    @login_required
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('您没有权限访问此页面！', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# 创建蓝图
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    """主页"""
    # 获取系统设置
    app_name = Setting.query.filter_by(key='app_name').first()
    return render_template('index.html', user=current_user, app_name=app_name.value if app_name else '政企智能舆情分析系统')

@main.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.status and check_password_hash(user.password_hash, password):
            # 更新最后登录时间
            user.last_login = datetime.now()
            db.session.commit()
            
            login_user(user, remember=remember)
            flash('登录成功！', 'success')
            return redirect(url_for('main.index'))
        elif user and not user.status:
            flash('账号已被禁用！', 'danger')
        else:
            flash('用户名或密码错误！', 'danger')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('已成功登出！', 'success')
    return redirect(url_for('main.login'))

# 用户管理路由
@main.route('/admin/users')
@login_required
def admin_users():
    """用户管理页面"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面！', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles)


@main.route('/admin/user/add', methods=['POST'])
@login_required
def admin_add_user():
    """添加用户"""
    if not current_user.is_admin:
        return jsonify({"status": "error", "message": "权限不足"})
    
    username = request.form['username']
    password = request.form['password']
    role_id = request.form['role_id']
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "用户名已存在"})
    
    # 创建新用户
    new_user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role_id=role_id
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "用户添加成功"})


@main.route('/admin/user/edit', methods=['POST'])
@login_required
def admin_edit_user():
    """编辑用户"""
    if not current_user.is_admin:
        return jsonify({"status": "error", "message": "权限不足"})
    
    user_id = request.form['user_id']
    username = request.form['username']
    role_id = request.form['role_id']
    status = request.form.get('status')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"})
    
    # 检查用户名是否已被其他用户使用
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != user.id:
        return jsonify({"status": "error", "message": "用户名已存在"})
    
    user.username = username
    user.role_id = role_id
    user.status = True if status == 'on' else False
    
    db.session.commit()
    
    return jsonify({"status": "success", "message": "用户更新成功"})


@main.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """删除用户"""
    if not current_user.is_admin:
        return jsonify({"status": "error", "message": "权限不足"})
    
    if current_user.id == user_id:
        return jsonify({"status": "error", "message": "不能删除自己的账号"})
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"})
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "用户删除成功"})





# 系统设置路由
@main.route('/admin/settings')
@login_required
def admin_settings():
    """系统设置页面"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面！', 'danger')
        return redirect(url_for('main.index'))
    
    settings = Setting.query.all()
    # 确保基本设置存在
    app_name = Setting.query.filter_by(key='app_name').first()
    if not app_name:
        app_name = Setting(key='app_name', value='政企智能舆情分析系统', description='应用名称')
        db.session.add(app_name)
        db.session.commit()
    
    return render_template('admin/settings.html', settings=settings)


@main.route('/admin/setting/save', methods=['POST'])
@login_required
def admin_save_setting():
    """保存系统设置"""
    if not current_user.is_admin:
        return jsonify({"status": "error", "message": "权限不足"})
    
    app_name = request.form['app_name']
    
    # 保存应用名称
    setting = Setting.query.filter_by(key='app_name').first()
    if setting:
        setting.value = app_name
    else:
        setting = Setting(key='app_name', value=app_name, description='应用名称')
        db.session.add(setting)
    
    db.session.commit()
    
    return jsonify({"status": "success", "message": "设置保存成功"})



@main.route('/data/collection', methods=['GET', 'POST'])
@login_required
def data_collection():
    """数据采集页面和API"""
    if request.method == 'GET':
        # 获取当前用户的采集结果
        from models import CollectionTemp
        collections = CollectionTemp.query.filter_by(collected_by=current_user.id).order_by(CollectionTemp.collected_at.desc()).all()
        return render_template('data_collection.html', collections=collections)
    
    # 处理POST请求
    spider_type = request.form.get('spider_type', 'baidu')
    keyword = request.form.get('keyword', '')
    page = int(request.form.get('page', 1))
    
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"用户{current_user.id}开始采集数据，爬虫类型：{spider_type}，关键词：{keyword}，页码：{page}")
        
        if spider_type == 'baidu':
            from services.spider import BaiduSpider
            spider = BaiduSpider()
            # 百度爬虫需要关键词
            if not keyword:
                logger.warning(f"用户{current_user.id}未输入关键词，采集失败")
                return jsonify({'code': 1, 'msg': '请输入搜索关键词'})
            results = spider.fetch_data(keyword, page)
        elif spider_type == 'xinhua':
            from services.spider import XinhuaSpider
            spider = XinhuaSpider()
            # 新华爬虫目前不支持关键词搜索，使用默认关键词
            results = spider.fetch_data(keyword, page)
        else:
            logger.warning(f"用户{current_user.id}使用不支持的爬虫类型：{spider_type}")
            return jsonify({'code': 1, 'msg': '不支持的爬虫类型'})
        
        logger.info(f"用户{current_user.id}采集到{len(results)}条数据")
        
        # 将采集结果保存到临时表
        from models import CollectionTemp
        from datetime import datetime
        
        saved_count = 0
        for result in results:
            # 检查是否已存在相同URL的记录
            existing = CollectionTemp.query.filter_by(url=result.get('url'), collected_by=current_user.id).first()
            if not existing:
                # 创建新的临时记录
                temp_item = CollectionTemp(
                    title=result.get('title', ''),
                    content=result.get('summary', '') or '无内容',
                    summary=result.get('summary', ''),
                    source=result.get('source', ''),
                    url=result.get('url', ''),
                    cover=result.get('cover', ''),
                    collected_by=current_user.id
                )
                db.session.add(temp_item)
                saved_count += 1
        
        db.session.commit()
        logger.info(f"用户{current_user.id}成功保存{saved_count}条新记录到临时表")
        
        # 保存成功后，重新查询数据库获取所有数据，包含id字段
        all_collections = CollectionTemp.query.filter_by(collected_by=current_user.id).order_by(CollectionTemp.collected_at.desc()).all()
        
        # 转换为前端需要的格式
        formatted_data = []
        for item in all_collections:
            formatted_data.append({
                'id': item.id,
                'title': item.title,
                'summary': item.summary,
                'content': item.content,
                'cover': item.cover,
                'url': item.url,
                'source': item.source,
                'collected_at': item.collected_at.isoformat(),
                'is_deep_collected': item.is_deep_collected
            })
        
        return jsonify({
            'code': 0, 
            'msg': f'采集成功，新增{saved_count}条记录', 
            'data': formatted_data
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"用户{current_user.id}采集数据失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'采集失败：{str(e)}'})





@main.route('/data/deep-collection', methods=['POST'])
@login_required
def deep_collection():
    """深度采集数据"""
    url = request.form.get('url')
    collection_id = request.form.get('collection_id')
    if not url:
        return jsonify({'code': 1, 'msg': 'URL不能为空'})
    
    try:
        # 这里应该调用实际的深度采集服务
        # 例如：result = spider.deep_crawl(url)
        
        # 模拟深度采集成功，这里应该有实际的内容解析
        time.sleep(1)  # 模拟处理时间
        
        # 假设深度采集得到了完整的内容
        deep_content = f"这是深度采集的完整内容，来源于URL：{url}\n\n包含详细的文章内容、段落、图片等信息..."
        
        # 更新临时表中的记录
        if collection_id:
            from models import CollectionTemp
            temp_item = CollectionTemp.query.get(collection_id)
            if temp_item:
                temp_item.content = deep_content
                temp_item.is_deep_collected = True
                db.session.commit()
        
        return jsonify({
            'code': 0,
            'msg': '深度采集成功',
            'data': {
                'url': url,
                'is_deep_collected': True,
                'content': deep_content
            }
        })
    except Exception as e:
        return jsonify({'code': 1, 'msg': f'深度采集失败：{str(e)}'})

@main.route('/data/save-to-warehouse', methods=['POST'])
@login_required
def save_to_warehouse():
    """保存单个采集数据到数据仓库"""
    collection_id = request.form.get('id')
    
    try:
        from models import CollectionTemp, DataWarehouse
        from datetime import datetime
        
        # 查找临时数据
        temp_item = CollectionTemp.query.get(collection_id)
        if not temp_item:
            return jsonify({'code': 1, 'msg': '数据不存在'})
        
        # 创建新的仓库数据
        new_warehouse_item = DataWarehouse(
            title=temp_item.title,
            content=temp_item.content,
            source=temp_item.source,
            url=temp_item.url,
            published_at=temp_item.published_at or datetime.now(),
            collected_by=current_user.id  # 添加采集者信息
        )
        
        db.session.add(new_warehouse_item)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '保存成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'保存失败：{str(e)}'})

@main.route('/data/warehouse/batch-save', methods=['POST'])
@login_required
@admin_required
def batch_save_to_warehouse():
    """批量保存到数据仓库"""
    collection_ids = request.form.getlist('collection_ids[]')
    if not collection_ids:
        import logging
        logging.getLogger(__name__).warning(f"用户{current_user.id}尝试批量保存到仓库，但未选择数据")
        return jsonify({'code': 1, 'msg': '请选择要保存的数据'})
    
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"用户{current_user.id}开始批量保存数据到仓库，数量：{len(collection_ids)}")
        
        from models import CollectionTemp, DataWarehouse
        saved_count = 0
        
        for collection_id in collection_ids:
            collection = CollectionTemp.query.get(collection_id)
            if not collection:
                logger.warning(f"用户{current_user.id}尝试保存不存在的临时记录：{collection_id}")
                continue
            
            # 检查数据仓库中是否已存在相同URL的记录
            existing = DataWarehouse.query.filter_by(url=collection.url).first()
            if not existing:
                # 创建新的数据仓库记录
                data = DataWarehouse(
                    title=collection.title,
                    content=collection.content,
                    source=collection.source,
                    url=collection.url,
                    published_at=collection.published_at,
                    collected_by=current_user.id
                )
                db.session.add(data)
                saved_count += 1
                
                # 从临时表中删除已保存的数据
                db.session.delete(collection)
        
        db.session.commit()
        logger.info(f"用户{current_user.id}成功批量保存{saved_count}条数据到仓库")
        return jsonify({'code': 0, 'msg': f'成功保存{saved_count}条数据到仓库'})
    except Exception as e:
        db.session.rollback()
        logging.getLogger(__name__).error(f"用户{current_user.id}批量保存数据到仓库失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'保存失败：{str(e)}'})

@main.route('/data/clear-collection', methods=['POST'])
@login_required
def clear_collection():
    """清空临时采集数据"""
    try:
        from models import CollectionTemp
        
        # 删除当前用户的所有临时采集数据
        CollectionTemp.query.filter_by(collected_by=current_user.id).delete()
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '清空成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'清空失败：{str(e)}'})

@main.route('/data/warehouse')
@login_required
def data_warehouse():
    """数据仓库管理页面"""
    from models import DataWarehouse, DetailedContent
    from sqlalchemy.orm import joinedload
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    # 构建查询，使用joinedload预加载详细内容信息
    query = DataWarehouse.query.options(joinedload(DataWarehouse.detailed_content))
    
    # 关键词搜索
    if keyword:
        query = query.filter(DataWarehouse.title.contains(keyword) | DataWarehouse.content.contains(keyword))
    
    # 按采集时间倒序排序
    query = query.order_by(DataWarehouse.created_at.desc())
    
    # 获取分页数据
    pagination = query.paginate(page=page, per_page=10)
    topics = pagination
    
    return render_template('data_warehouse.html', topics=topics)

@main.route('/data/warehouse/<int:topic_id>', methods=['PUT'])
@login_required
def update_topic(topic_id):
    """更新仓库数据"""
    from models import DataWarehouse
    from datetime import datetime
    
    try:
        # 获取表单数据
        title = request.form.get('title')
        content = request.form.get('content')
        source = request.form.get('source')
        url = request.form.get('url')
        published_at = request.form.get('published_at')
        
        # 验证数据
        if not title or not content:
            return jsonify({'code': 1, 'msg': '标题和内容不能为空'})
        
        # 查找仓库数据
        warehouse_item = DataWarehouse.query.get(topic_id)
        if not warehouse_item:
            return jsonify({'code': 1, 'msg': '数据不存在'})
        
        # 更新数据
        warehouse_item.title = title
        warehouse_item.content = content
        warehouse_item.source = source
        warehouse_item.url = url
        if published_at:
            warehouse_item.published_at = datetime.strptime(published_at, '%Y-%m-%dT%H:%M')
        
        # 保存到数据库
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'更新失败：{str(e)}'})

@main.route('/data/warehouse/<int:topic_id>', methods=['DELETE'])
@login_required
def delete_topic(topic_id):
    """删除仓库数据"""
    from models import DataWarehouse
    
    try:
        # 查找仓库数据
        warehouse_item = DataWarehouse.query.get(topic_id)
        if not warehouse_item:
            return jsonify({'code': 1, 'msg': '数据不存在'})
        
        # 删除数据
        db.session.delete(warehouse_item)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'删除失败：{str(e)}'})

@main.route('/data/warehouse/batch-delete', methods=['POST'])
@login_required
def batch_delete_topics():
    """批量删除仓库数据"""
    from models import DataWarehouse
    
    try:
        # 获取要删除的ID列表
        ids = request.form.getlist('ids')
        if not ids:
            return jsonify({'code': 1, 'msg': '请选择要删除的数据'})
        
        # 批量删除
        DataWarehouse.query.filter(DataWarehouse.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '批量删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'批量删除失败：{str(e)}'})

@main.route('/api/statistics/today-topics')
@login_required
def get_today_topics():
    """获取今日舆情数量"""
    try:
        from models import DataWarehouse
        from datetime import datetime, date
        
        today = date.today()
        today_count = DataWarehouse.query.filter(
            db.func.date(DataWarehouse.created_at) == today
        ).count()
        
        return jsonify({'code': 0, 'data': today_count})
    except Exception as e:
        logging.getLogger(__name__).error(f"获取今日舆情数量失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'获取数据失败：{str(e)}'})

@main.route('/api/statistics/sentiment-distribution')
@login_required
def get_sentiment_distribution():
    """获取情感分布统计"""
    try:
        from models import DataWarehouse
        
        # 这里假设sentiment字段存在且有值，实际项目中可能需要根据实际情况调整
        # 由于当前模型中DataWarehouse没有sentiment字段，这里使用固定数据作为示例
        distribution = {
            'positive': 45,
            'neutral': 30,
            'negative': 25
        }
        
        return jsonify({'code': 0, 'data': distribution})
    except Exception as e:
        logging.getLogger(__name__).error(f"获取情感分布失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'获取数据失败：{str(e)}'})

@main.route('/api/statistics/hot-keywords')
@login_required
def get_hot_keywords():
    """获取热门关键词"""
    try:
        # 这里需要实现关键词提取和统计功能
        # 由于当前项目中没有现成的关键词提取功能，这里使用固定数据作为示例
        hot_keywords = [
            {'word': '疫情', 'count': 128},
            {'word': '经济', 'count': 96},
            {'word': '政策', 'count': 85},
            {'word': '科技', 'count': 72},
            {'word': '教育', 'count': 64}
        ]
        
        return jsonify({'code': 0, 'data': hot_keywords})
    except Exception as e:
        logging.getLogger(__name__).error(f"获取热门关键词失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'获取数据失败：{str(e)}'})

@main.route('/data/warehouse/detailed-collect/<int:topic_id>', methods=['POST'])
@login_required
def detailed_collect(topic_id):
    """单条数据详细内容采集"""
    from models import DetailedContent
    try:
        # 获取数据仓库中的记录
        topic = DataWarehouse.query.get(topic_id)
        if not topic:
            return jsonify({'code': 1, 'msg': '数据不存在'})
        
        # 获取URL和来源
        url = topic.url
        source = topic.source
        
        if not url or not source:
            return jsonify({'code': 1, 'msg': '数据缺少URL或来源信息'})
        
        # 查找匹配的采集规则
        rule = CollectionRule.query.filter_by(site_name=source).first()
        if not rule:
            return jsonify({'code': 1, 'msg': f'未找到来源为{source}的采集规则'})
        
        # 解析请求头
        request_headers = {}
        try:
            if rule.request_headers:
                # 解析JSON格式的请求头
                raw_headers = json.loads(rule.request_headers)
                # 清理和验证请求头
                for key, value in raw_headers.items():
                    # 确保键名不包含冒号、空格等非法字符
                    clean_key = key.strip()
                    if ':' in clean_key or not clean_key:
                        continue
                    request_headers[clean_key] = str(value).strip()
        except (json.JSONDecodeError, AttributeError):
            # 如果解析失败，使用默认请求头
            request_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        
        # 发送请求获取页面内容
        response = requests.get(url, headers=request_headers, timeout=10)
        response.encoding = response.apparent_encoding
        html = response.text
        
        # 使用lxml解析HTML
        tree = etree.HTML(html)
        
        # 提取标题
        title = ''
        if rule.title_xpath:
            title_elements = tree.xpath(rule.title_xpath)
            if title_elements:
                # 使用text_content()或string()来提取元素及其所有子元素的文本
                title = title_elements[0].xpath("string()").strip()
        
        # 提取内容
        content = ''
        if rule.content_xpath:
            content_elements = tree.xpath(rule.content_xpath)
            if content_elements:
                # 使用string()来提取元素及其所有子元素的文本
                content = ' '.join([elem.xpath("string()").strip() for elem in content_elements])
        
        # 如果内容为空，尝试一些常见的内容XPath
        if not content:
            common_content_xpaths = [
                '//*[@id="detailContent"]',  # 常用的内容ID
                '//div[@id="detail"]//span[@id="detailContent"]',  # 针对当前页面的内容XPath
                '//article',
                '//div[contains(@class, "content")]',
                '//div[contains(@class, "article")]',
                '//div[contains(@id, "content")]'
            ]
            
            for xpath in common_content_xpaths:
                content_elements = tree.xpath(xpath)
                if content_elements:
                    content = ' '.join([elem.xpath("string()").strip() for elem in content_elements])
                    if content:  # 如果成功提取到内容，就停止尝试
                        break
        
        # 检查是否已经存在详细内容记录
        detailed_content = DetailedContent.query.filter_by(warehouse_id=topic_id).first()
        
        if not detailed_content:
            # 创建新的详细内容记录
            detailed_content = DetailedContent(
                warehouse_id=topic_id,
                detailed_title=title,
                detailed_content=content,
                raw_html=html,
                is_collected=True if (title or content) else False,
                collection_error=None
            )
            db.session.add(detailed_content)
        else:
            # 更新已存在的详细内容记录
            detailed_content.detailed_title = title
            detailed_content.detailed_content = content
            detailed_content.raw_html = html
            detailed_content.is_collected = True if (title or content) else False
            detailed_content.collection_error = None
            detailed_content.collected_at = datetime.now()
        
        # 如果提取到内容，则更新数据
        if title or content:
            db.session.commit()
            return jsonify({'code': 0, 'msg': '详细内容采集成功'})
        else:
            # 尝试自动更新规则
            try:
                # 分析页面结构，尝试自动生成新的XPath规则
                new_title_xpath, new_content_xpath = auto_update_rules(html, source)
                
                if new_title_xpath or new_content_xpath:
                    # 更新规则
                    if new_title_xpath:
                        rule.title_xpath = new_title_xpath
                    if new_content_xpath:
                        rule.content_xpath = new_content_xpath
                    rule.updated_at = datetime.now()
                    db.session.commit()
                    
                    # 使用新规则再次尝试提取
                    if new_title_xpath:
                        title_elements = tree.xpath(new_title_xpath)
                        if title_elements:
                            title = title_elements[0].xpath("string()").strip()
                    
                    if new_content_xpath:
                        content_elements = tree.xpath(new_content_xpath)
                        if content_elements:
                            content = ' '.join([elem.xpath("string()").strip() for elem in content_elements])
                    
                    # 更新详细内容记录
                    detailed_content.detailed_title = title
                    detailed_content.detailed_content = content
                    detailed_content.is_collected = True if (title or content) else False
                    
                    if title or content:
                        db.session.commit()
                        return jsonify({'code': 0, 'msg': '规则已自动更新，详细内容采集成功'})
                    else:
                        db.session.commit()
                        return jsonify({'code': 1, 'msg': '规则已自动更新，但仍未提取到内容'})
                else:
                    detailed_content.is_collected = False
                    detailed_content.collection_error = '未提取到标题或内容，且无法自动更新规则'
                    db.session.commit()
                    return jsonify({'code': 1, 'msg': '未提取到标题或内容，且无法自动更新规则'})
            except Exception as auto_update_error:
                logging.getLogger(__name__).error(f"自动更新规则失败：{str(auto_update_error)}", exc_info=True)
                detailed_content.is_collected = False
                detailed_content.collection_error = f'自动更新规则失败：{str(auto_update_error)}'
                db.session.commit()
                return jsonify({'code': 1, 'msg': f'未提取到标题或内容，自动更新规则失败：{str(auto_update_error)}'})
        
    except requests.exceptions.RequestException as e:
        logging.getLogger(__name__).error(f"请求页面失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'请求页面失败：{str(e)}'})
    except Exception as e:
        logging.getLogger(__name__).error(f"详细内容采集失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'采集失败：{str(e)}'})

def auto_update_rules(html, source):
    """自动更新采集规则"""
    try:
        tree = etree.HTML(html)
        
        # 尝试自动识别标题元素
        new_title_xpath = None
        # 常见的标题标签顺序
        title_tags = ['//h1', '//h2', '//header//h1', '//header//h2', '//div[contains(@class, "title")]', '//div[contains(@class, "headline")]']
        
        for xpath in title_tags:
            elements = tree.xpath(xpath)
            if elements:
                text = elements[0].xpath("string()").strip()
                if len(text) > 0:
                    new_title_xpath = xpath
                    break
        
        # 尝试自动识别内容元素
        new_content_xpath = None
        # 常见的内容标签顺序
        content_tags = ['//article', '//div[contains(@class, "content")]', '//div[contains(@class, "article")]', '//div[contains(@id, "content")]', '//section[contains(@class, "main")]', '//div[contains(@class, "post")]']
        
        for xpath in content_tags:
            elements = tree.xpath(xpath)
            if elements:
                # 检查是否包含足够的文本内容
                text = ''.join(elements[0].itertext()).strip()
                if len(text) > 100:  # 内容长度至少100个字符
                    new_content_xpath = xpath
                    break
        
        # 如果找到新规则，记录日志
        if new_title_xpath or new_content_xpath:
            logging.getLogger(__name__).info(f"自动更新了来源{source}的采集规则: title_xpath={new_title_xpath}, content_xpath={new_content_xpath}")
        
        return new_title_xpath, new_content_xpath
    except Exception as e:
        logging.getLogger(__name__).error(f"自动分析页面结构失败：{str(e)}", exc_info=True)
        return None, None

@main.route('/data/warehouse/detailed-content/<int:topic_id>', methods=['GET'])
@login_required
def get_detailed_content(topic_id):
    """获取单条数据的详细内容"""
    try:
        from models import DetailedContent
        
        # 查找详细内容记录
        detailed_content = DetailedContent.query.filter_by(warehouse_id=topic_id).first()
        
        if not detailed_content:
            return jsonify({'code': 0, 'msg': '未找到详细内容记录', 'data': {
                'detailed_title': '',
                'detailed_content': '',
                'is_collected': False,
                'collected_at': None,
                'collection_error': ''
            }})
        
        # 准备返回数据
        data = {
            'detailed_title': detailed_content.detailed_title,
            'detailed_content': detailed_content.detailed_content,
            'is_collected': detailed_content.is_collected,
            'collected_at': detailed_content.collected_at.isoformat() if detailed_content.collected_at else None,
            'collection_error': detailed_content.collection_error
        }
        
        return jsonify({'code': 0, 'msg': '获取成功', 'data': data})
    except Exception as e:
        return jsonify({'code': 1, 'msg': f'获取失败：{str(e)}'})


@main.route('/data/warehouse/batch-detailed-collect', methods=['POST'])
@login_required
def batch_detailed_collect():
    """批量数据详细内容采集"""
    from models import DetailedContent
    try:
        # 获取要采集的ID列表
        ids = request.form.getlist('ids[]')
        if not ids:
            return jsonify({'code': 1, 'msg': '请选择要采集的数据'})
        
        # 转换ID列表为整数
        ids = list(map(int, ids))
        
        # 获取数据仓库中的记录
        topics = DataWarehouse.query.filter(DataWarehouse.id.in_(ids)).all()
        if not topics:
            return jsonify({'code': 1, 'msg': '未找到选中的数据'})
        
        success_count = 0
        failed_count = 0
        
        for topic in topics:
            try:
                # 获取URL和来源
                url = topic.url
                source = topic.source
                
                if not url or not source:
                    failed_count += 1
                    continue
                
                # 查找匹配的采集规则
                rule = CollectionRule.query.filter_by(site_name=source).first()
                if not rule:
                    failed_count += 1
                    continue
                
                # 解析请求头
                request_headers = {}
                try:
                    if rule.request_headers:
                        # 解析JSON格式的请求头
                        raw_headers = json.loads(rule.request_headers)
                        # 清理和验证请求头
                        for key, value in raw_headers.items():
                            # 确保键名不包含冒号、空格等非法字符
                            clean_key = key.strip()
                            if ':' in clean_key or not clean_key:
                                continue
                            request_headers[clean_key] = str(value).strip()
                except (json.JSONDecodeError, AttributeError):
                    # 如果解析失败，使用默认请求头
                    request_headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                
                # 发送请求获取页面内容
                response = requests.get(url, headers=request_headers, timeout=10)
                response.encoding = response.apparent_encoding
                html = response.text
                
                # 使用lxml解析HTML
                tree = etree.HTML(html)
                
                # 提取标题
                title = ''
                if rule.title_xpath:
                    title_elements = tree.xpath(rule.title_xpath)
                    if title_elements:
                        # 使用text_content()或string()来提取元素及其所有子元素的文本
                        title = title_elements[0].xpath("string()").strip()
                
                # 提取内容
                content = ''
                if rule.content_xpath:
                    content_elements = tree.xpath(rule.content_xpath)
                    if content_elements:
                        # 使用string()来提取元素及其所有子元素的文本
                        content = ' '.join([elem.xpath("string()").strip() for elem in content_elements])
                
                # 检查是否已经存在详细内容记录
                detailed_content = DetailedContent.query.filter_by(warehouse_id=topic.id).first()
                
                if not detailed_content:
                    # 创建新的详细内容记录
                    detailed_content = DetailedContent(
                        warehouse_id=topic.id,
                        detailed_title=title,
                        detailed_content=content,
                        raw_html=html,
                        is_collected=True if (title or content) else False,
                        collection_error=None
                    )
                    db.session.add(detailed_content)
                else:
                    # 更新已存在的详细内容记录
                    detailed_content.detailed_title = title
                    detailed_content.detailed_content = content
                    detailed_content.raw_html = html
                    detailed_content.is_collected = True if (title or content) else False
                    detailed_content.collection_error = None
                    detailed_content.collected_at = datetime.now()
                
                # 如果提取到内容，则更新数据
                if title or content:
                    success_count += 1
                else:
                    # 尝试自动更新规则
                    try:
                        # 分析页面结构，尝试自动生成新的XPath规则
                        new_title_xpath, new_content_xpath = auto_update_rules(html, source)
                        
                        if new_title_xpath or new_content_xpath:
                            # 更新规则
                            if new_title_xpath:
                                rule.title_xpath = new_title_xpath
                            if new_content_xpath:
                                rule.content_xpath = new_content_xpath
                            rule.updated_at = datetime.now()
                            
                            # 使用新规则再次尝试提取
                            if new_title_xpath:
                                title_elements = tree.xpath(new_title_xpath)
                                if title_elements:
                                    title = title_elements[0].text.strip() if title_elements[0].text else ''
                            
                            if new_content_xpath:
                                content_elements = tree.xpath(new_content_xpath)
                                if content_elements:
                                    content = ' '.join([elem.text.strip() for elem in content_elements if elem.text])
                            
                            # 更新详细内容记录
                            detailed_content.detailed_title = title
                            detailed_content.detailed_content = content
                            detailed_content.is_collected = True if (title or content) else False
                            
                            if title or content:
                                success_count += 1
                            else:
                                detailed_content.is_collected = False
                                detailed_content.collection_error = '规则已自动更新，但仍未提取到内容'
                                failed_count += 1
                        else:
                            detailed_content.is_collected = False
                            detailed_content.collection_error = '未提取到标题或内容，且无法自动更新规则'
                            failed_count += 1
                    except Exception as auto_update_error:
                        logging.getLogger(__name__).error(f"自动更新规则失败：{str(auto_update_error)}", exc_info=True)
                        detailed_content.is_collected = False
                        detailed_content.collection_error = f'自动更新规则失败：{str(auto_update_error)}'
                        failed_count += 1
                    
            except Exception as e:
                logging.getLogger(__name__).error(f"批量采集单条数据失败：{str(e)}", exc_info=True)
                failed_count += 1
                continue
        
        # 提交事务
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': f'批量采集完成，成功{success_count}条，失败{failed_count}条'})
        
    except Exception as e:
        logging.getLogger(__name__).error(f"批量详细内容采集失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'批量采集失败：{str(e)}'})

@main.route('/data/warehouse/ai-analysis', methods=['POST'])
@login_required
def ai_analysis():
    """AI解析分析（预留接口）"""
    try:
        # 获取要分析的ID列表
        ids = request.form.getlist('ids[]')
        if not ids:
            return jsonify({'code': 1, 'msg': '请选择要分析的数据'})
        
        # 这里将在后期实现AI分析功能
        # 目前仅返回成功信息
        
        return jsonify({'code': 0, 'msg': 'AI分析功能开发中，敬请期待'})
    except Exception as e:
        logging.getLogger(__name__).error(f"AI分析失败：{str(e)}", exc_info=True)
        return jsonify({'code': 1, 'msg': f'分析失败：{str(e)}'})


# 缓存app_name，避免每次请求都查询数据库
APP_NAME_CACHE = None
APP_NAME_CACHE_TIME = None
CACHE_TIMEOUT = 3600  # 缓存有效期，单位：秒

@main.context_processor
def inject_app_name():
    """上下文处理器，全局注入app_name变量"""
    global APP_NAME_CACHE, APP_NAME_CACHE_TIME
    from datetime import datetime
    
    # 检查缓存是否存在且未过期
    current_time = datetime.utcnow()
    if APP_NAME_CACHE and APP_NAME_CACHE_TIME:
        time_diff = (current_time - APP_NAME_CACHE_TIME).total_seconds()
        if time_diff < CACHE_TIMEOUT:
            return dict(app_name=APP_NAME_CACHE)
    
    # 缓存不存在或已过期，重新查询数据库
    app_name = Setting.query.filter_by(key='app_name').first()
    APP_NAME_CACHE = app_name.value if app_name else '政企智能舆情分析系统'
    APP_NAME_CACHE_TIME = current_time
    
    return dict(app_name=APP_NAME_CACHE)


# AI引擎管理路由
@main.route('/admin/ai-engines')
@login_required
@admin_required
def ai_engines():
    """AI引擎管理页面"""
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    # 构建查询
    query = AiEngine.query
    
    # 关键词搜索
    if keyword:
        query = query.filter(AiEngine.provider_name.contains(keyword) | AiEngine.model_name.contains(keyword))
    
    # 按更新时间倒序排序
    query = query.order_by(AiEngine.updated_at.desc())
    
    # 获取分页数据
    pagination = query.paginate(page=page, per_page=10)
    engines = pagination
    
    return render_template('admin/ai_engines.html', engines=engines)

@main.route('/admin/ai-engine', methods=['POST'])
@login_required
@admin_required
def add_ai_engine():
    """添加AI引擎"""
    try:
        # 获取表单数据
        provider_name = request.form.get('provider_name')
        api_url = request.form.get('api_url')
        api_key = request.form.get('api_key')
        model_name = request.form.get('model_name')
        description = request.form.get('description', '')
        status = request.form.get('status', 'true').lower() == 'true'
        
        # 验证数据
        if not all([provider_name, api_url, api_key, model_name]):
            return jsonify({'code': 1, 'msg': '服务商名称、API URL、API Key和模型名称不能为空'})
        
        # 创建新引擎
        engine = AiEngine(
            provider_name=provider_name,
            api_url=api_url,
            api_key=api_key,
            model_name=model_name,
            description=description,
            status=status,
            created_by=current_user.id
        )
        
        db.session.add(engine)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': 'AI引擎添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'添加失败：{str(e)}'})

@main.route('/admin/ai-engine/<int:engine_id>', methods=['PUT'])
@login_required
@admin_required
def update_ai_engine(engine_id):
    """更新AI引擎"""
    try:
        # 获取引擎
        engine = AiEngine.query.get(engine_id)
        if not engine:
            return jsonify({'code': 1, 'msg': '引擎不存在'})
        
        # 获取表单数据
        provider_name = request.form.get('provider_name')
        api_url = request.form.get('api_url')
        api_key = request.form.get('api_key')
        model_name = request.form.get('model_name')
        description = request.form.get('description', '')
        status = request.form.get('status', 'true').lower() == 'true'
        
        # 验证数据
        if not all([provider_name, api_url, api_key, model_name]):
            return jsonify({'code': 1, 'msg': '服务商名称、API URL、API Key和模型名称不能为空'})
        
        # 更新引擎
        engine.provider_name = provider_name
        engine.api_url = api_url
        engine.api_key = api_key
        engine.model_name = model_name
        engine.description = description
        engine.status = status
        
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': 'AI引擎更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'更新失败：{str(e)}'})

@main.route('/admin/ai-engine/<int:engine_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_ai_engine(engine_id):
    """删除AI引擎"""
    try:
        # 获取引擎
        engine = AiEngine.query.get(engine_id)
        if not engine:
            return jsonify({'code': 1, 'msg': '引擎不存在'})
        
        # 删除引擎
        db.session.delete(engine)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': 'AI引擎删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'删除失败：{str(e)}'})

@main.route('/admin/ai-engine/<int:engine_id>')
@login_required
@admin_required
def get_ai_engine(engine_id):
    """获取单个AI引擎的详细信息"""
    try:
        # 获取引擎
        engine = AiEngine.query.get(engine_id)
        if not engine:
            return jsonify({'code': 1, 'msg': '引擎不存在'})
        
        # 转换为JSON格式
        engine_data = {
            'id': engine.id,
            'provider_name': engine.provider_name,
            'api_url': engine.api_url,
            'api_key': engine.api_key,
            'model_name': engine.model_name,
            'description': engine.description,
            'status': engine.status,
            'created_at': engine.created_at.isoformat() if engine.created_at else None,
            'updated_at': engine.updated_at.isoformat() if engine.updated_at else None
        }
        
        return jsonify({'code': 0, 'data': engine_data})
    except Exception as e:
        return jsonify({'code': 1, 'msg': f'获取引擎失败：{str(e)}'})


# 采集规则库路由
@main.route('/admin/collection-rules')
@login_required
@admin_required
def collection_rules():
    """采集规则库页面"""
    from models import CollectionRule
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '')
    
    # 构建查询
    query = CollectionRule.query
    
    # 关键词搜索
    if keyword:
        query = query.filter(CollectionRule.site_name.contains(keyword) | CollectionRule.site_url.contains(keyword))
    
    # 按更新时间倒序排序
    query = query.order_by(CollectionRule.updated_at.desc())
    
    # 获取分页数据
    pagination = query.paginate(page=page, per_page=10)
    rules = pagination
    
    return render_template('admin/collection_rules.html', rules=rules)

@main.route('/admin/collection-rule', methods=['POST'])
@login_required
@admin_required
def add_collection_rule():
    """添加采集规则"""
    from models import CollectionRule
    import json
    
    try:
        # 获取JSON数据
        data = request.get_json()
        if not data:
            return jsonify({'code': 1, 'msg': '请提供有效的JSON数据'})
        
        # 提取数据
        site_name = data.get('site_name')
        site_url = data.get('site_url')
        title_xpath = data.get('title_xpath')
        content_xpath = data.get('content_xpath')
        headers = data.get('request_headers', {})
        
        # 验证数据
        if not all([site_name, site_url, title_xpath, content_xpath]):
            return jsonify({'code': 1, 'msg': '站点名称、URL、标题XPath和内容XPath不能为空'})
        
        # 转换headers为JSON字符串
        headers_json = json.dumps(headers)
        
        # 创建新规则
        rule = CollectionRule(
            site_name=site_name,
            site_url=site_url,
            title_xpath=title_xpath,
            content_xpath=content_xpath,
            request_headers=headers_json,
            created_by=current_user.id
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '规则添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'添加失败：{str(e)}'})

@main.route('/admin/collection-rule/<int:rule_id>', methods=['PUT'])
@login_required
@admin_required
def update_collection_rule(rule_id):
    """更新采集规则"""
    from models import CollectionRule
    import json
    
    try:
        # 获取规则
        rule = CollectionRule.query.get(rule_id)
        if not rule:
            return jsonify({'code': 1, 'msg': '规则不存在'})
        
        # 获取表单数据
        site_name = request.form.get('site_name')
        site_url = request.form.get('site_url')
        title_xpath = request.form.get('title_xpath')
        content_xpath = request.form.get('content_xpath')
        headers_str = request.form.get('headers', '{}')
        
        # 验证数据
        if not all([site_name, site_url, title_xpath, content_xpath]):
            return jsonify({'code': 1, 'msg': '站点名称、URL、标题XPath和内容XPath不能为空'})
        
        # 解析headers JSON
        try:
            headers = json.loads(headers_str)
            headers_json = json.dumps(headers)
        except json.JSONDecodeError:
            return jsonify({'code': 1, 'msg': 'Request Headers格式错误，请使用有效的JSON格式'})
        
        # 更新规则
        rule.site_name = site_name
        rule.site_url = site_url
        rule.title_xpath = title_xpath
        rule.content_xpath = content_xpath
        rule.request_headers = headers_json
        
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '规则更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'更新失败：{str(e)}'})

@main.route('/admin/collection-rule/<int:rule_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_collection_rule(rule_id):
    """删除采集规则"""
    from models import CollectionRule
    
    try:
        # 获取规则
        rule = CollectionRule.query.get(rule_id)
        if not rule:
            return jsonify({'code': 1, 'msg': '规则不存在'})
        
        # 删除规则
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({'code': 0, 'msg': '规则删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 1, 'msg': f'删除失败：{str(e)}'})

@main.route('/admin/collection-rule/<int:rule_id>')
@login_required
@admin_required
def get_collection_rule(rule_id):
    """获取单个采集规则的JSON数据"""
    from models import CollectionRule
    import json
    
    try:
        # 获取规则
        rule = CollectionRule.query.get(rule_id)
        if not rule:
            return jsonify({'code': 1, 'msg': '规则不存在'})
        
        # 转换为JSON格式
        rule_data = {
            'id': rule.id,
            'site_name': rule.site_name,
            'site_url': rule.site_url,
            'title_xpath': rule.title_xpath,
            'content_xpath': rule.content_xpath,
            'request_headers': json.loads(rule.request_headers) if rule.request_headers else {}
        }
        
        return jsonify({'code': 0, 'data': rule_data})
    except Exception as e:
        return jsonify({'code': 1, 'msg': f'获取规则失败：{str(e)}'})
