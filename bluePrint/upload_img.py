import base64
from collections import OrderedDict
from flask import Flask, request, jsonify,  make_response, g, current_app
import requests
from flask import Blueprint
from extend import db
from models import Content, UserContent

bp = Blueprint('upload_img', __name__, url_prefix='/login')

# 百度OCR API相关配置
BAIDU_OCR_API_URL = 'https://aip.baidubce.com/rest/2.0/ocr/v1/idcard'
BAIDU_AK = 'LkANCIl21LRnNzpNXIP3oKjG'
BAIDU_SK = '6le9hIzRE91FdwLv745H27TimXgQqXBX'

#身份证号码校验
def is_valid_id_card(id_card_number):
    # 身份证号码长度必须是18位
    if len(id_card_number) != 18:
        return False

    # 检查是否全为数字或最后一位为字母X
    if not (id_card_number[:17].isdigit() and (id_card_number[17].isdigit() or id_card_number[17] == 'X')):
        return False

    # 这里可以添加更多的校验逻辑，比如出生日期的校验等
    # 下面是针对出生日期的简单验证
    birth_date = id_card_number[6:14]  # 获取出生日期部分
    year = int(birth_date[:4])
    month = int(birth_date[4:6])
    day = int(birth_date[6:8])

    # 检查日期合法性
    from datetime import datetime
    try:
        datetime(year, month, day)
    except ValueError:
        return False

    return True  # 所有校验通过，返回True

#身份证校验
def validate_id_card_info(id_card_info)->str:
    try:
        id_card_number = id_card_info.get('公民身份号码', {}).get('words', '')
        name = id_card_info.get('姓名',{}).get('words', '')
        gender = id_card_info.get('性别', {}).get('words', '')
        ethnicity = id_card_info.get('民族', {}).get('words', '')
        birth_date = id_card_info.get('出生日期', {}).get('words', '')

        if id_card_number == '' and name == '' and gender == '' and ethnicity == '' and birth_date == '':
            return "非身份证照片！"
        # 校验姓名（简单示例，仅检查是否为空）
        if not name:
            return "姓名不能为空！"
        # # 校验性别
        # valid_genders = ["男", "女"]
        # if gender not in valid_genders:
        #     return "性别不合法"
        # 校验民族（合理性检查）
        if ethnicity not in ['汉', '壮族', '满族', '回族', '苗族', '维吾尔族', '土家族', '彝族', '蒙古族', '藏族', '布依族', '侗族', '瑶族', '朝鲜族', '白族', '哈尼族', '黎族', '傣族', '畲族', '傈僳族', '仡佬族', '东乡族', '高山族', '拉祜族', '水族', '佤族', '纳西族', '羌族', '土族', '仫佬族', '锡伯族', '柯尔克孜族', '景颇族', '达斡尔族', '撒拉族', '布朗族', '毛南族']:
            return "民族不合法"
        # 校验出生日期格式是否正确
        # try:
        #     datetime.datetime.strptime(birth_date, "%Y%m%d")
        # except ValueError:
        #     return "出生日期格式不合法"
        # 校验身份证号码是否合法
        if not is_valid_id_card(id_card_number):
            return "身份证号码不合法"

        return "信息合格"  # 如果所有校验都通过，返回True
    except Exception as e:
        print(f"校验过程中发生错误: {e}")
        return "校验过程中发生错误"

#处理返回的json数据
def json_dispose(data,image_binary):
    words_result = data.get('words_result', {})
    json_data = OrderedDict([
        ("姓名", words_result.get('姓名', {}).get('words', '')),
        ("性别", words_result.get('性别', {}).get('words', '')),
        ("民族", words_result.get('民族', {}).get('words', '')),
        ("出生日期", words_result.get('出生', {}).get('words', '')),
        ("公民身份号码", words_result.get('公民身份号码', {}).get('words', '')),
        ("住址", words_result.get('住址', {}).get('words', '')),
        ("error","")
    ])
    try:
        if not current_app.config.get('USER_ID'):
            return make_response(jsonify({'error': '请先登录'}), 401)
        #创建内容
        #判断是否已经存在相同内容
        ID=UserContent.query.filter_by(user_id=current_app.config.get('USER_ID')).all()
        sign=False
        content_list=[]
        for i in ID:
            content_list = Content.query.filter_by(id=i.content_id).all()
            if content_list:
                sign=True
                break
        if  sign:
            for content in content_list:
                if content.id_card_number == json_data.get('公民身份号码'):
                    return   make_response(jsonify(json_data), 200)

        content = Content(name=json_data.get('姓名'),sex=json_data.get('性别'),nation=json_data.get('民族'),birth=json_data.get('出生日期'),id_card_number=json_data.get('公民身份号码'),address=json_data.get('住址'),image=image_binary)
        db.session.add(content)
        db.session.commit()
            # 实现用户与内容的关联
        user_content = UserContent(user_id=current_app.config.get('USER_ID'), content=content)
        db.session.add(user_content)
        db.session.commit()
    except Exception as e:
        print(f"创建内容失败: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

    return make_response(jsonify(json_data), 200)

# 获取access_token
def get_access_token():
    url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={BAIDU_AK}&client_secret={BAIDU_SK}'
    response = requests.get(url)
    return response.json().get('access_token')

# 调用OCR接口
def ocr_image(base64Data):
    access_token = get_access_token()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    params = {
        'access_token': access_token
    }
    data = {
        'id_card_side': 'front',
        'image': base64Data
    }
    response = requests.post(BAIDU_OCR_API_URL, headers=headers, params=params, data=data)
    return response.json()

@bp.route('/upload_img', methods=['POST', 'GET'])
def upload():
    try:
        data = request.form
        image_base64 = data.get('image')
        if not image_base64:
            return jsonify({'error': 'No image data provided'}), 400

        result = ocr_image(image_base64)

        if 'words_result' not in result:
            return jsonify({'error': 'OCR failed', 'details': result}), 400

        #抛出错误并返回错误信息
        error_info =validate_id_card_info(result.get('words_result', {}))
        if error_info !="信息合格":
            raise Exception(str(error_info))

        return json_dispose(result,base64.b64decode(image_base64)), 200
    except Exception as e:
        print(f"发生错误: {e}")
        return jsonify({'error': str(e)}), 500