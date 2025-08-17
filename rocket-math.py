#!/usr/bin/python

# written by Chris and Olivia Irwin, 2025
# TODO: 
#       implement a personalized mode to ask questions answered incorrectly, or ones where the time taken was long 

from random import random
from math import floor
from pathlib import Path
import time
import datetime
import curses
import csv 
import sys 
import argparse
import os

test = 4 / 0

parser = argparse.ArgumentParser(prog='rocket-math.py')
parser.add_argument('-s','--seconds',action='store_true', help='fixed seconds mode')
parser.add_argument('operation', help='operation (a,s,m,d)', nargs='?', default='m')
parser.add_argument('number', help='number of questions/seconds', nargs='?', default='50')
args = parser.parse_args()

file_path = Path.home() / 'Documents' / 'rocket-math.csv'

#problem space here is defined by types of questions in "Rocket Math" homework 
def new_question(operation):
    x = dict()
    if operation == 's':
        #make numbers such that x['num1']-x['num2']=x['answer']
        x['operation'] = '-'
        x['num2'] = floor(random()*9)+1
        x['answer'] = floor(random()*9)+1
        x['num1'] = x['num2'] + x['answer']
    elif operation == 'a':
        #make numbers such that x['num1']+x['num2']=x['answer']
        x['operation'] = '+'
        x['num1'] = floor(random()*9)+1
        x['num2'] = floor(random()*9)+1
        x['answer'] = x['num1'] + x['num2']
    elif operation == 'm':
        x['operation'] = 'x'
        x['num1'] = floor(random()*8)+2
        x['num2'] = floor(random()*8)+2
        x['answer'] = x['num1'] * x['num2']
    elif operation =='d':
        x['operation'] = '÷'
        x['num2'] = floor(random()*8)+2
        x['answer'] = floor(random()*8)+2
        x['num1'] = x['num2'] * x['answer']
    else:
        sys.exit()
    return x

def win_print(win, msg, color):
    win.clear()
    win.addstr(0,0,msg,curses.color_pair(color))
    win.refresh()

def do_it(stdscr):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    stdscr.bkgd(' ', curses.color_pair(2))
    stdscr.refresh()
    curses.echo()
    max_line, max_col = curses.LINES-1, curses.COLS-1
    w_title_bar = curses.newwin(1,max_col,0,0) #height, width, starty, startx
    w_title_bar.bkgd(' ', curses.color_pair(1))
    w_mode = curses.newwin(1,max_col,1,0)
    w_mode.bkgd(' ', curses.color_pair(3))
    w_question = curses.newwin(3,max_col,3,0)
    w_question.bkgd(' ', curses.color_pair(2))
    w_answer = curses.newwin(1,max_col,6,0)
    w_answer.bkgd(' ', curses.color_pair(3))
    w_feedback = curses.newwin(1,max_col,max_line-2,0)
    w_feedback.bkgd(' ', curses.color_pair(1))
    w_summary = curses.newwin(1,max_col,max_line-1,0)
    w_summary.bkgd(' ', curses.color_pair(1))
    w_hints = curses.newwin(1,max_col,max_line,0)
    w_hints.bkgd(' ', curses.color_pair(1))

    win_print(w_title_bar, "Rocket Math by Chris Irwin and Olivia Irwin, 2025", 1)
    mode = 's' if args.seconds else 'q'
    if mode == 'q':
        win_print(w_mode, "Question Mode Engaged", 3)
    elif mode == 's':
        win_print(w_mode, "Seconds Mode Engaged", 3)
        
    op_code = args.operation

    q_limit,s_limit=-1,-1
    if mode == 'q':
        q_limit = int(args.number)
    elif mode == 's':
        s_limit = int(args.number) 
        
    win_print(w_hints, "a,s,m,d to change operation, p to pause, q to quit", 1)
    win_print(w_answer,"",2)
    questions_answered=0
    seconds_passed=0
    if not os.path.exists(file_path):
        with open(file_path,'w') as f:
            fieldnames = ["time","seconds","num1","op","num2","answer","correct"]
            writer = csv.writer(f)    
            writer.writerow(fieldnames)
    with open(file_path,'a') as f:
        writer = csv.writer(f)    
        score = 0
        #countdown
        for i in range(3,0,-1):
            win_print(w_question, "Countdown!\n{}...".format(i), 2)
            time.sleep(1)
        while seconds_passed < s_limit or questions_answered < q_limit:  
            x = new_question(op_code)
            win_print(w_question, "Question {}\n{} {} {} =".format(questions_answered+1,x['num1'],x['operation'],x['num2']), 2)
            s_time = time.time()
            answer_is_valid = False
            while not answer_is_valid:
                #getstr returns bytes, which decode() turns into a string
                user_input = w_answer.getstr(0,0).decode().lower()
                w_answer.clear()
                w_answer.refresh()
                if user_input == "q":
                    sys.exit()
                elif user_input in ["a","s","m","d"]:
                    op_code = user_input
                    break
                elif user_input == "p":
                    win_print(w_question, "Timer is paused.  Press any key to continue...", 2)
                    w_answer.getch(0,0)
                    w_answer.clear()
                    w_answer.refresh()
                    break
                try:
                    user_input_int = int(user_input)
                    answer_is_valid = True
                except ValueError: #shouldn't mark a question wrong because the user mistyped
                    win_print(w_feedback, "Oops, that doesn't look like a number", 1)
                    continue

            if answer_is_valid: # needed for commands like p/a/s/m/d that break the above loop
                e_time = time.time()
                seconds_passed = seconds_passed + e_time - s_time
                questions_answered = questions_answered + 1
                seconds = round(e_time-s_time,1)
                if (user_input_int == x['answer'] ):
                    score += 1
                    win_print(w_feedback,"Answered correctly in {} seconds".format(seconds), 1)
                    writer.writerow([datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S'),seconds,x['num1'],x['operation'],x['num2'],user_input,'Y'])
                else:
                    win_print(w_feedback,"Opps!  {} seconds".format(seconds), 1)
                    writer.writerow([datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S'),seconds,x['num1'],x['operation'],x['num2'],user_input,'N'])
                win_print(w_summary, "You got {} right out of {}/{} questions! {}% in {} seconds".format(score,questions_answered,q_limit,int(score/(questions_answered)*100), round(seconds_passed,1)), 1)
    w_hints.clear()
    w_hints.refresh()
    win_print(w_question, "Press any key to quit... ", 2)
    w_answer.getch()

if __name__ == '__main__':
    curses.wrapper(do_it)

