"""
文件扫描模块
负责扫描项目文件和生成文件结构
"""
import os


class FileScanner:
    # 需要忽略的文件夹
    IGNORE_DIRS = {
        '__pycache__', 'node_modules', '.git', '.venv', 'venv',
        'env', 'ENV', 'build', 'dist', '.idea', '.vscode',
        'egg-info', '.pytest_cache', '.mypy_cache'
    }
    
    # 支持的代码文件扩展名
    CODE_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
        '.html', '.css', '.scss', '.sass', '.less', '.vue', '.xml',
        '.json', '.yaml', '.yml', '.md', '.txt', '.sh', '.bash',
        '.sql', '.r', '.m', '.dart', '.lua'
    }
    
    @staticmethod
    def scan_directory(root_path, max_file_size=500000):
        """
        扫描目录并返回文件结构和代码内容
        
        Args:
            root_path: 根目录路径
            max_file_size: 最大文件大小（字节），默认500KB
        
        Returns:
            (file_structure, code_files)
        """
        file_structure = []
        code_files = {}
        
        def should_ignore(name):
            """检查是否应该忽略该文件/文件夹"""
            return name.startswith('.') or name in FileScanner.IGNORE_DIRS
        
        def scan_recursive(path, prefix=''):
            """递归扫描目录"""
            try:
                items = sorted(os.listdir(path))
            except PermissionError:
                return
            
            for item in items:
                if should_ignore(item):
                    continue
                
                item_path = os.path.join(path, item)
                relative_path = os.path.relpath(item_path, root_path)
                
                if os.path.isdir(item_path):
                    file_structure.append(f"{prefix}📁 {item}/")
                    scan_recursive(item_path, prefix + '  ')
                else:
                    file_structure.append(f"{prefix}📄 {item}")
                    
                    # 检查是否是代码文件
                    _, ext = os.path.splitext(item)
                    if ext.lower() in FileScanner.CODE_EXTENSIONS:
                        try:
                            file_size = os.path.getsize(item_path)
                            if file_size <= max_file_size:
                                with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    code_files[relative_path] = content
                        except Exception as e:
                            print(f"读取文件失败 {item_path}: {e}")
        
        scan_recursive(root_path)
        
        return '\n'.join(file_structure), code_files
    
    @staticmethod
    def get_file_tree(root_path, display_name=None):
        """
        获取文件树结构（用于Qt树形控件）
        """
        def should_ignore(name):
            return name.startswith('.') or name in FileScanner.IGNORE_DIRS
        
        def build_tree(path):
            """递归构建树结构"""
            node = {
                'name': os.path.basename(path) or path,
                'path': path,
                'is_dir': os.path.isdir(path),
                'children': []
            }
            
            if node['is_dir']:
                try:
                    items = sorted(os.listdir(path))
                    for item in items:
                        if should_ignore(item):
                            continue
                        item_path = os.path.join(path, item)
                        child = build_tree(item_path)
                        if child:
                            node['children'].append(child)
                except PermissionError:
                    pass
            
            return node
        
        tree = build_tree(root_path)
        if display_name:
            tree['name'] = display_name
        return tree
