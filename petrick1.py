from dst import TableEntry
from tkinter import _flatten

class Petrick:
    def __init__(self, minterms, maxterms, dont_cares, dimension, variable_names, return_name):
        self.minterms = minterms
        self.maxterms = maxterms
        self.dont_cares = dont_cares
        self.dimension = dimension
        self.variable_names = variable_names
        self.return_name = return_name
        self.sop_essentials = []
        self.pos_essentials = []

    def calculate_sop_essentials(self):
        all_terms = self.minterms + self.dont_cares  # 合并最小项和不关心项
        self.sop_essentials = []  # 初始化SOP基本项列表
        groups = self.groupTerms(all_terms, True)  # 获取分组项
        reduced_groups = self.reduceGroupedTerms(groups, True)[:len(groups)]  # 简化分组项
        prime_implicants = self.getPrimeImplicants(reduced_groups)  # 获取主要蕴含项
        columns = self.getColumns(prime_implicants, True)  # 基于主要蕴含项获取列
        reduced_columns = self.reduceColumns(columns)  # 简化列
        self.sop_essentials = self.sop_essentials + (self.getEssentialImplicants(reduced_columns)) # 合并基本蕴含项

    
    def calculate_pos_essentials(self):
        all_terms = self.maxterms + self.dont_cares # 合并最大项和不关心项
        self.pos_essentials = []  # 初始化POS基本项列表
        groups = self.groupTerms(all_terms, False) # 获取分组项，第二个参数False表示是POS形式
        reduced_groups = self.reduceGroupedTerms(groups, False)[:len(groups)] # 简化分组项并去除最后一个元素（如果有）
        prime_implicants = self.getPrimeImplicants(reduced_groups) # 获取主要蕴含项
        columns = self.getColumns(prime_implicants, False) # 基于主要蕴含项获取列
        reduced_columns = self.reduceColumns(columns) # 简化列
        self.pos_essentials.extend(self.getEssentialImplicants(reduced_columns)) # 合并获取的基本蕴含项


    def get_sop_essentials(self):
        # 创建一个空列表来存储结果
        ess_arr = []
        # 遍历sopEssentials列表，并收集每个项的术语
        for t in self.sop_essentials:
            ess_arr.append(t.getTerms())  # 假设TableEntry类有一个getTerms方法
        return ess_arr  # 返回包含术语的列表
    
    def get_pos_essentials(self):
        # 创建一个空列表来存储结果
        ess_arr = []
        # 遍历sopEssentials列表，并收集每个项的术语
        for t in self.pos_essentials:
            ess_arr.append(t.getTerms())  # 假设TableEntry类有一个getTerms方法
        return ess_arr  # 返回包含术语的列表
    
    def get_sop_generic(self):
        # 开始构建输出字符串
        output = f"{self.return_name}({', '.join(self.variable_names)}) = "
        # 如果sopEssentials为空，则直接返回0
        if len(self.sop_essentials) == 0:
            return output + "0"
        
        # 如果sopEssentials只有一个全0的项，则返回1
        if len(self.sop_essentials) == 1 and self.sop_essentials[0].getBinaryRep() == "-" * self.dimension:
            return output + "1"
        
        # 遍历sopEssentials中的每个项
        for e in self.sop_essentials:
            entry_string = e.getBinaryRep()  # 假设TableEntry类有一个getBinaryRep方法
            for i, c in enumerate(entry_string):
                if c == "0":
                    output += f"{self.variable_names[i]}'"
                elif c == "1":
                    output += f"{self.variable_names[i]}"
            output += " + "
        
        # 移除最后的" + "，然后返回结果字符串
        return output[:-3]

    def get_pos_generic(self):
        # 开始构建输出字符串
        output = f"{self.return_name}({', '.join(self.variable_names)}) = "
        
        # 如果posEssentials为空，则直接返回1
        if len(self.pos_essentials) == 0:
            return output + "1"
        
        # 如果posEssentials只有一个全不关心的项，则返回0
        if len(self.pos_essentials) == 1 and self.pos_essentials[0].getBinaryRep() == "-" * self.dimension:
            return output + "0"
        
        # 遍历posEssentials中的每个项
        for e in self.pos_essentials:
            output += "("
            entry_string = e.getBinaryRep()  # 假设每个项有一个getBinaryRep方法
            for i, c in enumerate(entry_string):
                if c == "0":
                    output += f"{self.variable_names[i]} + "
                elif c == "1":
                    output += f"{self.variable_names[i]}' + "
            output = output[:-3] + ")"
        
        # 移除最后的" + "，然后返回结果字符串
        return output
    
    def groupTerms(self, terms, sop):
        groups = self.create_groups_array()  # 创建分组数组
        for term in terms:  # 遍历项
            num_ones = self.number_of(term, sop)  # 计算term中1的个数
            groups[num_ones].append(TableEntry([term], self.dimension))  # 添加到对应的组
        return groups
    
    def reduceGroupedTerms(self, grouped_terms, sop):
        groups = self.create_groups_array()  # 创建分组数组
        merged_entries = self.create_groups_array()  # 创建用于存储合并项的数组
        cont = False  # 控制递归继续的标志

        for i in range(len(grouped_terms) - 1):
            for j in range(i + 1, len(grouped_terms)):
                for t1 in grouped_terms[i]:
                    for t2 in grouped_terms[j]:
                        merged = False
                        merged = self.check_table_entries(t1, t2, groups, sop)
                        if merged:
                            merged_entries[i].append(t1)
                            merged_entries[j].append(t2)
                        cont = cont or merged

        for i in range(len(groups)):
            # 使用列表推导式和enumerate过滤重复项
            seen = set()
            groups[i] = [filtVal for filtVal in groups[i] if not 
                         (filtVal.getBinaryRep() in seen or seen.add(filtVal.getBinaryRep()))]
            # 过滤掉mergedEntries中已经包含的项
            grouped_terms[i] = [val for val in grouped_terms[i] if val not in merged_entries[i]]

        if cont:
            return [grouped_terms] + self.reduceGroupedTerms(groups, sop)
        else:
            return [grouped_terms] + [groups]
        
    def getPrimeImplicants(self, reduced_groups):
        prime_implicants = []  # 创建一个空列表来存储主要蕴含项
        for group in reduced_groups:  # 遍历每个组
            for entry in group:  # 遍历组中的每个项
                prime_implicants.extend(entry)  # 将项添加到主要蕴含项列表
        return prime_implicants  # 返回主要蕴含项列表
    
    def getColumns(self, prime_implicants, sop):
        columns = {}  # 创建一个字典来存储列
        essentials = []  # 创建一个空列表来存储基本蕴含项
        terms = self.minterms if sop else self.maxterms  # 根据sop选择最小项或最大项

        for term in terms:
            columns[term] = [[implicant ]for implicant in prime_implicants if term in implicant.getTerms()]

        # 检查每个列，如果只有一个项，则将其添加到基本蕴含项列表
        for key, value in list(columns.items()):
            if key in columns and len(value) == 1:
                essentials.append(value[0][0])  # 添加到基本蕴含项列表
                for k in value[0][0].getTerms():  # 从所有列中移除已处理的项
                    if k in columns:
                        del columns[k]
        # 创建剩余列的数组
        column_arr = []
        for key, value in columns.items():
            # 使用列表推导式来筛选 'value' 中不在 'essentials' 中的项
            filtered_value = [v for v in value if v[0] not in essentials]
            # 将筛选后的列表添加到 'columnArr' 中
            column_arr.append(filtered_value)

        # 根据sop更新类属性
        if sop:
            self.sop_essentials = essentials
        else:
            self.pos_essentials = essentials

        return column_arr
    
    def reduceColumns(self, columns):
        # print(columns)
        if len(columns) <= 1:
            return columns
        column1 = columns[0]
        column2 = columns[1]
        new_column = []
        
        # 合并两个列，并去除重复项
        for c1 in column1:
            for c2 in column2:
                temp = []
                temp.extend(c1)
                temp.extend(c2) # 合并两个项
                # 确保每个项只出现一次
                temp = [item for i, item in enumerate(temp) if temp.index(item) == i]
                new_column.append(temp)
        
        # 简化新列，移除冗余项
        new_column = self.simplifyColumn(new_column)
        new_columns = [new_column] + columns[2:] # 将新列和剩余的列组合

        # 如果新列的数量大于1，则递归调用reduceColumns，否则返回新列
        if len(new_columns) > 1:
            return self.reduceColumns(new_columns)
        else:
            return new_columns
    
    def getEssentialImplicants(self, reduced_columns):
        if len(reduced_columns) == 0:
            return []
        
        options = reduced_columns[0]
        if options is not None and len(options) > 0:
            # 按照长度对options进行排序
            options = sorted(options, key=lambda a: len(a))
            # 返回排序后数组的第一个元素
            return options[0]
        else:
            return []
        
    def simplifyColumn(self, column):
        return_column = [item for i, item in enumerate(column) if column.index(item) == i]
        i = 0
        while i < len(return_column) - 1:
            j = i + 1
            while j < len(return_column):
                if self.matchesIdentify(return_column[i], return_column[j]):
                    return_column = return_column[:j] + return_column[j+1:]
                elif self.matchesIdentify(return_column[j], return_column[i]):
                    return_column = return_column[:i] + return_column[i+1:]
                j += 1
            i += 1
        
        return return_column
    
    def matchesIdentify(self, x, xy):
        for t in x:
            if t not in xy:
                return False
        return True
    
    def number_of(self, val, ones):
        ret = 0
        while val:
            ret += val & 1
            val >>= 1
        ret = ret if ones else self.dimension - ret
        return ret

    def char_in_string(self, s, ones):
        return s.count('1') if ones else s.count('0')

    def create_groups_array(self):
        n_groups = self.dimension + 1
        groups = [[] for _ in range(n_groups)]  # 创建一个由空列表组成的列表
        return groups
    
    def check_table_entries(self, t1, t2, groups, sop):
        if t1.is_adjacent(t2):  # 检查t1和t2是否相邻
            t3 = t1.mergeEntry(t2)  # 合并t1和t2生成新的项t3
            num_ones = self.char_in_string(t3.getBinaryRep(), sop)  # 计算t3的二进制表示中1的个数
            groups[num_ones].append(t3)  # 将t3添加到对应的组
            return True
        return False
    
