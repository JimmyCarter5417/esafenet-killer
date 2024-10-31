import os
import subprocess
import sys

ext = ".bin"

def process_directory(src_dir, dst_dir):
    print("src_dir: %s, dst_dir: %s" % (src_dir, dst_dir))

    # 确保输出目录存在
    print("make dst_dir: %s" % (dst_dir))
    os.makedirs(dst_dir, exist_ok=True)

    # 获取根目录下的所有文件和子目录
    for entry in os.listdir(src_dir):
        src_entry = os.path.join(src_dir, entry)
        dst_entry = os.path.join(dst_dir, entry)

        if os.path.isdir(src_entry):
            # 如果是目录，递归处理
            print("[dir] %s -> %s" % (src_entry, dst_entry))
            process_directory(src_entry, dst_entry)
        elif os.path.isfile(src_entry):
            # 如果是文件，执行解密
            print("[file] %s -> %s" % (src_entry, dst_entry))
            dst_entry += ext # 带上.bin后缀，防止加密
            command = ["./notepad++.exe", src_entry, dst_entry]
            subprocess.run(command)
            # 通过 cp 命令还原原始文件名，只有 cp 命令不会加密，mv / ren / copy 都会加密
            command = ["cp", dst_entry, dst_entry.removesuffix(ext)]
            subprocess.run(command)
            # 删除 bin 文件
            os.remove(dst_entry)

if __name__ == "__main__":
    src_dir = sys.argv[1]
    dst_dir = sys.argv[2]

    process_directory(src_dir, dst_dir)
