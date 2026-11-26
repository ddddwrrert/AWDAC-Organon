def lookup(memory, source, condition):
    return memory.get_evaluation(source, condition)

def store(memory, source, condition, result):
    memory.save_evaluation(source, condition, result)
