#!/usr/bin/env python
# Impelmentation of Speech Recognition and Voice Sinthesize for turtlesim in ROS Kinetic usign PocketSphinx and Festival
# Created by Jose Barreiros / Human Robot Interaction - Cornell University. 2017
# Python 2.7.12

from __future__ import division
import rospy
import random
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
from pygame import mixer 
import time
import subprocess

global str2  #variable used to carry the voice commands

def callback(data):
# Callback function for the Subscriber.  Runs every time an event is trigered by the ROS subscriber
    global str2
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    str2=data.data
    

def talker():
# This function is a simple state machine that gets the voice from subscriber and performs an action based on the command. 
    global str2
    pub = rospy.Publisher('turtle1/cmd_vel', Twist, queue_size=10)    #Init the Publisher with topic "turtle1/cmd_vel" for turtlesim.
    rospy.init_node('translator', anonymous=True)
    rate = rospy.Rate(5) # 5hz
    mixer.init() #init mixer: an audio playback command 
    mixer.music.load('/home/jose/speech/src/hlpr_speech/hlpr_speech_recognition/music/clip2.mp3')
    str2=" "
    
    #flags for the state machine
    l=0 #left flag
    r=0 #right flag
    Rr=0 #ready flag
    D=0 #dance flag
    H=0 #hello flag
    S=0 #stop flag

    #run a loop while rospy is active. 
    while not rospy.is_shutdown():
        #Config the Subscriber    
        rospy.Subscriber("hlpr_speech_commands",String,callback)
        #For debugging
        print("global:")
        print(str2)
        #init variables
        az=0 #angular velocity
        lx=0 #linear velocity

        if (str2=='ARE YOU READY?'):
               #Action: Voice response with "text"
               l=0
               r=0
               H=0
               D=0
               S=0
               Rr=Rr+1
               if Rr==1:
                   text='"I\'m always ready"'
                  # subprocess.call('espeak '+text+' -p 70 -s 200 -ven-us+m5', shell=True)
                   subprocess.call('echo '+text+'|festival --tts',shell=True)  
                   time.sleep(1)
                   az=-10
               else:
                   az=0
        elif (str2=='GO BACKWARD'):
               #Action: Move backward
               lx=-0.5    
               az=0
               l=0
               r=0
               Rr=0
               H=0
               D=0
        elif (str2=='GO FORWARD'):
               #Action: Move forward
               lx=0.5    
               az=0
               l=0
               r=0
               Rr=0
               H=0
               D=0
        elif (str2=='TURN LEFT'):
               #Action: Turn left an angle a1 in the first step and then keep turning an smaller angle a2
               r=0
               Rr=0
               l=l+1  #flag 
               H=0
               D=0
               if (l==1): 
                  az=0.8  #a1
               else:
                  lx=0.03    
                  az=0.3 #a3
        elif (str2=='TURN RIGHT'):
               #Action: Turn right an angle a1 in the first step and then keep turning an smaller angle a2
               l=0
               Rr=0
               r=r+1  #flag 
               H=0
               D=0
               if (r==1): 
                  az=-0.8 #a1
               else:
                  lx=0.03   
                  az=-0.3  #a2
        elif (str2=='HELLO TURTLE GEORGE'):
               #Action: Voice response with "text"
               Rr=0
               l=0
               r=0
               H=H+1
               D=0               
               if H==1:
                   text='"Hi Jose"'
                   #subprocess.call('espeak '+text+' -p 70 -s 200 -ven-us+m5', shell=True)
                   subprocess.call('echo '+text+'|festival --tts',shell=True)
                   time.sleep(1) 
               if H<10:               
                  az=6
                  lx=0.02
               else:
                   az=0
                   lx=0
        elif (str2=='START DANCING'):
               #Action: Play music with Festival and move randomly
               l=0
               r=0
               Rr=0
               D=D+1
               H=0

               if D==1:
                   text='"Sure. I\'ll try some movements."'
                   #subprocess.call('espeak '+text+' -p 70 -s 200 -ven-us+m5', shell=True)
                   subprocess.call('echo '+text+'|festival --tts',shell=True)
                   time.sleep(1)
                   mixer.music.play()
               az=random.uniform(-10,10)
               lx=random.uniform(0,1.7)
        elif (str2=='STOP'):
               #Action: Stop movement and music
               l=0
               r=0
               D=0
               H=0
               lx=0    
               S=S+1
               #if S==1:
                   #subprocess.call('festival --tts /home/jose/speech/src/hlpr_speech/hlpr_speech_recognition/music/lyrics', shell=True)
               az=0
               lx=0
               mixer.music.stop()
        elif (str2=='TWIST LEFT'):
               #Action: Twist left
               l=0
               r=0
               lx=1    
               az=1
               H=0
               D=0
        elif (str2=='TWIST RIGHT'):
               #Action: Twist right
               l=0
               D=0
               r=0
               Rr=0
               lx=1    
               az=-1
               H=0
        else: 
               lx=0
               az=0
               l=0
               r=0
               Rr=0
               H=0
               D=0

  		
        pub.publish(Twist(Vector3(lx,0,0),Vector3(0,0,az)))  #publish angular and linear velocity in topic configured above
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
