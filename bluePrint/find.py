import base64
from flask import  request,  Blueprint, jsonify, current_app, send_file
from models import Content, UserContent

bp=Blueprint('find', __name__)


@bp.route('/find', methods=['POST'])
def find():
            try:
                # 从请求中获取关键字和用户 ID
                data = request.get_json()
                keywords = data.get('keyword')
                user_id =current_app.config.get("USER_ID")  # 假设用户 ID 存在于配置中
                # 检查用户 ID 和关键词是否提供
                if not user_id or not data:
                    return jsonify({'error': 'User ID or keywords not provided'}), 400

                UC =UserContent.query.filter_by(user_id=user_id).all()
                id_list=[]
                for uc in UC:
                    id_list.append(uc.content_id)
                # 查询匹配的内容
                contents = Content.query.filter(
                    Content.id.in_(id_list),
                    (Content.name.contains(keywords) |
                    Content.sex.contains(keywords) |
                    Content.id_card_number.contains(keywords) |
                    Content.birth.contains(keywords) |
                    Content.address.contains(keywords) |
                    Content.nation.contains(keywords))
                ).all()
                # 如果没有找到内容
                if not contents:
                    return jsonify({'error': '找不到相关内容'}), 404
                image_data=[]
                for content in contents:
                    image_data.append(base64.b64encode(content.image).decode('utf-8'))
                return jsonify({'image_data':image_data}), 200
            except Exception as e:
                print(e)
                return jsonify({'error': str(e)}), 400