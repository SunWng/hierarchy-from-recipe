import pandas as pd
import numpy as np

# read data
data = pd.read_csv('')

# subgoal class
class subgoal():
    def __init__(self, predicate, obj1, obj2=None):
        self.predicate = predicate
        self.object_1 = obj1
        self.object_2 = obj2
        self.level = 0
        self.dependency = []
        if predicate == 'on':
            self.object_list = [obj1, obj2]
        else:
            self.object_list = [obj1]
    
    def set_level(self, level_in):
        self.level = level_in
    
    def set_dependency(self, dependency_in):
        self.dependency = dependency_in
    
    def pddl_format(self):
        if self.object_2:
            return self.predicate + '(' + self.object_1 + ',' + self.object_2 + ')'
        elif not self.object_2:
            return self.predicate + '(' + self.object_1 + ')'

def main():
    ### extract subgoal and sequence ###
    task_index = data.iloc[:, 0].values

    last_index = task_index[-1]

    subgoal_sequence = []
    subgoal_pddl_sequence = []

    for i in range(1, last_index):
        current_task_index = np.where(task_index == i)[0]
        next_task_index = np.where(task_index == (i+1))[0]
        if i == 1:
            ingredient_list = data.iloc[current_task_index, [1]].values.reshape([len(current_task_index)]).tolist()
            for i in range(len(ingredient_list)):
                if ' ' in ingredient_list[i]:
                    ingredient_list[i] = ingredient_list[i].replace(' ', '_')
        
        current_state_matrix = data.iloc[current_task_index, 2:].values
        next_state_matrix = data.iloc[next_task_index, 2:].values
        
        diff_check = (next_state_matrix != current_state_matrix)
        diff_bool = np.where(diff_check)
        diff_row = diff_bool[0][0]
        diff_col = diff_bool[1][0]
        next_state = next_state_matrix.tolist()[diff_row][diff_col]
        current_state = current_state_matrix.tolist()[diff_row][diff_col]
        
        if diff_col == 0:
            if current_state in next_state:
                current_state = ', ' + current_state
                next_state = next_state.strip(current_state)
            current_subgoal = subgoal(next_state, ingredient_list[diff_row])
        elif diff_col == 1:
            next_state = next_state.replace(' ', '_')
            current_subgoal = subgoal('on', ingredient_list[diff_row], next_state)
        elif diff_col == 2:
            next_state = next_state.replace(' ', '_')
            current_subgoal = subgoal('in', ingredient_list[diff_row], next_state)
        elif diff_col == 3:
            next_state = next_state.replace(' ', '_')
            current_subgoal = subgoal('spread', ingredient_list[diff_row], next_state)
        subgoal_sequence.append(current_subgoal)
        subgoal_pddl_sequence.append(current_subgoal.pddl_format())
        
    ### check subgoal ###
    for i in range(len(subgoal_sequence)):
        print("[{i}]: {pddl}".format(i=i, pddl=subgoal_sequence[i].pddl_format()))
        
    ### search dependency and level ###
    recipe_heuristic = {}
    recipe_heuristic['tuna_spread'] = ['hot_sauce', 'onion', 'pepper', 'tuna']
    recipe_heuristic['sandwich'] = ['bread1', 'tuna_spread', 'arugula', 'bread2']

    reversed_subgoal_sequence = list(reversed(subgoal_sequence))
    reversed_subgoal_pddl_sequence = list(reversed(subgoal_pddl_sequence))
    sequence_length = len(subgoal_sequence)

    for i in range(sequence_length):
        if i == (sequence_length):
            offset = -subgoal_sequence[0].level +1
            for ii in subgoal_sequence:
                ii.level += offset
            break
        print(i, '\t', reversed_subgoal_sequence[i].pddl_format())
        dependent_subgoal_list = []
        
        if reversed_subgoal_sequence[i].predicate == 'exist':
            related_ingredient = recipe_heuristic[reversed_subgoal_sequence[i].object_1]
            
            for related_index in related_ingredient:
                for j in range(i+1, sequence_length):
                    related_check = related_index in reversed_subgoal_sequence[j].object_list
                    if related_check:
                        dependent_subgoal_list.append(reversed_subgoal_sequence[j])
                        reversed_subgoal_sequence[j].set_level(reversed_subgoal_sequence[i].level-1)
            reversed_subgoal_sequence[i].set_dependency(dependent_subgoal_list)
            
        else:
            for obj in reversed_subgoal_sequence[i].object_list:
                for search_index in range(i+1, sequence_length):
                    dependency_check = (obj in reversed_subgoal_sequence[search_index].object_list)
                    if dependency_check:
                        dependent_subgoal_list.append(reversed_subgoal_sequence[search_index])
                        reversed_subgoal_sequence[search_index].set_level(reversed_subgoal_sequence[i].level-1)
                        break
            
            reversed_subgoal_sequence[i].set_dependency(dependent_subgoal_list)
            
    ### check output ###
    for subgoal_ in subgoal_sequence:
        print("[Level {level}] {pddl} \n \t Dependency:".format(level=subgoal_.level, pddl=subgoal_.pddl_format()))
        for dep_subgoal in subgoal_.dependency:
            print('\t\t', dep_subgoal.pddl_format())
    