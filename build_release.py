import os
import shutil
import zipfile
import re

def get_plugin_version(init_file_path):
    """从 __init__.py 中读取插件版本"""
    try:
        with open(init_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'"version":\s*\(([^,]+),\s*([^,]+),\s*([^)]+)\)', content)
            if match:
                return f"{match.group(1).strip()}.{match.group(2).strip()}.{match.group(3).strip()}"
    except FileNotFoundError:
        print(f"Warning: __init__.py not found at {init_file_path}. Using default version.")
    return "0.0.0"

def build_release():
    project_root = os.path.dirname(os.path.abspath(__file__))

    # --- 用户需要修改的部分 ---
    project_base_name = "L4D2_Character_Tools"  # 用于zip文件名 (例如: L4D2_Character_Tools)
    blender_addon_folder_name = "L4D2_Character_Tools" # Blender安装后在addons目录下的文件夹名
    # --- 用户需要修改的部分结束 ---

    # 定义需要包含在发布包中的文件和目录（相对于项目根目录）
    include_files_and_dirs = [
        'resources', # 这是一个目录
        'bone_dict.py',
        'flex_dict.py',
        'flexmix_presets.py',
        'jiggleparams_presets.py',
        'presets', # 这是一个目录
        '__init__.py',
        'bone_modify.py',
        'flex.py',
        'jigglebone.py',
        'translation.py',
        'updatelog.txt',
        'vrd.py',
        'weights.py',
        # 'LICENSE',
    ]

    # 获取版本号 (从 __init__.py 读取)
    version = get_plugin_version(os.path.join(project_root, '__init__.py'))
    
    # 构造最终的zip文件名
    zip_filename = f"{project_base_name}-v{version}.zip"

    # 创建一个临时目录用于构建发布包
    build_dir = os.path.join(project_root, "release_build")
    temp_plugin_root_in_build = os.path.join(build_dir, blender_addon_folder_name)

    # 清理旧的构建目录
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(temp_plugin_root_in_build, exist_ok=True)

    print(f"Preparing files for {blender_addon_folder_name} v{version}...")

    # 复制指定的文件和目录到临时插件根目录
    # 注意：这里不再使用 ignore_pycache 函数，因为我们将在打包zip时进行更严格的过滤
    for item_name in include_files_and_dirs:
        source_path = os.path.join(project_root, item_name)
        destination_path = os.path.join(temp_plugin_root_in_build, item_name)

        if not os.path.exists(source_path):
            print(f"Warning: Source item '{item_name}' not found. Skipping.")
            continue

        if os.path.isdir(source_path):
            # 直接复制整个目录，包括可能的 __pycache__，我们稍后在打包时过滤
            shutil.copytree(source_path, destination_path, symlinks=False)
            print(f"  Copied directory: {item_name}/")
        else:
            shutil.copy2(source_path, destination_path)
            print(f"  Copied file: {item_name}")

    final_zip_path = os.path.join(project_root, zip_filename)

    print(f"Creating zip archive: {final_zip_path}...")
    with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历临时插件根目录，将其内容添加到zip文件中
        for root, dirs, files in os.walk(temp_plugin_root_in_build):
            # 过滤掉 dirs 列表中的 __pycache__，这样 os.walk 就不会进入这些目录
            # 注意：修改 dirs 列表会影响 os.walk 的遍历行为
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                # 过滤掉 __pycache__ 中的文件
                if '__pycache__' in root:
                    continue # 如果文件在 __pycache__ 目录中，则跳过

                file_path = os.path.join(root, file)
                # 计算在zip文件中的相对路径
                arcname = os.path.relpath(file_path, build_dir)
                zipf.write(file_path, arcname)
            
            # 处理空目录，确保 __pycache__ 目录不会作为空目录被添加
            for dir_name in dirs: # dirs 此时已经排除了 __pycache__
                dir_path = os.path.join(root, dir_name)
                # 检查是否是空目录
                if not os.listdir(dir_path):
                    arcname = os.path.relpath(dir_path, build_dir)
                    zipf.writestr(arcname + '/', '')

    print(f"Cleaning up temporary build directory: {build_dir}...")
    shutil.rmtree(build_dir)

    print(f"Successfully created release package: {final_zip_path}")

if __name__ == "__main__":
    build_release()
