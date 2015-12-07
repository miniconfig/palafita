#! /usr/bin/python
#################################################
#                 EchoPy Alexa API              #
#################################################
# Zachary Priddy - 2015                         #
# me@zpriddy.com                                #
#                                               #
# Features:                                     #
#################################################
#################################################
def run(app):

    try:
        app.run(port=5000,
                threaded=True,
                use_reloader=False,
                host='0.0.0.0'
                )
    finally:
        print("Disconnecting clients")

    print("Done")
