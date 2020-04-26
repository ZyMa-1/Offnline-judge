from datetime import datetime
import multiprocessing
import subprocess
import os
from time import sleep


def test_solution(solution_id, problem_id, results):
    solution_path = f'data/testing_system/solutions/{solution_id}'
    problem_path = f'data/problems/{problem_id}/tests'

    def delete_temp_files():
        os.remove(f'{solution_path}/solution.exe')
        os.remove(f'{solution_path}/input.txt')
        os.remove(f'{solution_path}/output.txt')

    os.rename(f'{solution_path}/{os.listdir(solution_path)[0]}', f'{solution_path}/solution.cpp')
    process = os.system(
        f"g++ -static -fno-strict-aliasing -DACMP -lm -s -x c++ -std=c++14 -Wl,--stack=67108864 -O2 -o {solution_path}/solution.exe {solution_path}/solution.cpp")

    if process != 0:
        results[solution_id] = "CE"
        return
    test_num = 1
    for filename in os.listdir(f'{problem_path}/input'):

        input = open(f'{problem_path}/input/{filename}', 'r').read()
        output = open(f'{problem_path}/output/{filename}', 'r').read()

        open(f'{solution_path}/input.txt', 'w').write(input)
        subprocess.Popen(f"{solution_path}/solution.exe", stdin=open(f"{solution_path}/input.txt", "r"),
                         stdout=open(f"{solution_path}/output.txt", "w"))
        sleep(.1)
        if open(f"{solution_path}/output.txt", "r").read() != output:
            delete_temp_files()
            results[solution_id] = f"WA {test_num}"
            return
        test_num += 1
    delete_temp_files()
    results[solution_id] = "AC"
    return


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    results = manager.dict()
    start = datetime.now()
    processes = []
    for i in range(1, 4):
        p = multiprocessing.Process(target=test_solution, args=[i, 1, results])
        processes.append(p)
        p.start()
    for process in processes:
        process.join()
    print(datetime.now() - start)
    print(results)
