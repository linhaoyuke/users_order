# backend/utils/permissions.py

from models.user import User

def has_permission(user_id, permission_code):
    """
    检查指定ID的用户是否拥有特定的权限。

    这是一个辅助函数，通过查询数据库来验证用户的权限。
    它封装了从用户ID到权限验证的整个过程。

    注意：在受JWT保护的路由中，更高效的方式是直接从JWT的claims中读取权限信息，
    而不是每次都查询数据库。可以参考 `utils.jwt.py` 中的 `permission_required` 装饰器。
    这个函数可能适用于非请求上下文的场景，例如在后台任务中验证权限。

    :param user_id: 要检查的用户的ID。
    :param permission_code: 要检查的权限编码，例如 'user:create'。
    :return: Boolean, 如果用户拥有该权限则返回True，否则返回False。
    """
    # 根据ID从数据库中查找用户
    user = User.query.get(user_id)
    
    # 如果用户不存在，则当然没有任何权限
    if not user:
        return False
        
    # 调用User模型中定义的has_permission方法来进行实际的权限检查
    return user.has_permission(permission_code)
