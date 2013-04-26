
#Imagination 2.0 Slideshow Project - http://imagination.sf.net

[slideshow settings]
video format=600
background color=0;0;0;
distort images=false
number of slides=${len(slides)}
% for slide in slides:

[slide ${slide['position'] + 1}]
filename=${slide['url']}
angle=0
duration=3
transition_id=19
speed=1
no_points=0
text=${slide['text']|n}
anim id=1
anim duration=1
text pos=7
placing=0
font=Qlassik Bold, Bold Italic 22
font color=0;0;0;1;
font bgcolor=1;1;1;1;
% endfor
