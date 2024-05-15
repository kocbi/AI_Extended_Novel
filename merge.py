import os

# 定义要合并的txt文件所在的文件夹路径
folder_path = '../data/3'



# 定义要输出的合并后的txt文件路径及文件名
output_file = '../data/scifi.txt'

# 打开输出文件，以追加模式写入
with open(output_file, 'a', encoding='utf-8') as output:
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否是txt文件
        if filename.endswith('.txt'):
            # 获取txt文件的路径
            file_path = os.path.join(folder_path, filename)
            # 打开txt文件，以读取模式读取内容
            with open(file_path, 'r', encoding='utf-8') as file:
                # 将当前txt文件的内容写入输出文件
                output.write(file.read())
                # 添加换行符分隔不同文件内容
                output.write('\n')