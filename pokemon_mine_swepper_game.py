#author: YI DING
#email: dydifferent@gmail.com
#The University of Queensland
#May 2020

import random,os,sys,time
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

TASK_ONE = 'TASK_ONE'
TASK_TWO = 'TASK_TWO'
square_size = 60
UNEXPOSED = "~"
POKEMON = "☺"
FLAG = "♥"
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
DIRECTIONS = (UP, DOWN, LEFT, RIGHT,
              f"{UP}-{LEFT}", f"{UP}-{RIGHT}",
              f"{DOWN}-{LEFT}", f"{DOWN}-{RIGHT}")


class BoardModel:
    '''
    Store and manage the internal game state.
    '''
    def __init__(self, grid_size, num_pokemon):
        """
        Construct a covered or uncovered board

        parameters:
            grid_size (int):The grid size of the game.
            num_pokemon (int): The number of pokemons that the game will have.
        """
        self._grid_size = grid_size
        self._num_pokemon = num_pokemon
        self._board = UNEXPOSED*(self._grid_size ** 2) 
        self._pokemon_locations = ()
        self._attempted_catches_num = 0
        self.generate_pokemons(grid_size, num_pokemon)

    def get_game(self): 
        '''
        Returns an appropriate representation of the current state of the game board.
        '''
        return self._board

    def generate_pokemons(self, grid_size, num_pokemon):
        """Pokemons will be generated and given a random index within the game.

        Parameters:
            grid_size (int): The grid size of the game.
            num_pokemon (int): The number of pokemons that the game will have.

        Returns:
            (tuple<int>): A tuple containing  indexes where the pokemons are
            created for the game string.
        """
        square_count = self._grid_size ** 2 
        for i in range(self._num_pokemon):
            if len(self._pokemon_locations) >= square_count:
                break
            index = random.randint(0, square_count-1)
            while index in self._pokemon_locations:
                index = random.randint(0, square_count-1)
            self._pokemon_locations += (index,)

    def get_pokemon_locations(self):
        '''
        Returns the indices describing all pokemon locations.
        '''
        return self._pokemon_locations

    def get_num_attempted_catches(self):
        '''
        Returns the number of pokeballs currently placed on the board.
        '''
        return self._attempted_catches_num 


    def get_num_pokeball_leave(self):
        '''
        Return the number of left pokeballs
        '''
        self._leave_ball = self._num_pokemon - self.get_num_attempted_catches()
        if self._leave_ball < 0:
            return 0 
        else:
            return self._leave_ball
        
    def get_num_pokemon(self):
        '''
        Returns the number of pokemon hidden in the game.
        '''
        return self._num_pokemon

    def position_to_index(self, position, grid_size):
        """
        Convert the row, column coordinate in the grid to the game strings index.

        Parameters:
            position (tuple<int, int>): The row, column position of a cell.
            grid_size (int): The grid size of the game.

        Returns:
            (int): The index of the cell in the game string.
        """
        x, y = position
        return x + y * self._grid_size 

    def flag_cell(self, index):
        """
        Toggle Flag on or off at selected index. If the selected index is already
        revealed, the game would return with no changes.

            Parameters:
                index (int): The index in the game string where a flag is placed.
            Returns
                (str): The updated game string.
        """
        if self._board[index] == FLAG:
            self._board = self.replace_character_at_index(index, UNEXPOSED)
            self._attempted_catches_num -= 1

        elif self._board[index] == UNEXPOSED:
            if self.get_num_pokeball_leave() == 0:
                return None
            else:
                self._board = self.replace_character_at_index(index, FLAG)
                self._attempted_catches_num += 1

        return self._board

    def replace_character_at_index(self, index, character):
        """
        A specified index in the game string at the specified index is replaced by
        a new character.
        Parameters:
            index (int): The index in the game string where the character is replaced.
            character (str): The new character that will be replacing the old character.

        Returns:
            (str): The updated game string.
        """
        self._board = self._board[:index] + character + self._board[index + 1:]
        return self._board

    def index_in_direction(self, index, grid_size, direction):
        """
        The index in the game string is updated by determining the
        adjacent cell given the direction.
        The index of the adjacent cell in the game is then calculated and returned.

        The index of m is 4 in the game string.
        if the direction specified is "up" then:
        the updated position corresponds with j which has the index of 1 in the game string.

        Parameters:
            index (int): The index in the game string.
            grid_size (int): The grid size of the game.
            direction (str): The direction of the adjacent cell.

        Returns:
            (int): The index in the game string corresponding to the new cell position
            in the game.

            None for invalid direction.
        """
        row = index % self._grid_size
        col = index // self._grid_size
        if RIGHT in direction:
            col += 1
        elif LEFT in direction:
            col -= 1
        if UP in direction:
            row -= 1
        elif DOWN in direction:
            row += 1
        if not (0 <= col < self._grid_size and 0 <= row < self._grid_size):
            return None
        return self.position_to_index((row, col), self._grid_size)

    def neighbour_directions(self, index, grid_size):
        """
        Seek out all direction that has a neighbouring cell.

        Parameters:
            index (int): The index in the game string.
            grid_size (int): The grid size of the game.

        Returns:
            (list<int>): A list of index that has a neighbouring cell.
        """
        neighbours = []
        for direction in DIRECTIONS:
            neighbour = self.index_in_direction(index, grid_size, direction)
            if neighbour is not None:
                neighbours.append(neighbour)
        return neighbours

    def number_at_cell(self, pokemon_locations, grid_size, index):
        """
        Calculates what number should be displayed at that specific index in the game.

        Parameters:
            pokemon_locations (tuple<int, ...>): Tuple of all Pokemon's locations.
            grid_size (int): Size of game.
            index (int): Index of the currently selected cell

        Returns:
            (int): Number to be displayed at the given index in the game string.
        """
        if self._board[index] != UNEXPOSED:
            return int(self._board[index])
        number = 0
        for neighbour in self.neighbour_directions(index, grid_size):
            if neighbour in pokemon_locations:
                number += 1
        return number

    def big_fun_search(self, grid_size, pokemon_locations, index):
        """
        Searching adjacent cells to see if there are any Pokemon"s present.

        Using some sick algorithms.

        Find all cells which should be revealed when a cell is selected.

        For cells which have a zero value (i.e. no neighbouring pokemons) all the cell"s
        neighbours are revealed. If one of the neighbouring cells is also zero then
        all of that cell"s neighbours are also revealed. This repeats until no
        zero value neighbours exist.

        For cells which have a non-zero value (i.e. cells with neighbour pokemons), only
        the cell itself is revealed.

        Parameters:
            grid_size (int): Size of game.
            pokemon_locations (tuple<int, ...>): Tuple of all Pokemon's locations.
            index (int): Index of the currently selected cell

        Returns:
            (list<int>): List of cells to turn visible.
        """
        queue = [index]
        discovered = [index]
        visible = []
        if self._board[index] == FLAG:
            return queue
        number = self.number_at_cell(pokemon_locations, grid_size, index)
        if number != 0:
            return queue
        while queue:
            node = queue.pop()
            for neighbour in self.neighbour_directions(node, grid_size):
                if neighbour in discovered:
                    continue
                discovered.append(neighbour)
                if self._board[neighbour] != FLAG:
                    number = self.number_at_cell(pokemon_locations, grid_size, neighbour)
                    if number == 0:
                        queue.append(neighbour)
                visible.append(neighbour)
        return visible

    def reveal_cells(self, grid_size, pokemon_locations, index):
        """
        Reveals all neighbouring square boards at index and repeats for all
        square boards that had a 0.

        Parameters:
            pokemon_locations (tuple<int, ...>): Tuple of all Pokemon's locations.
            grid_size (int): Size of game.
            index (int): Index of the currently selected cell.

        Returns:
            (str): The updated game string.
        """
        number = self.number_at_cell(pokemon_locations, grid_size, index)
        self._board = self.replace_character_at_index(index, str(number))
        clear = self.big_fun_search(grid_size, pokemon_locations, index)
        for i in clear:
            if self._board[i] != FLAG:
                number = self.number_at_cell(pokemon_locations, grid_size, i)
                self._board = self.replace_character_at_index(i, str(number))
        return self._board


