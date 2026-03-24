"""
评审管理模块
负责管理评审历史记录
"""
import json
import os
import re
from datetime import datetime


class ReviewManager:
    def __init__(self, reviews_dir='reviews'):
        self.reviews_dir = reviews_dir
        if not os.path.exists(self.reviews_dir):
            os.makedirs(self.reviews_dir)
        self.index_file = os.path.join(self.reviews_dir, 'index.json')
        self.reviews_index = self.load_index()
    
    def load_index(self):
        """加载评审索引"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载评审索引失败: {e}")
                return []
        return []
    
    def save_index(self):
        """保存评审索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.reviews_index, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存评审索引失败: {e}")
            return False
    
    def _extract_archive_info(self, folder_path: str) -> tuple[str, str | None]:
        """提取原始压缩包名称和内部根目录名。"""
        temp_dir_match = re.match(r"(.*/code_review_archive_[^/]+)/(.+)", folder_path)
        if temp_dir_match:
            temp_root = temp_dir_match.group(1)
            inner_name = temp_dir_match.group(2)
            if os.path.isdir(temp_root):
                archive_name = os.path.basename(temp_root)
                original_archive = next(
                    (os.path.basename(item) for item in os.listdir(temp_root) if item.lower().endswith(('.zip', '.rar'))),
                    None
                )
                return original_archive or archive_name, inner_name
        return os.path.basename(folder_path), None

    def save_review(self, workspace_origin_path, folder_path, review_content, display_name=None, model_name=None):
        """保存评审记录"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = None
        internal_root = None

        if workspace_origin_path and workspace_origin_path.lower().endswith(('.zip', '.rar')):
            archive_name = os.path.basename(workspace_origin_path)
            internal_root = os.path.basename(folder_path)
        else:
            archive_name, internal_root = self._extract_archive_info(folder_path)

        display_name = display_name or archive_name or os.path.basename(folder_path)
        review_id = f"{(archive_name or display_name).replace(' ', '_')}_{timestamp}"

        # 保存Markdown文件
        md_filename = f"{review_id}.md"
        md_path = os.path.join(self.reviews_dir, md_filename)
        raw_filename = f"{review_id}.raw.txt"
        raw_path = os.path.join(self.reviews_dir, raw_filename)

        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write("# 代码评审报告\n\n")
                f.write(f"**项目路径**: {folder_path}\n\n")
                if archive_name:
                    f.write(f"**原始压缩包**: {archive_name}\n\n")
                f.write(f"**评审时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(review_content)

            with open(raw_path, 'w', encoding='utf-8') as raw_file:
                raw_file.write(review_content)

            review_record = {
                'id': review_id,
                'folder_path': folder_path,
                'folder_name': os.path.basename(folder_path),
                'display_name': display_name,
                'archive_name': archive_name,
                'timestamp': timestamp,
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'md_file': md_filename,
                'raw_file': raw_filename,
                'model_name': model_name or ''
            }
            self.reviews_index.insert(0, review_record)
            self.save_index()

            return review_id, md_path
        except Exception as e:
            print(f"保存评审记录失败: {e}")
            return None, None
    
    def get_review_content(self, review_id):
        """获取评审内容"""
        for review in self.reviews_index:
            if review['id'] == review_id:
                raw_file = review.get('raw_file')
                target_file = raw_file or review['md_file']
                md_path = os.path.join(self.reviews_dir, target_file)
                if os.path.exists(md_path):
                    try:
                        with open(md_path, 'r', encoding='utf-8') as f:
                            return f.read()
                    except Exception as e:
                        print(f"读取评审内容失败: {e}")
                        return None
        return None
    
    def get_all_reviews(self):
        """获取所有评审记录"""
        return self.reviews_index
    
    def delete_review(self, review_id):
        """删除评审记录"""
        for i, review in enumerate(self.reviews_index):
            if review['id'] == review_id:
                # 删除MD文件
                md_path = os.path.join(self.reviews_dir, review['md_file'])
                if os.path.exists(md_path):
                    try:
                        os.remove(md_path)
                    except Exception as e:
                        print(f"删除评审文件失败: {e}")

                raw_file = review.get('raw_file')
                if raw_file:
                    raw_path = os.path.join(self.reviews_dir, raw_file)
                    if os.path.exists(raw_path):
                        try:
                            os.remove(raw_path)
                        except Exception as e:
                            print(f"删除原始评审文件失败: {e}")
                
                # 从索引中移除
                self.reviews_index.pop(i)
                self.save_index()
                return True
        return False
