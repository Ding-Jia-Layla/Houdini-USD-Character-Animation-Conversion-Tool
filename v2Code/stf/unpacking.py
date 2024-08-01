first_part = [1, 2, 3]
second_part = [4, 5, 6]

# 合并列表
combined = [*first_part, *second_part]
print(combined)  # 输出: [1, 2, 3, 4, 5, 6]

# 解包元组进行赋值
a, *b, c = [1, 2, 3, 4, 5]
print("a:", a)  # a: 1
print("b:", b)  # b: [2, 3, 4]
print("c:", c)  # c: 5
