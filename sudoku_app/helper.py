import requests
from django.contrib.auth.models import User
from sudoku_app.models import SudokuRecord
from django.db import connection
from urllib.parse import quote
import re

# credit to https://github.com/bertoort/sugoku for sudoku api
# retrieve sudoku puzzle and solution
def generateSudoku(difficulty='easy'):
    sudoku_board = requests.get(f'https://sugoku.herokuapp.com/board?difficulty={difficulty}').json()
    encoded_board = encodeParams(sudoku_board)
    solution_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    sudoku_solution = requests.post('https://sugoku.herokuapp.com/solve', data=encoded_board, headers=solution_headers).json()
    return {'puzzle': sudoku_board['board'], 'solution': sudoku_solution['solution']}

# see https://github.com/bertoort/sugoku
def encodeBoard(board): 
    result = ''
    for count, row in enumerate(board):
        end = '' if count == len(board) - 1 else '%2C'
        string_row = ','.join(map(lambda num: str(num), row))
        encodedRow = f'%5B{quote(string_row)}%5D{end}'
        result = result + encodedRow
    return result

# see https://github.com/bertoort/sugoku
def encodeParams(params):
    return '&'.join(map(lambda key : key + '=' + f'%5B{encodeBoard(params[key])}%5D', params.keys()))

# create array of booleans indicating if given position in sudoku board should be immutable
def getLockedPositions(initial_board_array):
    return [[col != 0 for col in row] for row in initial_board_array]

# create array of booleans indicating if given position in sudoku board matches solution
def getErrors(current_board_array, solution_board_array):
    return [[current_board_array[i][j] != solution_board_array[i][j] for j in range(0,9)] for i in range(0,9)]

# creates representation of sudoku board based on positions sent by view and positions locked in initially
def fillCurrentBoard(initial_board_array, post_request_data):
    # reg-ex that detects and ignores invalid inputs
    pattern = re.compile('[0-9]')
    current_board_array = []
    for i in range(0,9):
        current_board_array.append([])
        for j in range(0,9):
            # format of coordinate sent by view
            key = f'({i},{j})'
            # if the view did not sent a value for this coordinate, then it was in the initial puzzle
            if key not in post_request_data:
                val = initial_board_array[i][j]
            # just coerce invalid inputs into blanks, represented by 0s
            elif post_request_data[key] == '' or not pattern.fullmatch(post_request_data[key]):
                val = 0
            # this indicates valid input and is put into current version of puzzle
            else:
                val = int(post_request_data[key])
            current_board_array[i].append(val)
    return current_board_array

# fills in the first blank with answer from solution board
def addHint(current_board_array, solution_board_array):
    for i in range(0,9):
        for j in range(0,9):
            if current_board_array[i][j] == 0:
                current_board_array[i][j] = solution_board_array[i][j]
                return current_board_array

# query that retrieves number of puzzles solved for each difficulty from db
def getPuzzleStats(request):
    with connection.cursor() as c:
        sudoku_record_table_name = SudokuRecord.objects.model._meta.db_table
        user_table_name = User.objects.model._meta.db_table
        query = f"SELECT difficulty, COUNT(difficulty) as total FROM {sudoku_record_table_name} INNER JOIN {user_table_name} ON {sudoku_record_table_name}.user_id = {user_table_name}.id WHERE username='{request.user.username}' GROUP BY difficulty"
        c.execute(query)
        results = dict(c.fetchall())
        return results

# query that retrieves number of puzzles each person has solved from db
def getLeaderboard(request):
    with connection.cursor() as c:
        sudoku_record_table_name = SudokuRecord.objects.model._meta.db_table
        user_table_name = User.objects.model._meta.db_table
        query = f"SELECT username, COUNT(difficulty) as total FROM {sudoku_record_table_name} INNER JOIN {user_table_name} ON {sudoku_record_table_name}.user_id = {user_table_name}.id GROUP BY username ORDER BY total DESC;"
        c.execute(query)
        results = dict(c.fetchall())
        return results





