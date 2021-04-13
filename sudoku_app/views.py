from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .helper import generateSudoku, getLockedPositions, getErrors, fillCurrentBoard, addHint, getPuzzleStats, getLeaderboard
from sudoku_app.models import SudokuGame, SudokuRecord
import json

# Create your views here.

# display all of the current user's puzzles
@login_required
def puzzles(request):
    # retrieve list of puzzles belonging to this current user from the table
    puzzle_list = list(SudokuGame.objects.filter(user=request.user))
    return render(request, 'sudoku_app/puzzles.html', {'puzzles': puzzle_list})

# display the requested puzzle
@login_required
def puzzle(request, puzzle_id):
    # retrieve requested puzzle and ensure that it belongs to current user
    puzzle = get_object_or_404(SudokuGame, pk=puzzle_id)
    if puzzle.user != request.user:
        return HttpResponseRedirect('/puzzles')
    # ensure that the solve has been recorded for leaderboard purposes
    if puzzle.is_solved():
        SudokuRecord.objects.get_or_create(puzzle_id=puzzle_id, defaults={'difficulty': puzzle.difficulty, 'user': puzzle.user})
    # load puzzle data into iterable format
    initial_board_array, current_board_array, solution_board_array = json.loads(puzzle.initial_board), json.loads(puzzle.current_board), json.loads(puzzle.solution_board)
    # send relevant data to view 
    # (locked positions indicates what numbers were initially in the puzzle and can't be modified)
    return render(request, 'sudoku_app/puzzle.html', {'puzzle': current_board_array, 'solution': solution_board_array, 'solved': puzzle.is_solved(), 'locked_positions': getLockedPositions(initial_board_array), 'puzzle_id': puzzle_id, 'difficulty': puzzle.difficulty})

# create a puzzle for current user of given difficulty
@login_required
def create_puzzle(request, difficulty='easy'):
    # create puzzle and corresponding solution from API
    puzzle_data = generateSudoku(difficulty)
    # serialize puzzle to store in database
    initial_board_string, solution_board_string = json.dumps(puzzle_data['puzzle']), json.dumps(puzzle_data['solution'])
    # create instance of puzzle in database
    sudoku_game = SudokuGame(initial_board=initial_board_string, current_board=initial_board_string, solution_board=solution_board_string, difficulty=difficulty, user=request.user)
    sudoku_game.save()
    # display the puzzle that has just been created
    return HttpResponseRedirect(f'/puzzles/{sudoku_game.id}')

# save current state of puzzle to database 
@login_required
def save_puzzle(request, puzzle_id):
    # retrieve requested puzzle and ensure that it belongs to current user
    puzzle = get_object_or_404(SudokuGame, pk=puzzle_id)
    if puzzle.user != request.user:
        return HttpResponseRedirect('/puzzles')
    # populate current board given data sent from view (note: no data sent if puzzle has been solved already) and save in db
    initial_board_array = json.loads(puzzle.initial_board)
    current_board_array = fillCurrentBoard(initial_board_array, request.POST) if not puzzle.is_solved() else json.loads(puzzle.current_board)
    puzzle.current_board = json.dumps(current_board_array)
    puzzle.save()
    # display requested puzzle
    return HttpResponseRedirect(f'/puzzles/{puzzle_id}')

# check if current state of puzzle has any mistakes according to solution
@login_required
def check_puzzle(request, puzzle_id):
    # retrieve requested puzzle and ensure that it belongs to current user
    puzzle = get_object_or_404(SudokuGame, pk=puzzle_id)
    if puzzle.user != request.user:
        return HttpResponseRedirect('/puzzles')
    # populate current board given data sent from view (note: no data sent if puzzle has been solved already) and save in db
    initial_board_array, solution_board_array = json.loads(puzzle.initial_board), json.loads(puzzle.solution_board)
    current_board_array = fillCurrentBoard(initial_board_array, request.POST) if not puzzle.is_solved() else json.loads(puzzle.current_board)
    puzzle.current_board = json.dumps(current_board_array)
    puzzle.save()   
    # ensure that the solve has been recorded for leaderboard purposes
    if puzzle.is_solved():
        SudokuRecord.objects.get_or_create(puzzle_id=puzzle_id, defaults={'difficulty': puzzle.difficulty, 'user': puzzle.user})
    # send relevant data to view 
    # (locked positions indicates what numbers were initially in the puzzle and can't be modified) 
    # (errors are calculated based on discrepencies between current and solution board)
    return render(request, 'sudoku_app/puzzle.html', {'puzzle': current_board_array, 'solution': solution_board_array, 'solved': puzzle.is_solved(), 'locked_positions': getLockedPositions(initial_board_array), 'errors': getErrors(current_board_array, solution_board_array), 'puzzle_id': puzzle_id, 'difficulty': puzzle.difficulty})

# add one number to current puzzle
@login_required
def add_hint(request, puzzle_id):
    # retrieve requested puzzle and ensure that it belongs to current user
    puzzle = get_object_or_404(SudokuGame, pk=puzzle_id)
    if puzzle.user != request.user:
        return HttpResponseRedirect('/puzzles')
    # populate current board given data sent from view (note: no data sent if puzzle has been solved already) and save in db
    initial_board_array, solution_board_array = json.loads(puzzle.initial_board), json.loads(puzzle.solution_board)
    current_board_array = addHint(fillCurrentBoard(initial_board_array, request.POST), solution_board_array) if not puzzle.is_solved() else json.loads(puzzle.current_board)
    puzzle.current_board = json.dumps(current_board_array)
    puzzle.save()
    # display requested puzzle
    return HttpResponseRedirect(f'/puzzles/{puzzle_id}')

# delete current puzzle
@login_required
def delete_puzzle(request, puzzle_id):
    # retrieve requested puzzle and ensure that it belongs to current user
    puzzle = get_object_or_404(SudokuGame, pk=puzzle_id)
    if puzzle.user != request.user:
        return HttpResponseRedirect('/puzzles')
    # delete puzzle and redirect to home page
    puzzle.delete()
    return HttpResponseRedirect('/puzzles')

# reset current puzzle to initial board
@login_required
def reset_puzzle(request, puzzle_id):
    # retrieve requested puzzle and ensure that it belongs to current user
    puzzle = get_object_or_404(SudokuGame, pk=puzzle_id)
    if puzzle.user != request.user:
        return HttpResponseRedirect('/puzzles')
    # reset puzzle to initial state
    if not puzzle.is_solved():
        puzzle.current_board = puzzle.initial_board
    puzzle.save()
    # display requested puzzle
    return HttpResponseRedirect(f'/puzzles/{puzzle_id}')

# create user that solve/save puzzles and view statistics
def create_user(request):
    # GET request indicates page needs to be displayed, POST indicates that user is being created
    if request.method == 'GET':
        return render(request, 'sudoku_app/createuser.html', {})
    else:
        # create user using data sent from form and redirect to login page
        email, username, password = request.POST['email'], request.POST['username'], request.POST['password']
        User.objects.create_user(username, email, password)
        return HttpResponseRedirect('/accounts/login')

# display number of puzzles that current user has solved
@login_required
def display_stats(request):
    return render(request, 'sudoku_app/statistics.html', getPuzzleStats(request))

# display how many puzzles each registered user has solved
@login_required
def display_leaderboard(request):
    return render(request, 'sudoku_app/leaderboard.html', {"scores": getLeaderboard(request)})




