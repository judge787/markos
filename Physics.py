import phylib;
import sqlite3
import os
import math

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg id="poolTable" width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";

FOOTER = """</svg>\n""";

################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS;
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER;

# add more here
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS;
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH;
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH;
SIM_RATE = phylib.PHYLIB_SIM_RATE;
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON;
DRAG = phylib.PHYLIB_DRAG;
MAX_TIME = phylib.PHYLIB_MAX_TIME;
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS;

FRAME_RATE = 0.01;
FRAME_INTERVAL = 0.01;

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
    ];

################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass;


################################################################################
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0 );
    
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall;

    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x , self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number])
        


    # add an svg method here

class RollingBall (phylib.phylib_object):
    """
    Python RollingBall class.
    """

    def __init__( self, number, pos, vel, acc ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_ROLLING_BALL, 
                                       number, 
                                       pos, vel, acc, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = RollingBall;

    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x , self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number])


class Hole (phylib.phylib_object):
    """
    Python Hole class.
    """

    def __init__( self, pos ):

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HOLE,
                                       0,
                                       pos,
                                       None, None,
                                       0.0, 0.0);
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = Hole;

    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS)



class HCushion (phylib.phylib_object):
    """
    Python HCushion class.
    """

    def __init__( self, pos ):

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HCUSHION,
                                       0,
                                       pos,
                                       None, None,
                                       0.0, 0.0);
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = HCushion;

    def svg(self):
        if self.obj.hcushion.y < 100:
            y_pos = -25
        else:
            y_pos = 2700
        return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % (y_pos)

class VCushion (phylib.phylib_object):
    """
    Python VCushion class.
    """

    def __init__( self, pos ):

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_VCUSHION,
                                       0,
                                       pos,
                                       None, None,
                                       0.0, 0.0);
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = VCushion;

    def svg(self):
        if self.obj.hcushion.y < 100:
            x_pos = -25
        else:
            x_pos = 1350

        return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % (x_pos)

################################################################################

class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        # self.current = -1
        return self;

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;

    # add svg method here
    def svg( self ):
        string = HEADER
        for item in self:
            if item != None:
                string += item.svg()
        string += FOOTER
        return string
    
    def roll(self, t):
        new = Table()
        for ball in self:
            if isinstance(ball, RollingBall):
                # create a new ball with the same number as the old ball
                new_ball = RollingBall(ball.obj.rolling_ball.number,
                                    Coordinate(0, 0),
                                    Coordinate(0, 0),
                                    Coordinate(0, 0))
                # compute where it rolls to
                phylib.phylib_roll(new_ball, ball, t)
                # add ball to table
                new += new_ball
            if isinstance(ball, StillBall):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall(ball.obj.still_ball.number,
                                    Coordinate(ball.obj.still_ball.pos.x,
                                                ball.obj.still_ball.pos.y))
                # add ball to table
                new += new_ball
        # return table
        return new
    
    def cueBall(self, velX, velY):

        for ball in self:
            if (isinstance(ball, StillBall) and ball.obj.still_ball.number == 0):
                cueball = ball
        
        x = cueball.obj.still_ball.pos.x
        y = cueball.obj.still_ball.pos.y

        cueball.type = phylib.PHYLIB_ROLLING_BALL

        cueball.obj.rolling_ball.pos.x = x
        cueball.obj.rolling_ball.pos.y = y


        #finding accel
        speed = math.sqrt((velX * velX) + (velY * velY))

        accX = 0.0
        accY = 0.0
        accX = float(accX)
        accY = float(accY)

        if speed > VEL_EPSILON:
            accX = ((velX * -1)/speed) * DRAG
            accY = ((velY * -1)/speed) * DRAG

        #setting new vlaues
        cueball.obj.rolling_ball.acc.x = accX
        cueball.obj.rolling_ball.acc.y = accY
        cueball.obj.rolling_ball.vel.x = velX
        cueball.obj.rolling_ball.vel.y = velY

        cueball.obj.rolling_ball.number = 0


class Database():

    def __init__(self, reset=False):
        self.db_path = "phylib.db"
        if reset and os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.conn = sqlite3.connect(self.db_path)

    def createDB( self ):
        cursor = self.conn.cursor()

        table_creation_commands = [
            """
            CREATE TABLE IF NOT EXISTS Ball (
                BALLID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                BALLNO INTEGER NOT NULL,
                XPOS FLOAT NOT NULL,
                YPOS FLOAT NOT NULL,
                XVEL FLOAT,
                YVEL FLOAT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS TTable (
                TABLEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                TIME FLOAT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS BallTable (
                BALLID INTEGER NOT NULL,
                TABLEID INTEGER NOT NULL,
                FOREIGN KEY (BALLID) REFERENCES Ball(BALLID),
                FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Shot (
                SHOTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                PLAYERID INTEGER NOT NULL,
                GAMEID INTEGER NOT NULL,
                FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID),
                FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS TableShot (
                TABLEID INTEGER NOT NULL,
                SHOTID INTEGER NOT NULL,
                FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
                FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Game (
                GAMEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                GAMENAME VARCHAR(64) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Player (
                PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                GAMEID INTEGER NOT NULL,
                PLAYERNAME VARCHAR(64) NOT NULL,
                FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
            );
            """

            ]
        for command in table_creation_commands:
            cursor.execute(command)

        self.conn.commit()
        cursor.close()

