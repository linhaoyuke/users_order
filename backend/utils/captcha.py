# backend/utils/captcha.py

import base64
import operator
import random

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature


def get_serializer():
    """
    获取一个itsdangerous序列化器实例。
    使用应用的SECRET_KEY和特定的salt来保证签名安全。
    每次调用都创建一个新实例，以确保线程安全。
    """
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='captcha-salt')

class CaptchaGenerator:
    """
    一个无状态、线程安全的验证码生成器。
    它生成数学计算题，并将问题渲染成SVG图片。
    答案通过itsdangerous进行加密和签名，生成一个有时效性的token，代替了传统的session存储。
    """
    def __init__(self, width=120, height=50):
        self.width = width
        self.height = height
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul
        }

    def generate_math_problem(self):
        """生成一个随机的数学问题（加、减、乘）。"""
        operation = random.choice(['+', '-', '*'])
        if operation == '+':
            num1, num2 = random.randint(1, 20), random.randint(1, 20)
        elif operation == '-':
            num1 = random.randint(10, 30)
            num2 = random.randint(1, num1)
        else:  # 乘法
            num1, num2 = random.randint(1, 10), random.randint(1, 10)
        
        result = self.operations[operation](num1, num2)
        problem_text = f"{num1} {operation} {num2} = ?"
        return {'problem': problem_text, 'result': str(result)}

    def create_captcha(self):
        """
        创建验证码。
        返回包含Base64编码的SVG图片和加密答案的token的字典。
        """
        try:
            math_problem = self.generate_math_problem()
            result = math_problem['result']
            problem_to_draw = math_problem['problem'].replace(' = ?', '')
            
            # 生成SVG图片
            image_data = self.generate_simple_svg_image(problem_to_draw)

            # 将正确答案加密成一个有时效性的token (有效期5分钟)
            s = get_serializer()
            token = s.dumps(result)

            return {'image': image_data, 'token': token}
        except Exception as e:
            current_app.logger.error(f"验证码生成失败: {e}")
            raise

    @staticmethod
    def verify_captcha(user_input, token):
        """
        静态方法，用于验证用户输入是否与token中的答案匹配。
        :param user_input: 用户提交的答案。
        :param token: 创建验证码时生成的token。
        :return: Boolean, 验证是否成功。
        """
        if not user_input or not token:
            return False

        s = get_serializer()
        try:
            # 解密token，并设置最大有效期为300秒 (5分钟)
            stored_result = s.loads(token, max_age=300)
            # 比较解密后的答案和用户输入的答案
            return stored_result == user_input.strip()
        except (SignatureExpired, BadTimeSignature):
            # 如果token过期或签名无效，则验证失败
            return False

    def generate_simple_svg_image(self, text):
        """使用丰富的干扰元素生成SVG格式的验证码图片。"""
        svg_content = f'''
        <svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <filter id="noise">
                    <feTurbulence baseFrequency="0.9" numOctaves="4" result="noise"/>
                    <feDisplacementMap in="SourceGraphic" in2="noise" scale="2"/>
                </filter>
                <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#2c3e50;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#34495e;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="{self.width}" height="{self.height}" fill="#f8f9fa" stroke="#dee2e6" stroke-width="1"/>
            {self._generate_interference_noise()}
            {self._generate_interference_lines()}
            {self._generate_char_elements(text)}
            {self._generate_interference_circles()}
            {self._generate_foreground_lines()}
        </svg>'''
        # 将SVG内容编码为Base64
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{svg_base64}"

    # --- 以下为生成各种SVG干扰元素的私有辅助方法 ---

    def _generate_interference_lines(self):
        """生成随机干扰线。"""
        lines = []
        for _ in range(random.randint(3, 6)):
            x1, y1 = random.randint(0, self.width), random.randint(0, self.height)
            x2, y2 = random.randint(0, self.width), random.randint(0, self.height)
            color = f"rgb({random.randint(150, 200)}, {random.randint(150, 200)}, {random.randint(150, 200)})"
            lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{random.randint(1, 2)}" opacity="{random.uniform(0.3, 0.7)}"/>')
        return '\n'.join(lines)

    def _generate_interference_circles(self):
        """生成随机干扰圆圈。"""
        circles = []
        for _ in range(random.randint(2, 4)):
            cx, cy, r = random.randint(0, self.width), random.randint(0, self.height), random.randint(3, 8)
            color = f"rgb({random.randint(180, 220)}, {random.randint(180, 220)}, {random.randint(180, 220)})"
            circles.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{random.uniform(0.2, 0.5)}"/>')
        return '\n'.join(circles)

    def _generate_interference_noise(self):
        """生成随机噪点。"""
        noise = []
        for _ in range(random.randint(20, 40)):
            x, y = random.randint(0, self.width), random.randint(0, self.height)
            color = f"rgb({random.randint(200, 240)}, {random.randint(200, 240)}, {random.randint(200, 240)})"
            noise.append(f'<circle cx="{x}" cy="{y}" r="1" fill="{color}" opacity="{random.uniform(0.1, 0.3)}"/>')
        return '\n'.join(noise)

    def _generate_char_elements(self, text):
        """将问题文本渲染为带有随机样式的SVG <text> 元素。"""
        chars = []
        char_width = self.width // (len(text) + 1)
        for i, char in enumerate(text):
            x = char_width * (i + 0.8) # 调整字符间距
            y = self.height // 2 + random.randint(-5, 5)
            
            # 对运算符进行特殊处理，使其更突出
            if char in self.operations:
                rotation, font_size, color = random.randint(-5, 5), random.randint(28, 34), f"rgb({random.randint(180, 220)}, {random.randint(20, 50)}, {random.randint(20, 50)})"
            else: # 数字样式
                rotation, font_size, color = random.randint(-15, 15), random.randint(22, 28), f"rgb({random.randint(20, 80)}, {random.randint(20, 80)}, {random.randint(20, 80)})"
            
            transform = f"rotate({rotation} {x} {y})"
            chars.append(f'<text x="{x}" y="{y}" font-family="monospace" font-size="{font_size}" font-weight="bold" fill="{color}" text-anchor="middle" dominant-baseline="middle" transform="{transform}" filter="url(#noise)">{char}</text>')
        return '\n'.join(chars)

    def _generate_foreground_lines(self):
        """生成前景干扰线（在文字之上）。"""
        lines = []
        for _ in range(random.randint(1, 3)):
            x1, y1 = random.randint(0, self.width), random.randint(0, self.height)
            x2, y2 = random.randint(0, self.width), random.randint(0, self.height)
            color = f"rgb({random.randint(100, 150)}, {random.randint(100, 150)}, {random.randint(100, 150)})"
            lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1" opacity="{random.uniform(0.2, 0.4)}"/>')
        return '\n'.join(lines)