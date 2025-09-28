#!/usr/bin/env python3
"""
脚本名称：文件内容搜索替换工具
创建时间：2024-01-20
用途：在指定目录中搜索和替换文件内容，支持正则表达式和批量操作
参数：
  --directory: 搜索目录路径
  --pattern: 搜索模式（支持正则表达式）
  --replacement: 替换内容
  --file-pattern: 文件名模式（如 *.py, *.js）
  --dry-run: 预览模式，不实际修改文件
  --backup: 创建备份文件
示例：
  python scripts/ai/file_processing/search_replace.py --directory src --pattern "old_function" --replacement "new_function" --file-pattern "*.py"
  python scripts/ai/file_processing/search_replace.py --directory . --pattern "console\.log\(.*\)" --replacement "logger.info" --file-pattern "*.js" --dry-run
"""

import sys
import re
import argparse
import logging
from pathlib import Path
import shutil
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_files(directory, file_pattern):
    """查找匹配的文件"""
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")
    
    # 转换glob模式
    if file_pattern:
        files = list(directory.rglob(file_pattern))
    else:
        files = [f for f in directory.rglob("*") if f.is_file()]
    
    return files

def search_in_file(file_path, pattern, use_regex=True):
    """在文件中搜索模式"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if use_regex:
            matches = re.findall(pattern, content, re.MULTILINE)
            return len(matches) > 0, matches
        else:
            return pattern in content, [pattern] if pattern in content else []
    
    except UnicodeDecodeError:
        logger.warning(f"无法读取文件（编码问题）: {file_path}")
        return False, []
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        return False, []

def replace_in_file(file_path, pattern, replacement, use_regex=True, create_backup=False):
    """在文件中替换内容"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        if use_regex:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            new_content = content.replace(pattern, replacement)
        
        if new_content != original_content:
            # 创建备份
            if create_backup:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copy2(file_path, backup_path)
                logger.info(f"创建备份: {backup_path}")
            
            # 写入新内容
            file_path.write_text(new_content, encoding='utf-8')
            
            # 计算替换次数
            if use_regex:
                replace_count = len(re.findall(pattern, original_content, re.MULTILINE))
            else:
                replace_count = original_content.count(pattern)
            
            return True, replace_count
        
        return False, 0
    
    except Exception as e:
        logger.error(f"替换文件内容失败 {file_path}: {e}")
        return False, 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='文件内容搜索替换工具')
    parser.add_argument('--directory', required=True, help='搜索目录路径')
    parser.add_argument('--pattern', required=True, help='搜索模式')
    parser.add_argument('--replacement', help='替换内容（搜索模式时可选）')
    parser.add_argument('--file-pattern', help='文件名模式（如 *.py）')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际修改')
    parser.add_argument('--backup', action='store_true', help='创建备份文件')
    parser.add_argument('--no-regex', action='store_true', help='不使用正则表达式')
    parser.add_argument('--case-insensitive', action='store_true', help='忽略大小写')
    args = parser.parse_args()
    
    try:
        # 查找文件
        logger.info(f"在目录 {args.directory} 中查找文件...")
        files = find_files(args.directory, args.file_pattern)
        logger.info(f"找到 {len(files)} 个文件")
        
        if not files:
            logger.warning("没有找到匹配的文件")
            return
        
        # 调整正则表达式标志
        use_regex = not args.no_regex
        if args.case_insensitive and use_regex:
            pattern = f"(?i){args.pattern}"
        else:
            pattern = args.pattern
        
        # 搜索和替换
        total_files_found = 0
        total_files_modified = 0
        total_replacements = 0
        
        for file_path in files:
            # 搜索
            found, matches = search_in_file(file_path, pattern, use_regex)
            
            if found:
                total_files_found += 1
                logger.info(f"找到匹配: {file_path}")
                
                if args.replacement is not None:
                    # 替换模式
                    if args.dry_run:
                        logger.info(f"  [预览] 将替换 {len(matches)} 处匹配")
                    else:
                        modified, replace_count = replace_in_file(
                            file_path, pattern, args.replacement, use_regex, args.backup
                        )
                        if modified:
                            total_files_modified += 1
                            total_replacements += replace_count
                            logger.info(f"  替换了 {replace_count} 处匹配")
                else:
                    # 仅搜索模式
                    logger.info(f"  匹配内容: {matches[:3]}{'...' if len(matches) > 3 else ''}")
        
        # 输出总结
        logger.info(f"\n总结:")
        logger.info(f"  检查文件数: {len(files)}")
        logger.info(f"  找到匹配的文件数: {total_files_found}")
        
        if args.replacement is not None:
            if args.dry_run:
                logger.info(f"  [预览模式] 将修改的文件数: {total_files_found}")
            else:
                logger.info(f"  实际修改的文件数: {total_files_modified}")
                logger.info(f"  总替换次数: {total_replacements}")
        
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()