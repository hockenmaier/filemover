#!/usr/bin/python

#This script looks in the 'complete' deluge folder and SFTP's files to the destination folder when it is available.
#It requires FreeSSH or similar to be running on the target machine to be able to make a connection.

"""
This script is intended to loop through all the files in the
current directory and move them to the destination folder
"""

import datetime
import shutil
import os
import time
#import ftplib
#from ftplib import FTP
import sys
import paramiko

currentlocation = os.getcwd()
source = '/home/pi/sample/folder'
destination = 'Users/Username/Sample/Folder'
host = '192.168.0.1'
port = 22
user = 'user'
password = 'password'

def printLog(s):
    print s
    logfile = open('/home/pi/deluge/testftp/fileslog.txt', "a")    
    logfile.write("\n" + s)
    logfile.close()

def findfiles(source):
    files = os.listdir(source)
    print('Operating in: ' + source + "\nThese are the files here: \n" + str(files))
    tfiles = []
    for f in files:
        if not f == 'fileslog.txt' and not f[-3:] == '.py' and not f[-3:] == '.sh':
            tfiles.append(f)
            print('This will be moved: %s ,found: %s' % ((f), datetime.datetime.now()))
        else:
            print('This won\'t be moved :' + f)
    return tfiles
   
def SFTPtransfer(f, source, destination, sftp, transport, level):
    sourcefile = source + '/' + f
    destfile = destination + '/' + f
    level += 1
    breakvar = False
    printLog('Starting a new recursion with: ' + sourcefile)
    printLog('Destination: ' + destfile)
    if os.path.isfile(sourcefile):
        try:
            printLog('Putting File: ' + sourcefile)
            sftp.put(sourcefile, destfile)
            printLog('File Put')
            return True
        except:
            printLog('Level: ' + str(level) + ' We got an error while trying to put the file: %s' % (str(sys.exc_info())))
            return False
    else:
        try:
            printLog('Directory detected, Starting to traverse: ' + sourcefile)
            for root, dirs, files in os.walk(sourcefile):
                printLog('Starting For loop with root  = %s, dirs = %s, and files = %s.' % (str(root),str(dirs),str(files)))
                printLog('Checking if directory already exists: ' + str(f in sftp.listdir(destination)))
                if (f in sftp.listdir(destination)):
                    printLog('Directory already exists, just gonna put the files there')
                else:
                    printLog('Making Directory: ' + str(destfile))
                    sftp.mkdir(destfile)
                    printLog('Made')
                #printLog('Starting dirs: '  + str(dirs))
                for newfile in dirs:
                    if not newfile == []:
                        if not SFTPtransfer(newfile, sourcefile, destfile, sftp, transport, level):
                            printLog('Level: ' + str(level) + ' Error hit on a deep folder recursion, breaking lowest for loop')
                            breakvar = True
                            break
                        else:
                            printLog('Transfering low level folder %s seemed to go well, now removing it' % newfile)
                            shutil.rmtree(source + '/' + newfile)
                    else:
                        print('No more dirs in ' + sourcefile)
                if breakvar:
                    printLog('Breaking outer for loop now')
                    break
                print('Done with dirs in '  + sourcefile)
                #printLog('Starting files: '  + str(files))
                for newfile in files:
                    if not newfile == []:
                        if not SFTPtransfer(newfile, sourcefile, destfile, sftp, transport, level):
                            printLog('Level: ' + str(level) + ' Error hit on a deep file recursion, breaking lowest for loop')
                            breakvar = True
                            break
                        else:
                            printLog('Transfering low level file %s seemed to go well, now removing it' % newfile)
                            shutil.rmtree(source + '/' + newfile)
                    else:
                        print('No more files in ' + sourcefile)
                if breakvar:
                    printLog('Breaking outer for loop now')
                    break
                print('Done with files in '  + sourcefile)
            if breakvar:
                return False
            else:
                return True
                #printLog('Removing folder now: ' + sourcefile)  
                #os.remove(sourcefile)
        except:
            printLog('Level: ' + str(level) + ' We got an error while trying to put the "%s" folder: %s' % (sourcefile,str(sys.exc_info())))
            #sftp.close()
            #transport.close()
            printLog('Returning false at end of top level, this should go back to SFTPlist now')
            return False

def SFTPlist(files, source, host, port, user, password, destination):
    try:
        transport = paramiko.Transport((host, port))
        printLog("Transport Object Created")
    except:
        #printLog('We got an error while trying to connect to %s: %s' % (host, str(sys.exc_info())))
        printLog('HockenmaierA3 isn\'t on')
        return
    printLog('Starting an SFTP job with files %s from %s to %s %s' % (files, source, host, destination))
    transport.connect(username = user, password = password)
    printLog('Connected via SFTP')
    printLog('These files will be moved: ' + str(files))
    sftp = paramiko.SFTPClient.from_transport(transport)
    printLog('Created SFTP Object')
    for f in files:
        if SFTPtransfer(f, source, destination, sftp, transport, 0):
            printLog('Transfering top level %s seemed to go well, now removing it' % f)
            shutil.rmtree(source + '/' + f)
        else:
            printLog('Something when wrong, I will try this item again later: ' % f)
    sftp.close()
    transport.close()
    printLog('Closed SFTP')
    
#Check for running process:
pid = str(os.getpid())
print pid
pidfile = "/tmp/mydaemon.pid"

if os.path.isfile(pidfile):
    print "%s already exists, exiting" % pidfile
    sys.exit()
else:
    printLog('Writing a new PID file')
    printLog('Process is: ' + pid)
    file(pidfile, 'w').write(pid)
    
#Now starting the work:
printLog(str(datetime.datetime.now()))
tfiles = findfiles(source)
if tfiles:
    SFTPlist(tfiles, source, host, port, user, password, destination)
time.sleep(5)
if os.path.isfile(pidfile):
    os.remove(pidfile)