#jays
    


    #mine
    def readTable(self, tableID):
        
        
        tableIDPlusOne = tableID + 1
        cursor = self.conn.cursor()
        
        #change not
        # balls_data = cursor.execute("""SELECT Ball.*, TTable.TIME FROM Ball 
        #                JOIN BallTable ON Ball.BALLID = BallTable.BALLID
        #                JOIN TTable ON BallTable.TABLEID = TTable.TABLEID
        #                WHERE BallTable.TABLEID = ?""", (tableIDPlusOne,)).fetchall()

        cursor.execute('''SELECT Ball.*, TTable.TIME FROM Ball JOIN BallTable ON Ball.BALLID = BallTable.BALLID JOIN TTable ON BallTable.TABLEID = TTable.TABLEID WHERE BallTable.TABLEID = ?''', (tableIDPlusOne,))
        balls_data = cursor.fetchall()


        #balls_data = cursor.fetchall()
        #cursor.close()

        if not balls_data:
            cursor.close()
            return None  # Return None if no matching tableID is found

        table = Table()  # Instantiate a new Table object
        
        for row in balls_data:

            ballID, ballNO, xpos, ypos, xvel, yvel, time = row

            
            if xvel is None and yvel is None:  # Check if ball has no velocity
                ball = StillBall(ballNO, Coordinate(xpos, ypos))
            else:

                speed = math.sqrt((xvel * xvel) + (yvel * yvel))

                xacc = 0.0
                yacc = 0.0
                xacc = float(xacc)
                yacc = float(yacc)

                if speed > VEL_EPSILON:
                    accx = ((xvel * -1)/speed) * DRAG
                    accy = ((yvel * -1)/speed) * DRAG
                
                ball = RollingBall(ballNO, Coordinate(xpos, ypos), Coordinate(xvel, yvel), Coordinate(xacc, yacc))

                
            table += ball  # Add ball to the table

        table.time = time
        cursor.close()

        return table
        

    #add the return none if tableID does not exist
    def writeTable(self, table):
        
        cursor = self.conn.cursor()
        #update table time
        cursor.execute("""INSERT INTO TTable (TIME) VALUES (?)""", (table.time,))

        writeTableTable = table

        # Insert the table time into TTable and retrieve the new TABLEID
        #cursor.execute("INSERT INTO TTable (TIME) VALUES (?)", (table.time,))
        tableId = cursor.lastrowid  # Get the auto-incremented TABLEID

        for ball in table:
            
            
            # #print(ball.type)
            # Insert each ball into the Ball table

            # inserting a rolling ball
            if isinstance(ball, RollingBall):
                cursor.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)",
                            (ball.obj.rolling_ball.number , ball.obj.rolling_ball.pos.x, ball.obj.rolling_ball.pos.y, ball.obj.rolling_ball.vel.x, ball.obj.rolling_ball.vel.y))
                ball_id = cursor.lastrowid
            elif isinstance(ball, StillBall):
                cursor.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)",
                            (ball.obj.still_ball.number , ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y, None, None))
                ball_id = cursor.lastrowid
            else:
                ball_id = None
                
            
            # ball_id = cursor.lastrowid  # Get the auto-incremented BALLID

            
            # Link the ball to the table in the BallTable table
            
            if ball_id:
                cursor.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (ball_id, tableId))


        
        self.conn.commit()  # Commit all changes
        cursor.close()  # Close the cursor

        return (tableId - 1)  # Adjust TABLEID 
    
    def close(self):
        self.conn.commit()
        self.conn.close()

    def getGame(self, gameID):
        adjustedGameID = gameID + 1
        cursor = self.conn.cursor()

        # SQL to fetch game details
        game_details = cursor.execute("""
            SELECT Game.GAMEID, Game.GAMENAME, Player.PLAYERNAME
            FROM Game
            JOIN Player ON Game.GAMEID = Player.GAMEID
            WHERE Game.GAMEID = ?
            ORDER BY Player.PLAYERID ASC
            """, (adjustedGameID,)).fetchall()

        print(game_details)

        cursor.close()

        if not game_details:
            return None  # No game found with the given ID

        # Assuming game_details contains [(GAMEID, GAMENAME, PLAYER1NAME), (GAMEID, GAMENAME, PLAYER2NAME)]
        if len(game_details) == 2:
            # Unpack the game name and player names
            _, gameName, player1Name = game_details[0]
            _, _, player2Name = game_details[1]

            return gameName, player1Name, player2Name
        else:
            return None  # Unexpected number of players found

    

    def setGame(self, gameName, player1Name, player2Name):
        cursor = self.conn.cursor()
        
        # Insert the new game into the Game table and fetch its ID
        cursor.execute("INSERT INTO Game (GAMENAME) VALUES (?)", (gameName,))
        gameID = cursor.lastrowid  # Retrieve the newly created game's ID
        
        # Insert Player 1 into the Player table with the fetched gameID
        cursor.execute("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)", (gameID, player1Name))
        
        # Insert Player 2 into the Player table with the fetched gameID
        cursor.execute("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)", (gameID, player2Name))
        
        # Commit the changes to the database
        self.conn.commit()
        cursor.close()
        
        # Return the gameID of the newly created game
        return (gameID - 1)  # Adjust gameID to Python's 0-based indexing if necessary

    def newShot(self, gameID, playerID):
        cursor = self.conn.cursor()

        cursor.execute("""INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, ?)""", (playerID, gameID,))

        shotID = cursor.lastrowid

        self.conn.commit()
        cursor.close()

        return (shotID - 1) # - 1 becuase of sql and python difference
    
    def getPlayerID(self, playerName):

        cursor = self.conn.cursor()

        ID = cursor.execute("""SELECT PLAYERID FROM Player WHERE PLAYERNAME = ?""", (playerName,)).fetchone()

        returnID = ID[0]

        cursor.close()

        return (returnID - 1) 
        #- 1 due to how sql and python use different indexing
    
    def newTableShot(self, tableID, shotID):

        
        self.cursor = self.conn.cursor();

        
        # self.cursor.execute( """INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?)""", (tableID + 1, shotID + 1,) );
        self.cursor.execute( """INSERT INTO TableShot (TABLEID, SHOTID)
                                SELECT ?, ? 
                                WHERE NOT EXISTS (
                                    SELECT 1
                                    FROM TableShot 
                                    WHERE TableShot.TABLEID = ? 
                                    AND TableShot.SHOTID = ?)""", (tableID + 1, shotID + 1, tableID + 1, shotID + 1) );
        
        # Commit changes and close cursor
        self.conn.commit();
        self.cursor.close();


