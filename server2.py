import sys; # used to get argv
import cgi; # used to parse Mutlipart FormData 
            # this should be replace with multipart in the future
import re;
import os;
import glob;
import Physics;
import random
import math;
import json
from urllib.parse import urlparse, parse_qsl



currentGame = None
currentPlayer = ""
player1Score = 0
player2Score = 0
p2Playing = ""
p1Playing = ""
lastTable = None

def rackTable():
    table = Physics.Table()

    still_balls = [
        Physics.StillBall(0, Physics.Coordinate(675, 2025)),

        Physics.StillBall(1, Physics.Coordinate(675, 675)),

        Physics.StillBall(2, Physics.Coordinate(646, 618)),  # left second row
        Physics.StillBall(3, Physics.Coordinate(705, 618)),  # right

        Physics.StillBall(4, Physics.Coordinate(617, 561)),  # left
        Physics.StillBall(5, Physics.Coordinate(675, 561)),
        Physics.StillBall(6, Physics.Coordinate(732, 561)),  # middle

        Physics.StillBall(7, Physics.Coordinate(588, 504)),  # left
        Physics.StillBall(8, Physics.Coordinate(646, 504)),
        Physics.StillBall(9, Physics.Coordinate(703, 504)),  # middle
        Physics.StillBall(10, Physics.Coordinate(760, 504)),  # middle

        Physics.StillBall(11, Physics.Coordinate(559, 447)),  # left
        Physics.StillBall(12, Physics.Coordinate(617, 447)),
        Physics.StillBall(13, Physics.Coordinate(674, 447)),  # middle
        Physics.StillBall(14, Physics.Coordinate(731, 447)),  # middle
        Physics.StillBall(15, Physics.Coordinate(788, 447))   # middle
    ]

    for sb in still_balls:
        table += sb  

    return table


# web server parts
from http.server import HTTPServer, BaseHTTPRequestHandler;

# used to parse the URL and extract form data for GET requests
from urllib.parse import urlparse;


# handler for our web-server - handles both GET and POST requests
class MyHandler( BaseHTTPRequestHandler ):
    def do_GET(self):

        parsed  = urlparse( self.path );

        if parsed.path in [ '/signup.html' ]:

            # retreive the HTML file
            fp = open( '.'+self.path );
            content = fp.read();

            # generate the headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len( content ) );
            self.end_headers();

            # send it to the broswer
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();
        
        elif parsed.path == '/getStats':
            query = dict(parse_qsl(parsed.query))
            id = int(query.get("id"))
            data = {
                "p1Playing":p1Playing,
                "p2Playing":p2Playing,
                "player1Name":currentGame.player1Name,
                "player2Name":currentGame.player2Name,
                "player1Score":player1Score,
                "player2Score":player2Score,
                "poolTableSvg":lastTable.svg(),
                "gameName":currentGame.gameName
            }
            response = json.dumps(data)
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "application/json" );
            self.end_headers();

            # send it to the broswer
            self.wfile.write( bytes( response, "utf-8" ) );
            

        else:
            # generate 404 for GET requests that aren't the 3 files above
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) );


    def do_POST(self):
        # hanle post request
        # parse the URL to get the path and form data

        
        global currentGame, lastTable, currentPlayer  # Add this line to indicate you're using the global variables
    
    # ... the rest of your method

        parsed  = urlparse( self.path );

        

        if parsed.path in [ '/start.html' ]:

            form = cgi.FieldStorage( fp=self.rfile,
                                     headers=self.headers,
                                     environ = { 'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': 
                                                   self.headers['Content-Type'],
                                               } 
                                   );
            
            Player1name = form.getvalue("player1_name") 
            Player2name = form.getvalue("player2_name")
            gamename = form.getvalue("game_name")

            currentGame = Physics.Game(gameName=gamename, player1Name=Player1name, player2Name=Player2name) 

            #do a random choice to pick between player 1 name or p2 name
            currentPlayer = random.choice([Player1name, Player2name])

            print(f"{currentGame.player1Name}")

            lastTable = rackTable()

            # retreive the HTML file
            with open("start.html", "r") as fp:
                content = fp.read()

            content = content.replace("{id}", str(currentGame.gameID))


            # generate the headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len( content ) );
            self.end_headers();

            # send it to the broswer
            self.wfile.write( bytes( content, "utf-8" ) );
            fp.close();
        
        if parsed.path == '/shoot':
            form = cgi.FieldStorage( fp=self.rfile,
                                     headers=self.headers,
                                     environ = { 'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': 
                                                   self.headers['Content-Type'],
                                               } 
                                   );
            
            # The content length header tells you how many bytes to read from the request body
            
            # Now you can retrieve xVelocity and yVelocity from the parsed data
            xVelocity = float(form.getvalue('xVelocity'))
            yVelocity = float(form.getvalue('yVelocity'))

            print(xVelocity,yVelocity)

            listOfSVGS, lastFrame = currentGame.shoot(currentGame.gameName, currentPlayer, lastTable, xVelocity, yVelocity)

            lastTable = lastFrame

            response = json.dumps(listOfSVGS)
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "application/json" );
            self.send_header( "Content-length", len( response ) );
            self.end_headers();

            # send it to the broswer
            self.wfile.write( bytes( response, "utf-8" ) );
            


if __name__ == "__main__":
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
    print( "Server listing in port:  ", int(sys.argv[1]) );
    httpd.serve_forever();