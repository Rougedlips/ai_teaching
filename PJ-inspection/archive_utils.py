"""Archive utilities for handling compressed project inputs."""
from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from typing import Tuple

try:
    import rarfile  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    rarfile = None

RAR_TOOL_CANDIDATES = ('unar', 'unrar', 'rar', '7z', 'bsdtar')

SUPPORTED_ARCHIVE_EXTENSIONS = {'.zip', '.rar'}


class ArchiveExtractionError(Exception):
    """Raised when an archive cannot be processed safely."""


def is_supported_archive(archive_path: str) -> bool:
    """Return True if the provided path points to a supported archive file."""
    _, extension = os.path.splitext(archive_path or '')
    return extension.lower() in SUPPORTED_ARCHIVE_EXTENSIONS


def _ensure_within_directory(base_directory: str, target_path: str) -> None:
    """Validate that the extracted member stays within the destination directory."""
    normalized_base = os.path.abspath(base_directory)
    normalized_target = os.path.abspath(target_path)
    if os.path.commonpath([normalized_base, normalized_target]) != normalized_base:
        raise ArchiveExtractionError('检测到压缩包包含不安全的路径，已终止解压。')


def _safe_extract_zip(zip_file: zipfile.ZipFile, destination_directory: str) -> None:
    for member in zip_file.infolist():
        member_path = os.path.join(destination_directory, member.filename)
        _ensure_within_directory(destination_directory, member_path)
    zip_file.extractall(destination_directory)




def extract_archive(archive_path: str) -> Tuple[str, str]:
    """Extract the archive into a temporary directory and return (temp_dir, display_name)."""
    if not archive_path:
        raise ArchiveExtractionError('未提供压缩包路径。')

    absolute_path = os.path.abspath(archive_path)
    if not os.path.exists(absolute_path):
        raise ArchiveExtractionError('压缩包不存在，请检查路径。')

    _, extension = os.path.splitext(absolute_path)
    extension = extension.lower()
    if extension not in SUPPORTED_ARCHIVE_EXTENSIONS:
        raise ArchiveExtractionError('当前仅支持 ZIP 或 RAR 格式的压缩包。')

    temporary_directory = tempfile.mkdtemp(prefix='code_review_archive_')
    display_name = os.path.basename(absolute_path)

    try:
        if extension == '.zip':
            with zipfile.ZipFile(absolute_path) as zip_handle:
                _safe_extract_zip(zip_handle, temporary_directory)
        else:
            if rarfile is None:
                raise ArchiveExtractionError(
                    '缺少 rarfile 依赖，请执行 pip install rarfile'
                )

            if not rarfile.is_rarfile(absolute_path):
                raise ArchiveExtractionError('文件不是有效的 RAR 压缩包')

            rar_executable = rarfile.UNRAR_TOOL
            if not rar_executable:
                rar_executable = rarfile.UNAR_TOOL

            if not rar_executable:
                for fallback_tool in RAR_TOOL_CANDIDATES:
                    if rarfile._check_unrar_tool(fallback_tool):
                        rar_executable = fallback_tool
                        break

            if not rar_executable:
                raise ArchiveExtractionError(
                    '未检测到可用的 RAR 解压工具，请安装 unar 或 unrar。'
                )

            rarfile.UNRAR_TOOL = rar_executable

            try:
                with rarfile.RarFile(absolute_path) as rar_handle:
                    _safe_extract_zip(rar_handle, temporary_directory)
            except rarfile.Error as extraction_error:
                raise ArchiveExtractionError(
                    f'RAR 解压失败: {extraction_error}'
                ) from extraction_error
    except Exception:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise

    # 检查解压后的目录结构，如果只有一个子目录，使用该子目录作为根目录
    extracted_items = os.listdir(temporary_directory)
    extracted_items = [item for item in extracted_items if not item.startswith('.')]
    
    if len(extracted_items) == 1:
        single_item = os.path.join(temporary_directory, extracted_items[0])
        if os.path.isdir(single_item):
            # 如果只有一个子目录，使用该目录作为实际的工作目录
            return single_item, display_name

    return temporary_directory, display_name


def cleanup_temp_directory(temporary_directory: str) -> None:
    """Remove the temporary directory created during archive extraction."""
    if temporary_directory and os.path.isdir(temporary_directory):
        shutil.rmtree(temporary_directory, ignore_errors=True)