class BoardView(tk.Canvas):
    '''
    View the pokemon game board
    '''
    def __init__(self, master, grid_size, Model, pokemongame, board_width=600, *args, **kwargs):
        '''
        Construct a board view from a board layout.

        Parameters:
            master (tk.Widget): Widget within which the board is placed.
            grid_size (int): Size of game.
            Model(class): BoardModel class.
            pokemongame(class):PokemonGame class.
            board_width(int):the width of the board.
        '''
        super().__init__(master, *args, **kwargs)
        self._master = master
        self._grid_size = grid_size
        self._board_width = board_width
        self._BoardModel = Model
        self._pokemongame = pokemongame
        self._now_position = None
        self._move_image = []
        
    def draw_board(self, board):
        '''
        Given an appropriate representation of the current state of the game board, 
        draw the view to reflect this game state.

        Parameters:
            board(string):The board game string.
        '''
        # clear the entire board before drawing the game again.
        self.delete(tk.ALL)
        #draw square board
        for i in range(self._grid_size):
            for j in range(self._grid_size):
                char = board[self._BoardModel.position_to_index((i, j), self._grid_size)]
                x1, y1 = i * square_size, j * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                center_pixel = self.position_to_pixel((i,j))
                if char == UNEXPOSED:
                    self.create_rectangle(x1, y1, x2 , y2, fill='#054a29')                   
                elif char == FLAG:
                    self.create_rectangle(x1, y1, x2 , y2, fill='#e6071d')
                elif char == POKEMON:
                    self.create_rectangle(x1, y1, x2 , y2, fill='#f5e90a')
                else:
                    self.create_rectangle(x1, y1, x2 , y2, fill='#0fd174')
                    self.create_text(center_pixel[0], center_pixel[1],text= char)
        self.bind_clicks()   
        self.config(width = self._board_width, height = self._board_width)

    def bind_clicks(self):
        """
        Bind clicks on a label to the left and right click handlers.
        """
        # bind left click
        self.bind('<Button-1>', lambda e: self.left_click((e.x, e.y)))
        # bind right click MAC
        self.bind('<Button-2>', lambda e: self.right_click((e.x, e.y)))
        # bind right click WINDOWS
        self.bind('<Button-3>', lambda e: self.right_click((e.x, e.y)))
        self.bind('<Motion>', lambda e: self.highlight((e.x, e.y)))

    def left_click(self, pixel):
        '''
        Handle left clicking on a square board.

        Parameters:
            pixel(tuple):The grafic coordinate.
        '''
        position = self.pixel_to_position(pixel)
        index = self._BoardModel.position_to_index(position, self._grid_size)
        pokemon_locations = self._BoardModel.get_pokemon_locations()          
        if index in self._BoardModel.get_pokemon_locations():
             for index in self._BoardModel.get_pokemon_locations():
                self._BoardModel.replace_character_at_index(index, POKEMON)
                self._master.update()
        else:
            self._BoardModel.reveal_cells(self._grid_size, pokemon_locations, index)
        self.draw_board(self._BoardModel.get_game())
        self._master.update()
        self._pokemongame.check_game_over(position)
        
    def right_click(self, pixel):
        """
        Handle right clicking on a square board.

        Parameters:
            pixel(tuple):The grafic coordinate.
        """
        position = self.pixel_to_position(pixel)
        index = self._BoardModel.position_to_index(position, self._grid_size)
        self._BoardModel.flag_cell(index)
        self.draw_board(self._BoardModel.get_game())
        self._master.update()
        self._pokemongame.check_game_over(position)

    def highlight(self,pixel):
        '''
        Handel the highlight with the cursor moving

        Parameters:
            pixel(tuple):The grafic coordinate.
        '''
        if pixel[0] in range(self._grid_size * square_size):
            if pixel[1] in range(self._grid_size * square_size):
                position = self.pixel_to_position(pixel)
                index = self._BoardModel.position_to_index(position, self._grid_size)
                if self._pokemongame._task == TASK_ONE:
                    x1, y1 = position[0] * square_size, position[1] * square_size
                    x2, y2 = x1 + square_size, y1 + square_size
                    self.create_rectangle(x1, y1, x2, y2, outline = '#34b1eb')
                    if self._now_position != position: 
                        if self._now_position:
                            self.create_rectangle(self._now_position[0] * square_size,
                                                self._now_position[1] * square_size,
                                                self._now_position[0] * square_size + square_size,
                                                self._now_position[1] * square_size + square_size,
                                                outline = None)
                        self._now_position = position
                elif self._pokemongame._task == TASK_TWO:
                    image_1 = get_image('images/unrevealed')
                    self._move_image.append(image_1)
                    image_2 = get_image('images/unrevealed_moved')
                    self._move_image.append(image_2)
                    if self._BoardModel.get_game()[index] == UNEXPOSED:
                        x1, y1 = position[0] * square_size, position[1] * square_size
                        self.create_image(x1 + square_size/2, y1 + square_size/2, image = image_2)
                    if self._now_position != position:
                        if self._now_position:
                            now_index = self._BoardModel.position_to_index(self._now_position, self._grid_size)
                            if self._BoardModel.get_game()[now_index] == UNEXPOSED:
                                self.create_image((self._now_position[0] * square_size) + square_size/2,
                                                (self._now_position[1] * square_size) + square_size/2,
                                                image = image_1)
                        self._now_position = position

            
    def pixel_to_position(self, pixel): 
        '''
        Converts the supplied pixel to the position of the cell it is contained within.

        Parameters:
            pixel(tuple):The grafic coordinate.
        '''
        x, y = pixel[0], pixel[1]
        position = (x // square_size, y // square_size)
        return position 

    def position_to_pixel(self, position): 
        '''
        Converts position to the center postion of each square.

        Parameters:
            position:The position of each sqaure.

        Returns the center pixel for the cell at position.
        '''
        return (position[0] * square_size + square_size/2, position[1] * square_size +square_size/2)

class ImageBoardView(BoardView):
    '''
    View the pokemon game board with pictures.
    '''
    def draw_board(self,board):
        '''
        Given an appropriate representation of the current state of the game board, 
        draw the view to reflect this game state.

        Parameters:
            board(string):The board game string.
        '''
        self._image = []
        self.delete(tk.ALL)
        for i in range(self._grid_size):
            for j in range(self._grid_size):
                char = board[self._BoardModel.position_to_index((i, j), self._grid_size)]
                x1, y1 = i * square_size, j * square_size
                if char == UNEXPOSED:
                    image = get_image("images/unrevealed")
                    self.create_image(x1 + square_size/2, y1 + square_size/2, image = image)
                    self._image.append(image)
                elif char == FLAG:
                    image = get_image("images/pokeball")
                    self.create_image(x1 + square_size/2, y1 + square_size/2, image = image)
                    self._image.append(image)
                elif char == POKEMON:
                    pokemon_choose = {0:"images/pokemon_sprites/pikachu",
                                      1:"images/pokemon_sprites/charizard",
                                      2:"images/pokemon_sprites/cyndaquil",
                                      3:"images/pokemon_sprites/psyduck",
                                      4:"images/pokemon_sprites/togepi",
                                      5:"images/pokemon_sprites/umbreon",}
                    pokemon_random_index = random.randint(0,5)
                    image = get_image(pokemon_choose[pokemon_random_index])
                    self.create_image(x1+ square_size/2, y1 + square_size/2, image = image)
                    self._image.append(image)
                else:
                    num_adjacent = {0:"images/zero_adjacent",
                                    1:"images/one_adjacent",
                                    2:"images/two_adjacent",
                                    3:"images/three_adjacent",
                                    4:"images/four_adjacent",
                                    5:"images/five_adjacent",
                                    6:"images/six_adjacent",
                                    7:"images/seven_adjacent"}
                    image = get_image(num_adjacent[int(char)])
                    self.create_image(x1+ square_size/2, y1 + square_size/2, image = image)
                    self._image.append(image)
        self.bind_clicks()
        self.config(width = self._board_width, height = self._board_width)


class PokemonGame:
    '''
    PokemonGame represents the controller class. 
    '''  
    def __init__(self, master, grid_size = 10, num_pokemon = 15,task = TASK_TWO):
        '''
        Construct a new pokemon game within a master widget.
        
        Parameters:
            master (tk.Widget):Widget within which the board is placed.
            grid_size (int):Size of game.
            num_pokemon (int):The number of pokemons that the game will have.
            task(string):Choose show one game board.
        '''
        self._master = master
        self._grid_size = grid_size
        self._num_pokemon = num_pokemon
        self._task = task
        self._BoardModel = BoardModel(self._grid_size, self._num_pokemon)
        self.draw()
        
    def draw(self):
        '''
        Draw the game to the master widget.
        '''
        self._label = tk.Label(self._master, text='Pokemon: Got 2 Find Them All!', fg='white', bg='#d46a81',font=('Courier',25,'bold'))
        self._label.pack(fill=tk.X)
        if self._task == TASK_ONE:
            self._BoardView = BoardView(self._master, self._grid_size, self._BoardModel, self)
            self._BoardView.draw_board(self._BoardModel.get_game())
            self._BoardView.pack(side = tk.TOP)
        elif self._task == TASK_TWO:
            self._ImageBoardView = ImageBoardView(self._master, self._grid_size, self._BoardModel, self)
            self._ImageBoardView.draw_board(self._BoardModel.get_game())
            self._ImageBoardView.pack(side = tk.TOP)
            self._StatusBar = StatusBar(self._master, self._BoardModel, self)
            self._StatusBar.pack(side = tk.BOTTOM)

    def save_game(self):
        '''
        Run the save function.
        '''
        save_txt = open('game_save.txt','w')
        with save_txt as txt:
            txt.write(f'grid_size: {self._grid_size}\n'
                      f'pokemon_num: {self._num_pokemon}\n'
                      f'timer: {self._StatusBar._time_record}\n'
                      f'pokemon_locations: {self._BoardModel.get_pokemon_locations()}\n' 
                      f'attempted_num: {self._BoardModel.get_num_attempted_catches()}\n'
                      f'pokeball_leave: {self._BoardModel.get_num_pokeball_leave()}\n'
                      f'board: {self._BoardModel.get_game()}')

    def load_game(self):
        '''
        Run the load function.
        '''
        with open("game_save.txt",'r') as txt:
            line = txt.readlines()
            #get the grid_size record
            grid_size = int((line[0].split())[1])
            #get the pokemon_num record
            num_pokemon = int((line[1].split())[1])
            #get the time record
            load_time_record = int((line[2].split())[1])
            #get the pokemon_location record
            if self._num_pokemon == 1:
                clean_pokemon_location =(((line[3])[19:])[1:-2]).split(',')
            else:
                clean_pokemon_location =(((line[3])[19:])[1:-2]).split(', ')
            self._BoardModel._pokemon_locations = ()
            for i in range(0,self._num_pokemon):
                index = int(clean_pokemon_location[i])
                self._BoardModel._pokemon_locations += (index,)
            #get the attempted pokeballs record
            self._BoardModel._flag_num = int((line[4].split())[1])
            #get the number of pokeballs left record
            self._BoardModel._leave_ball = int((line[5].split())[1])
            #get the board string
            self._BoardModel._board = (line[6])[7:]
        self._label.destroy()
        self._ImageBoardView.destroy()
        self._StatusBar.destroy()
        self._label = tk.Label(self._master, text='Pokemon: Got 2 Find Them All!', fg='white', bg='#d46a81',font=('Courier',25,'bold'))
        self._label.pack(fill=tk.X)
        self._ImageBoardView = ImageBoardView(self._master, grid_size, self._BoardModel, self)
        self._ImageBoardView.draw_board(self._BoardModel._board)
        self._ImageBoardView.pack(side = tk.TOP)
        self._StatusBar = StatusBar(self._master, self._BoardModel, self,load_time_record)
        self._StatusBar.pack(side = tk.BOTTOM)
        
    def destroy_game(self):
        '''
        Redraw a new game.
        '''
        self._label.destroy()
        if self._task ==TASK_ONE:
            self._BoardView.destroy()
        elif self._task ==TASK_TWO:
            self._ImageBoardView.destroy()
            self._StatusBar.destroy()
        self.draw()

    def new_game(self):
        '''
        Start a new game, all functions need to be reset.
        '''
        self._BoardModel = BoardModel(self._grid_size, self._num_pokemon)
        self.destroy_game()

    def restart_game(self):
        '''
        Restart the current game, including game timer. Pokemon locations should persist.
        '''
        self._BoardModel._board = UNEXPOSED*(self._grid_size ** 2) 
        self.destroy_game()

    def quit_game(self):
        '''
        Quit the game.
        '''
        response = messagebox.askyesno('Quit', 'Do you want to quit?')
        if response:
            self._master.destroy()
        
    def rank_score(self):
        '''
        Calculate the info and sort the grades.
        '''
        top3_num = 0
        winner_info=[]
        winner_record_txt = open('winner_record.txt','r')
        root = tk.Tk()
        root.title("Top 3")
        tk.Label(root, text='High Scores', fg='white', bg='#d46a81',font=('Courier',25,'bold')).pack(fill = tk.X)
        root.resizable(False, False)
        with open("winner_record.txt",'r') as txt:
            for line in txt:
                winner_record = (line[:-1]).split(':')
                winner_info.append([winner_record[0],int(winner_record[1])])
        winner_info.sort(key =lambda element: element[1])
        #Only display top 3 players' info.
        for info in winner_info:
            top3_num +=1
            if top3_num <= 3:
                if info[1] > 60:
                    second = info[1] % 60
                    minute = info[1] // 60
                    tk.Label(root, text=f'{info[0]}: 'f'{minute}m 'f'{second}s').pack(side = tk.TOP)
                else:
                    tk.Label(root, text=f'{info[0]}: 'f'{info[1]}s').pack(side = tk.TOP)
            else:
                None
        tk.Button(root, text = 'Done', command = root.destroy).pack(side = tk.TOP)

    def socre_record(self):
        '''
        Record winner's name and grades.
        '''
        winner_record_txt = open('winner_record.txt','a')
        winner_name = simpledialog.askstring(title = 'You win!',prompt = f'You won in {self._StatusBar._minute}m and' f'{self._StatusBar._second} s! Enter your name:')
        winner_grade = self._StatusBar._time_record
        winner_detail = f'{winner_name}:'f'{winner_grade}\n'
        with winner_record_txt as txt:
            txt.write(winner_detail)

    def check_game_over(self,position):
        '''
        Check if the game is over and exit if so
        '''
        if self._BoardModel.get_game().count(POKEMON) != 0:
            if self._task == TASK_ONE:
                response = messagebox.askyesno('Game Over', 'You lose! Would you like to play again?')
                if response:
                    self.new_game()
                else:
                    self._master.destroy()
            else:
                self._StatusBar.stop_timer()
                response = messagebox.askyesno('Game Over', 'You lose! Would you like to play again?')
                if response:
                    self.new_game()
                else:
                    self._master.destroy()
        elif UNEXPOSED not in self._BoardModel.get_game() and self._BoardModel.get_game().count(FLAG) == len(self._BoardModel.get_pokemon_locations()):
            if self._task ==TASK_TWO:
                self._StatusBar.stop_timer()
            response = messagebox.showinfo('Game Over', 'You won! :D')
            if self._task == TASK_TWO:
                self.socre_record()
            self._master.destroy()
                
                
        

class StatusBar(tk.Frame):
    '''
    Show the current status of the game, inclouding timer, pokeballs amount and newgame or restart button.
    '''
    def __init__(self, master, Model, pokemongame, load_time_record = 0):
        '''
        Construct a new pokemon game status frame within a master widget.

        Parameters:
            master(tk.widgets):Widget within which the board is placed.
            Model(class):The BoardModel class.
            pokemongame(class):The PokemonGame class.
            load_time_record(int):the record time people saved before.
        '''
        super().__init__(master)
        self._master = master
        self._pokemongame = pokemongame
        self._BoardModel = Model
        self._load_time_record = load_time_record
        self._image=[]
        self._attempted_ball = tk.StringVar()
        self._left_ball = tk.StringVar()
        self._record_time = tk.StringVar()
        self._now_time = time.time()
        self.file_menu()
        self.pokeball_catch()
        self.clock_record()
        self.game_button()
        self.update_attempted_ball()
        self.update_timer()

    def pokeball_catch(self):
        '''
        Draw the pokeballs status frame.
        '''
        self._pokeball_frame = tk.Frame(self)
        image_1 = get_image('images/full_pokeball')
        self._image.append(image_1)
        self._pokeball_image = tk.Label(self._pokeball_frame, image = self._image[0], width = 60)
        self._pokeball_image.pack(side=tk.LEFT)
        self._attempted_catches = tk.Label(self._pokeball_frame, textvariable = self._attempted_ball)
        self._attempted_catches.pack(side = tk.TOP, anchor = tk.W)
        self._pokeballs_left = tk.Label(self._pokeball_frame,textvariable = self._left_ball)
        self._pokeballs_left.pack(side = tk.TOP, anchor = tk.W)
        self._pokeball_frame.pack(side = tk.LEFT)

    def clock_record(self):
        '''
        Draw the timer frame.
        '''
        self._clock_frame = tk.Frame(self)
        image_2 = get_image('images/clock')
        self._image.append(image_2)
        self._clock_image = tk.Label(self._clock_frame, image = self._image[1])
        self._clock_image.pack(side=tk.LEFT)
        self._time_elapsed = tk.Label(self._clock_frame, text = 'Time elapsed')
        self._time_elapsed.pack()
        self._time = tk.Label(self._clock_frame,textvariable = self._record_time)
        self._time.pack()
        self._clock_frame.pack(side = tk.LEFT)

    def game_button(self):
        '''
        Draw the buttons of new game and restart game.
        '''
        self._button_frame = tk.Frame(self)
        self._new_game_button = tk.Button(self._button_frame, text = 'New game', command = self._pokemongame.new_game)
        self._new_game_button.pack(side = tk.TOP, padx = 60, pady = 5)
        self._restart_game = tk.Button(self._button_frame,text = 'Restart game', command = self._pokemongame.restart_game)
        self._restart_game.pack(side = tk.TOP, padx = 60, pady = 5)
        self._button_frame.pack(side = tk.LEFT)

    def file_menu(self):
        '''
        Draw the file menu
        '''
        self._menubar = tk.Menu(self._master)
        self._master.config(menu = self._menubar)
        self._file_menu = tk.Menu(self._menubar)
        self._menubar.add_cascade(label = 'file', menu = self._file_menu)
        self._file_menu.add_command(label = "Save game", command = self._pokemongame.save_game)
        self._file_menu.add_command(label = "Load game", command = self._pokemongame.load_game)
        self._file_menu.add_command(label = "Restart game", command = self._pokemongame.restart_game)
        self._file_menu.add_command(label = "New game", command = self._pokemongame.new_game)
        self._file_menu.add_command(label = 'Quit game', command = self._pokemongame.quit_game)
        self._file_menu.add_command(label = 'High scores', command = self._pokemongame.rank_score)

    def update_attempted_ball(self):
        '''
        update the pokeballs amount currently.
        '''
        self._attempted_ball.set(f'{self._BoardModel.get_num_attempted_catches()} attenpeted catches')
        self._left_ball.set(f'{self._BoardModel.get_num_pokeball_leave()} pokeballs left')
        self._updater = self.after(50, self.update_attempted_ball)
        
    def update_timer(self):
        '''
        Update the timer.
        '''
        self._time_record = int(time.time() - self._now_time) + self._load_time_record
        self._second = self._time_record % 60
        self._minute = self._time_record// 60
        self._record_time.set(f'{self._minute}m 'f'{self._second} s')
        self._timer = self.after(500, self.update_timer)

    def stop_timer(self):
        '''
        Stop the timer.
        '''
        self.after_cancel(self._timer)

def get_image(image_name):
        """
        (tk.PhotoImage) Get a image file based on capability.

        If a .png doesn't work, default to the .gif image.
        """
        try:
            image = tk.PhotoImage(file=image_name + ".png")
        except tk.TclError:
            image = tk.PhotoImage(file=image_name + ".gif")
        return image

def main():
    root = tk.Tk()
    root.title("Pokemon: Got 2 Find Them All!")

    PokemonGame(root)
    root.resizable(False, False)
    root.update()
    root.mainloop()
    
if __name__ == "__main__":
    main()

