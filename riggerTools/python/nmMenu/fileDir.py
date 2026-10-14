import os.path

path = os.path.dirname(os.path.abspath(__file__))
#tmp_path = 'D:\studio_pipeline\Tools\riggerTools\python\nmMenu'
#newPath = tmp_path.replace(os.sep, '/')
abs_path = os.path.normpath(path)


cut_path = abs_path.replace(r'\python\nmMenu','')
# D:\studio_pipeline\Tools\riggerTools
print(cut_path)
