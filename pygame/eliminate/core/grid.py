import logging
import math
import random

from core.main_config import MainConfig
from core.strategy import high_order_first
from domain.cell_state import CellState
from domain.cell_vo import CellVO
from domain.direct_type import DirectType
from domain.enum_type import CellType, min_order_type, StrategyType, OrderType
from domain.monster import Monster
from domain.soldier import Soldier
from domain.stone import Stone
from util.logger import log


class Grid:
    def __init__(self, grid_id=0):
        self.configs = MainConfig()
        self.current_grid = self.configs.grids[grid_id]
        self.row = self.current_grid['row']
        self.col = self.current_grid['col']
        # TODO use dict, more quickly?
        self.grid = []  # Monster or  Stone Object
        self.type_count = {}

        # direct ->[CellState]
        self.direct_states = {}  # able to eliminate (length more than 2)
        self.probably_eliminate = {}  # probably to eliminate (length equal to 2)

        self.soldiers = {}  # (ref_id, order,level) -> soldier synthesizer then go on battle

        # init monster count
        for monster in self.configs.monsters:
            self.type_count[monster['id']] = 0

    def init_generate_grid(self):
        data = self.current_grid['data']
        for index in range(len(data)):
            type_ = data[index]
            if type_ == CellType.MONSTER.value:
                self.grid.append(self.create_monster(index))
            if type_ == CellType.STONE.value:
                self.grid.append(self.create_stone(index))

        while True:
            self.check_eliminate()
            for direct in self.direct_states:
                states = self.direct_states[direct]
                for state in states:
                    indexes = state.indexes
                    index = random.choice(indexes)

                    monster = self.grid[index]
                    monster.ref_id = self.replace_monster_with_other(monster.ref_id)

            self.check_eliminate()
            # self.simple_show()
            # log.debug('check %s' % self.direct_states)
            if len(self.direct_states) == 0:
                break

    @staticmethod
    def create_stone(index):
        return Stone(index, Stone.random_hp())

    def create_monster(self, index):
        return Monster(index, self.random_monster_ref(), min_order_type())

    def replace_monster_with_other(self, ref_id) -> str:
        self.type_count[ref_id] -= 1
        ids = []
        for monster in self.configs.monsters:
            if monster['id'] != ref_id:
                ids.append(monster['id'])
        other_id = random.choice(ids)
        return other_id

    def random_monster_ref(self) -> str:
        # return 'X'

        # monster_dict = random.choice(self.configs.monsters)
        # ref_id = monster_dict['id']
        # self.type_count[ref_id] += 1
        # return ref_id

        ref_id = random.choice(self.get_monster_resources())
        self.type_count[ref_id] += 1
        return ref_id

    def get_monster_resources(self) -> []:
        result = []
        max_count = max(self.type_count.values())

        for ref_id in self.type_count:
            if self.type_count[ref_id] != max_count:
                result.append(ref_id)

        if len(result) == 0:
            return list(self.type_count.keys())
        return result

    def check_eliminate(self):
        self.direct_states = {}
        self.probably_eliminate = {}

        self.check_east()
        self.check_south()
        self.check_north_east()
        self.check_south_east()

    def check_east(self):
        for x in range(self.row):
            temp = []
            for y in range(0, self.col):
                cell = self.grid[self.col * x + y]
                temp = self.compare_monster(cell, temp, DirectType.EAST)
            self.add_monster(temp, DirectType.EAST)

    def check_south(self):
        for y in range(self.col):
            temp = []
            for x in range(self.row):
                cell = self.grid[self.col * x + y]
                temp = self.compare_monster(cell, temp, DirectType.SOUTH)
            self.add_monster(temp, DirectType.SOUTH)

    def check_south_east(self):
        for i in range(self.col - 2):
            temp = []
            for j in range(i, (self.row - i) * self.col, self.col + 1):
                cell = self.grid[j]
                temp = self.compare_monster(cell, temp, DirectType.SOUTH_EAST)
            self.add_monster(temp, DirectType.SOUTH_EAST)

        for i in range(self.col, self.col * (self.row - 1), self.col):
            temp = []
            for j in range(i, self.col * self.row, self.col + 1):
                cell = self.grid[j]
                temp = self.compare_monster(cell, temp, DirectType.SOUTH_EAST)
            self.add_monster(temp, DirectType.SOUTH_EAST)

    def check_north_east(self):
        for i in range(1, self.col):
            temp = []
            for j in range(i, i * self.col + 1, self.col - 1):
                cell = self.grid[j]
                temp = self.compare_monster(cell, temp, DirectType.NORTH_EAST)
            self.add_monster(temp, DirectType.NORTH_EAST)

        if self.row < 3:
            return
        for i in range(self.col * 2 - 1, (self.row - 1) * self.col - 1, self.col):
            temp = []
            for j in range(i, self.row * self.col - 1, self.col - 1):
                cell = self.grid[j]
                temp = self.compare_monster(cell, temp, DirectType.NORTH_EAST)
            self.add_monster(temp, DirectType.NORTH_EAST)

    def compare_monster(self, cell, temp, direct_type):
        if len(temp) == 0:
            if cell.get_type() == CellType.MONSTER:
                return [cell]
            return []

        temp_ = temp[0]
        # log.debug('%s %s | %s %s' % (cell.index, cell.show(), temp_.index, temp_.show()))

        if temp_.get_type() == cell.get_type() == CellType.MONSTER and temp_.is_same(cell):
            temp.append(cell)
        elif cell.get_type() == CellType.MONSTER:
            self.add_monster(temp, direct_type)
            temp = [cell]
        else:
            self.add_monster(temp, direct_type)
            temp = []
        return temp

    def add_monster(self, temp, direct_type):
        if len(temp) == 0:
            return

        temp = sorted(temp, key=lambda a: a.order.value)

        indexes = []
        result = []
        state = None
        for i in range(len(temp)):
            indexes.append(temp[i].index)
            if i == 0:
                state = CellState(temp[i].ref_id, indexes, temp[i].order, direct_type)
                result.append(state)

            elif temp[i].order != temp[i - 1].order:
                state = CellState(temp[i].ref_id, indexes, temp[i].order, direct_type)
                result.append(state)
                indexes = []
            else:
                state.indexes = indexes

        if len(temp) <= 2:
            if direct_type not in self.probably_eliminate:
                self.probably_eliminate[direct_type] = [state]
            else:
                self.probably_eliminate[direct_type].append(state)
        if len(temp) > 2:
            if direct_type not in self.direct_states:
                self.direct_states[direct_type] = [state]
            else:
                self.direct_states[direct_type].append(state)

    def main_loop(self, loop, strategy_type):
        self.init_generate_grid()
        i = 0
        for i in range(loop):
            log.info('loop %s' % i)
            self.table_show()

            cells = self.swap_by_strategy(strategy_type)
            if len(cells) == 0:
                log.warning('can\'t find any swap plan')
                break
            log.info('best plan %s' % str(cells))

            self.swap_and_eliminate(cells)

        log.warning('complete loop: %s' % i)
        self.show()

    # 生成/掉落
    def generate_new(self, space_indexes):
        for index in space_indexes:
            monster = Monster(index, self.random_monster_ref(), min_order_type())
            # log.debug('generate %s' % monster)
            self.grid.__setitem__(index, monster)

    # 记录上场士兵
    def record_soldier(self, ref_id, order, target_level):
        if (ref_id, order, target_level - 1) in self.soldiers:
            self.soldiers[(ref_id, order, target_level - 1)].count += target_level
        else:
            soldier = Soldier(ref_id, order, target_level - 1, target_level)
            self.soldiers[(ref_id, order, target_level - 1)] = soldier

    # 交换和消除
    def swap_and_eliminate(self, cell_vo_tuple):
        if len(cell_vo_tuple) != 2:
            return
        self.swap_monster(cell_vo_tuple[0].index, cell_vo_tuple[1].index)

        while True:
            removes = self.synthesize_monster()
            if len(removes) == 0:
                break
            space_indexes = self.eliminate_monster(removes)

            self.table_show()
            # log.debug('space %s' % space_indexes)
            self.generate_new(space_indexes)

    # 合成
    def synthesize_monster(self) -> []:
        self.check_eliminate()
        temp = []
        for direct in self.direct_states:
            temp.extend(self.direct_states[direct])
        if len(temp) == 0:
            return []

        result = {}
        for state in temp:
            key = (state.ref_id, state.order)
            if key not in result:
                result[key] = state
            else:
                result[key].indexes.extend(state.indexes)

        final_index = []
        remove_indexes = None
        for (ref_id, order) in result:
            if order == OrderType.A:
                log.warning('up the top order %s %s' % (ref_id, result[(ref_id, order)]))
                continue

            value = result[(ref_id, order)]
            indexes = set(value.indexes)
            target_index, target_level = self.get_synthesize_index_level(indexes)

            log.debug('synthesize unit: %s %s %s target_index %s' % (ref_id, order, indexes, target_index))

            final_index.append(target_index)
            monster = Monster(target_index, ref_id, order.up(), level=target_level)
            self.grid[target_index] = monster

            self.record_soldier(ref_id, order, target_level)

            if remove_indexes is None:
                remove_indexes = indexes
            else:
                remove_indexes = indexes.union(remove_indexes)

        log.info('synthesize:%s remove:%s' % (final_index, remove_indexes))
        if remove_indexes is None:
            return []

        result = []
        for index in remove_indexes:
            if index not in final_index:
                result.append(index)
        log.debug('remove=%s' % result)
        return result

    def get_synthesize_index_level(self, indexes) -> (int, int):
        target_level = 0
        target_index = 0
        average = math.fsum(indexes) / len(indexes)
        temp = None
        for index in indexes:
            diff = math.fabs(index - average)
            if temp is None or temp > diff:
                target_index = index
                temp = diff

            monster = self.grid[index]
            target_level += monster.level
        target_level -= 2

        # log.debug('final_count=%s index=%s average=%s' % (target_level, target_index, average))

        return target_index, target_level

    # 消除和掉落 返回空缺的[index]
    def eliminate_monster(self, removes) -> []:
        if removes is None or len(removes) == 0:
            return []
        for index in removes:
            self.grid[index].ref_id = ' '

        space_indexes = []
        for x in range(self.col):
            stack = []
            for i in range(self.row):
                index = (self.row - i - 1) * self.col + x
                if index in removes:
                    # log.debug('space %s' % index)
                    stack.append(index)
                else:
                    if len(stack) == 0:
                        continue
                    target_remove = stack[0]
                    swap_result = self.swap_monster(index, target_remove)
                    if swap_result:
                        stack.pop(0)
                        stack.append(index)
                        # log.debug('swap and append %s %s stack%s' % (index, target_remove, stack))
            # log.info('current col space:%s' % stack)
            space_indexes.extend(stack)
        return space_indexes

    def swap_monster(self, one_index, other_index) -> bool:
        log.debug('swap %s %s' % (one_index, other_index))
        one = self.grid[one_index]
        other = self.grid[other_index]

        if one.get_type() != CellType.MONSTER or other.get_type() != CellType.MONSTER:
            return False

        if one.is_same(other):
            # log.warning('swap same %s<->%s' % (one, other))
            return False

        other.index = one_index
        one.index = other_index
        self.grid[one_index] = other
        self.grid[other_index] = one

        return True

    def swap_by_strategy(self, strategy_type) -> (CellVO, CellVO):
        """
        依据策略找出最佳方案
        :return: (CellVO, CellVO) 需要交换的两个 cell
        """
        # TODO 完善策略
        # log.setLevel(logging.DEBUG)

        if strategy_type == StrategyType.HIGH_ORDER_FIRST:
            return high_order_first.best_plan_to_swap(self)

        # log.setLevel(logging.INFO)

    def calculate_swap_effect(self, index_one, index_other) -> int:
        effect = 0
        swap_result = self.swap_monster(index_one, index_other)
        if not swap_result:
            log.debug('swap failed')
            return 0
        self.check_eliminate()
        for direct in self.direct_states:
            for state in self.direct_states[direct]:
                effect += state.order.value ** 3
                target_level = 0
                for index in state.indexes:
                    monster = self.grid[index]
                    target_level += monster.level
                effect += (target_level - 3) * (state.order.value - 1) ** 3
                log.debug('state %s effect=%s' % (state, effect))

        self.swap_monster(index_one, index_other)
        return effect

    def is_same_monster(self, index_one, index_other) -> bool:
        return self.grid[index_one].is_same(self.grid[index_other])

    def is_intersect(self, a, b) -> bool:
        cell_a = self.get_nearby_index_lists(a)
        cell_b = self.get_nearby_index_lists(b)
        # log.debug('%s %s | %s %s' % (cell_a, b.index, a.index, cell_b))

        temp = []
        for indexes in cell_a:
            temp.extend(indexes)
        if b.index in temp:
            return True

        temp = []
        for indexes in cell_b:
            temp.extend(indexes)
        if a.index in temp:
            return True
        return False

    # 根据 index 和 期望的ref_id 找出附近 最大的关联结构 [[index],[index]]
    def get_nearby_index_lists(self, target) -> [[], []]:
        current = target.index
        result = []

        for direct in self.probably_eliminate:
            state_list = self.probably_eliminate[direct]
            for cell in state_list:
                pre = cell.get_pre(self)
                next_ = cell.get_next(self)
                if pre == current or next_ == current:
                    result.append(cell.indexes)

        return result

    def get_completion_one(self, cell) -> Monster:
        """
        first find in outside , then find min count inside
        :param cell:
        return monster
        """
        index_lists = self.get_nearby_index_lists(cell)
        temp = []
        for indexes in index_lists:
            temp.extend(indexes)

        target = []
        for monster in self.grid:
            if monster.get_type() != CellType.MONSTER:
                continue
            if not monster.is_same(cell):
                continue

            if monster.index in temp:
                # log.debug('ignore %s' % monster)
                pass
            else:
                # log.debug('monster=%s' % monster)
                target.append(monster)
        if len(target) != 0:
            return random.choice(target)

    def get_simple_swap_choice(self) -> Monster:
        for direct in self.probably_eliminate:
            state_list = self.probably_eliminate[direct]
            for state in state_list:
                temp = []
                if len(state.indexes) > 1:
                    if state.get_pre(self) is not None:
                        temp.append(self.grid[state.get_pre(self)])
                    if state.get_next(self) is not None:
                        temp.append(self.grid[state.get_next(self)])
                for monster in temp:
                    if monster.get_type() == CellType.MONSTER:
                        return monster

    # 获取备选方案 按权重倒序排序
    def get_complex_swap_choice(self) -> [CellVO]:
        self.check_eliminate()

        result = []
        result.extend(self.cell_vo_by_successive())
        if len(result) > 1:
            result = sorted(result, key=lambda cell_vo: cell_vo.weight, reverse=True)
        return result

    # 分为 xo ox xx
    def cell_vo_by_successive(self) -> [CellVO]:
        vo_dict = {}  # id -> [(order,index)]
        for direct in self.probably_eliminate:
            state_list = self.probably_eliminate[direct]
            for cell in state_list:
                pre = cell.get_pre(self)
                next_ = cell.get_next(self)
                # log.debug('%s %s - %s' % (cell, pre, next_))

                if cell.ref_id not in vo_dict:
                    vo_dict[cell.ref_id] = []

                id_ = vo_dict[cell.ref_id]
                if pre is not None:
                    id_.append((cell.order, pre))
                if next_ is not None:
                    id_.append((cell.order, next_))

        result = []
        for ref_id in vo_dict:
            vo_tuple = vo_dict[ref_id]
            # log.debug('%s: %s' % (ref_id, str(vo_tuple)))
            result.extend(self.get_repeated_indexes(ref_id, vo_tuple))
        return result

    def get_repeated_indexes(self, ref_id, vo_tuple) -> [CellVO]:
        temp = {}  # ref_id_order->count
        result = []
        for order, index in vo_tuple:
            base = 1
            if index < 0:
                index *= -1
                base = 1 / 2

            key = (order, index)
            if key not in temp:
                temp[key] = base
            else:
                temp[key] = temp[key] + base

        for order, index in temp:
            key = (order, index)
            if temp[key] > 0.75 and self.grid[index].get_type() == CellType.MONSTER:
                cell = CellVO(ref_id, order, index, temp[key])
                result.append(cell)
        return result

    def show(self):
        log.setLevel(logging.INFO)
        self.table_show()
        self.show_detail()
        self.show_soldier()
        log.info('type count: %s' % self.type_count)

    def show_detail(self):
        for i in range(self.row):
            temp = ''
            for j in range(self.col):
                temp += "%8s" % (self.grid[i * self.col + j].show())
            log.info('%s' % temp)

    def table_show(self):
        log.info('┏' + '━┳' * (self.col - 1) + '━┓')
        for i in range(self.row):
            temp = '┃'
            for j in range(self.col):
                temp += "%s┃" % (self.grid[i * self.col + j].simple_show())
            log.info('%s' % temp)
            if i != self.row - 1:
                log.info('┣' + '━╋' * (self.col - 1) + '━┫')
        log.info("┗" + '━┻' * (self.col - 1) + "━┛")

    def simple_show(self):
        for i in range(self.row):
            temp = '|'
            for j in range(self.col):
                temp += "%2s" % (self.grid[i * self.col + j].simple_show())
            log.info('%s |' % temp)

    def show_soldier(self):
        result = []
        for (ref_id, order, level) in self.soldiers:
            result.append(self.soldiers[(ref_id, order, level)])
            # log.info('%s' % self.soldiers[(ref_id, order, level)])

        result = sorted(result, key=lambda soldiers: soldiers.order.value, reverse=True)
        count = 0
        for soldier in result:
            log.info('%s' % soldier)
            count += soldier.count
        log.info('count=%s' % count)
