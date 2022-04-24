class Container_GA(object):
    """
    集装箱遗传算法
    """
    def __init__(self, data: list = None, weight_min: int = 0, weight_max: int = 9999, population_size: int = 10, epoch: int = 100, crossover_rate: float = 0.2, mutation_rate: float = 0.01):
        """
        初始化
        :param data: 数据 [{"sku": "aa",
                     "weight": 1,
                     "value": 3},]
        :param population_size: 种群大小
        :param epoch: 迭代次数
        :param crossover_rate: 交叉概率
        :param mutation_rate: 变异概率
        """
        if data is None:
            data = [{"sku": "aa",
                     "weight": 1,
                     "value": 3},
                    {"sku": "bb",
                     "weight": 2,
                     "value": 2},
                    {"sku": "cc",
                     "weight": 4,
                     "value": 6},
                    {"sku": "dd",
                     "weight": 6,
                     "value": 8},
                    ]
        self.data = data
        self.weight_min = weight_min
        self.weight_max = weight_max
        self.population_size = population_size
        self.epoch = epoch
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.chromosome_length = len(data)
        self.n = 4
        self.code_rule = ["0", "0", "0", "0", "1"] # 用于针对特殊情况需要让编码0,1不等概率产生

    def update_code_rule(self):
        """
        更新被选择的0,1个数
        :return:
        """
        self.code_rule = ["0"] * self.n + ["1"]


    def fitness(self, population: list):
        """
        适应度计算. 计算该染色体的重量, 价值
        :param population: [{"chromosome": ""},]
        :return:[{"chromosome": "","weight": 0, "value": 0}]
        """
        new_population = []
        local_best = {"chromosome": "","weight": 0, "value": 0} # 记录本次最佳解决方案
        for i in population:
            fitness_value = {"chromosome": "", "weight": 0, "value": 0}
            fitness_value["chromosome"] = i["chromosome"]
            chromosome_split = list(i["chromosome"])
            for key, value in enumerate(chromosome_split):
                if value == "1":
                    fitness_value["value"] += self.data[key]["value"]
                    fitness_value["weight"] += self.data[key]["weight"]
            new_population.append(fitness_value)
            # 判断当前染色体价值是否大于历史
            if fitness_value["value"] > local_best["value"]:
                local_best["value"] = fitness_value["value"]
                local_best["weight"] = fitness_value["weight"]
                local_best["chromosome"] = fitness_value["chromosome"]
        return new_population, local_best

    def selection(self, population: list):
        """
        选择.

        :param population:{"chromosome": "", "weight": 0, "value": 0}
        :return:
        """
        population_bak = population.copy()
        for key, value in reversed(list(enumerate(population_bak))):
            # 排除掉超重或不足的个体
            if value["weight"] > self.weight_max or value["weight"] < self.weight_min:
                population_bak.pop(key)
        # 轮盘赌:价值越大被选中的概率越大
        total_value = 0 # 种群总适应值
        for i in population_bak:
            total_value += i["value"]
        # 计算每个个体被选择概率
        for key, value in enumerate(population_bak):
            value["p"] = value["value"] / total_value # 被选择概率
            population_bak[key] = value
        # 计算每个个体的累计概率
        for key, value in enumerate(population_bak):
            if key == 0:
                value["q"] = value["p"]
            else:
                value["q"] = value["p"] + population_bak[key - 1]["q"] # 累计概率
            population_bak[key] = value

        # 轮盘赌转动population_size, 选出population_size个个体
        parent_population = []
        for num in range(self.population_size):
            # 随机数
            r = random.random()
            # 遍历种群选择q_k-1<r<q_k的种群, 选择第k个个体
            for key, value in enumerate(population_bak):
                if key == 0 and r <= value["q"]:
                    parent_population.append(value)
                if value["q"] < r and r < population_bak[key + 1]["q"]:
                    parent_population.append(population_bak[key + 1])
                    break
        return parent_population

    def crossover(self, population: list):
        """
        杂交操作
        :param population: 种群 [{"chromosome":""},]
        :return:
        """
        # 根据重组率, 判断每个个体被选择来重组的
        while True:
            selected = np.random.random(self.population_size) < self.crossover_rate
            # 保证偶数个
            if sum(selected) % 2 == 0:
                break

        # 配对重组
        crossover_candidate = [] # 选择重组个体
        crossover_generation = [] # 重组之后的子代
        for key, value in enumerate(selected):
            if value:
                crossover_candidate.append(population[key])

        # 打乱crossover_candidate顺序
        random.shuffle(crossover_candidate)
        for i in range(0, len(crossover_candidate), 2):
            # 产生杂交位点
            pos = random.randint(0, self.chromosome_length)
            # 两条染色体交叉
            chromosome1 = crossover_candidate[i]["chromosome"]
            chromosome2 = crossover_candidate[i+1]["chromosome"]
            temp1 = chromosome1[pos:]
            temp2 = chromosome2[pos:]
            chromosome1 = chromosome1[:pos] + temp2
            chromosome2 = chromosome2[:pos] + temp1
            crossover_generation.append({"chromosome": chromosome1})
            crossover_generation.append({"chromosome": chromosome2})
        # pop掉被选重组的父代, append重组之后的子代
        for key, value in reversed(list(enumerate(selected))):
            if value:
                population.pop(key)
        for i in crossover_generation:
            population.append(i)
        return population

    def mutation(self, population: list):
        """
        变异操作
        对每一个染色体的每一个基因位产生随机数, 若小于mutation_rate则变异
        :param population: [{"chromosome":""},]
        :return:
        """
        for index, individual in enumerate(population):
            # 判断是否突变
            mutation = np.random.random(self.chromosome_length) < self.mutation_rate
            chromosome_list = list(individual["chromosome"])
            for key, value in enumerate(mutation):
                if value:
                    # 突变操作
                    chromosome_list[key] = "0" if chromosome_list[key] == "1" else "1"
                    individual["chromosome"] = "".join(chromosome_list)
            population[index] = individual
        return population

    def init_population(self):
        """
        初始化种群
        :return:
        """
        chromosome_list = []
        for i in range(self.population_size):
            # 方案一: 随机产生0,1, 两者概率相等
            # chromosome = "".join([str(_) for _ in np.random.randint(0, 2, self.chromosome_length)])
            # 方案二: 随机产生0,1, 两者概率不等
            chromosome = "".join([random.choice(self.code_rule) for x in range(self.chromosome_length)])
            chromosome_list.append({"chromosome": chromosome})
        return chromosome_list

    def run(self):
        """
        主函数
        :return:
        """
        # 只有一个元素的
        if self.chromosome_length == 1:
            return [True]
        # 记录历史子代中local最佳个体
        all_best = {"chromosome": "", "weight": 0, "value": 0}
        # 记录每一代最佳个体
        epoch_best_list = []
        # 初始化种群, 直至产生适应环境的初始种群
        while True:
            init_population = self.init_population()
            population_fitness, local_best = self.fitness(init_population)
            population_selection = self.selection(population_fitness)
            if len(population_selection) != 0:
                break
            # 初始种群不符合要求, 加大n, 提高编码0的数量
            self.n += 1
            # 更新0,1概率
            self.update_code_rule()

        for epoch in range(self.epoch):
            # 计算适应度, 和当代最优秀个体
            population_fitness, local_best = self.fitness(init_population)
            # 选择操作
            population_selection = self.selection(population_fitness)
            # 排除超重, 过轻
            _, local_best = self.fitness(population_selection)
            # 重组操作
            population_crossover = self.crossover(population_selection)
            # 变异操作
            population_mutation = self.mutation(population_crossover)
            # 经过一代之后产生新的子代, 赋值给初始种群变量, 进行下一次运行
            init_population = population_mutation
            # 存储local最佳个体
            epoch_best_list.append(local_best)
            # 判断该代的适应度是否比以前更优
            if all_best["value"] < local_best["value"]:
                all_best = local_best

        # 最佳染色体
        self.all_best = all_best
        best_chromosome = all_best["chromosome"]
        # 解码返回原data长度的True False
        result = []
        for i in list(best_chromosome):
            if i == "1":
                result.append(True)
            else:
                result.append(False)
        return result