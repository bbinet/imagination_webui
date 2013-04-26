
#Imagination 2.0 Slideshow Project - http://imagination.sf.net

[slideshow settings]
video format=576
background color=0;0;0;
distort images=true
number of slides=${len(slides)}
% for slide in slides:

[slide ${slide['position'] + 1}]
filename=${slide['url']}
text=${slide['text']|n}
angle=0
duration=1
transition_id=-1
speed=4
no_points=0
anim id=0
anim duration=1
text pos=4
placing=0
font=Sans 12
font color=0;0;0;1;
font bgcolor=1;1;1;1;
% endfor