class Game():
    
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):

        self.db = Database()
        self.db.createDB()
        #cursor = self.db.conn.cursor()

        if (gameID != None and gameName == None and player1Name == None and player2Name == None):
            
        
            # Fetch game details from the database using the helper method
            game_details = self.db.getGame(gameID)
            
            if game_details:
                self.gameName, self.player1Name, self.player2Name = game_details
            else:
                raise ValueError("Game with provided ID does not exist.")

        elif (gameID == None and isinstance(gameName, str) and isinstance(player1Name, str) and isinstance(player2Name, str)):
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name
            
            
            self.gameID = self.db.setGame(gameName, player1Name, player2Name)
    

    
    def shoot(self, gameName, playerName, table, xvel, yvel):

        #use game name to check if the table exists
        cursor = self.db.conn.cursor()

        gameTorF = cursor.execute("""SELECT GAMENAME FROM Game WHERE GAMENAME = ?""", (gameName,)).fetchone()

        if gameTorF[0] is None:
            raise ValueError("game with provided name does not exist.")
        
        cursor.close()

        playerID = self.db.getPlayerID(playerName)

        shotID = self.db.newShot(self.gameID, playerID)

        lastFrame = table

        table.cueBall(xvel, yvel)

        fallenBalls = []

        svgTables = []

        start = 0.0
        end = 0.0

        while table:

            # Get end time

            # Iterate over the segments
            seg = table.segment();

            

            # if segment is not None:
            #     end = segment.time;

            # Stop loop
            if (seg == None):
                lastFrame = table
                break;
            
            end = seg.time
            

            # Calculate length of the segment
            segLength = int( ( end - start ) // FRAME_INTERVAL )
            

            # if segment_len == 0:
            #     segment_len = start_time
            #     int(segment_len)

            #maybe we start over here try checking the end

            for i in range(1, segLength + 1):
                
                multi = i * FRAME_INTERVAL
                
                newTable = table.roll(multi)
                newTable.time = table.time + multi
                
                newTableID = self.db.writeTable(newTable)
                self.db.newTableShot(newTableID, shotID)
                
                svgTables.append(newTable.svg())


            start = end
            
            # Update the table to the last state of the segment
            table = seg

        return svgTables, lastFrame