import time

start_time = time.perf_counter()  # 记录开始时间
# 示例使用
minterms = [4,5,10,11,12]  # 示例最小项
maxterms = [0,15,1]            # 示例最大项，这里为空列表
dont_cares = [2,3,6,7,8,9,13,14]     # 示例不关心项
dimension = 4            # 维度，例如4个变量
variable_names = ['a', 'b', 'c', 'd']  # 变量名称
return_name = 'f'       # 返回值名称

# minterms = [1, 2, 3, 4, 6, 9]  # 示例最小项
# maxterms = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]            # 示例最大项，这里为空列表
# dont_cares = [0]     # 示例不关心项
# dimension = 4            # 维度，例如4个变量
# variable_names = ['a', 'b', 'c', 'd']  # 变量名称
# return_name = 'f'       # 返回值名称

petrick = Petrick(minterms, maxterms, dont_cares, dimension, variable_names, return_name)

# 访问属性
petrick.calculate_sop_essentials()
petrick.get_sop_generic()
print(petrick.get_sop_generic())

end_time = time.perf_counter()  # 记录结束时间
elapsed_time_ms = (end_time - start_time) * 1000  # 转换为毫秒
print(f"Elapsed time with high precision: {elapsed_time_ms:.2f} ms")
# 修改属性
petrick.minterms = [0, 1, 2, 3]

# 示例使用
petrick = Petrick(minterms, maxterms, dont_cares, dimension, variable_names, return_name)
groups = petrick.create_groups_array()