
$x=rand(1, 5)
$y=$x^2
$x4=$x^4

$x4_half_disp = makereducedfraction($x4, 2) 
$intervaldisp="[0,{$x}]"
$step2integraldisp="int_0^{$x} 2pi x(x^2) dx = int_0^{$x} 2pi x^3 dx"
$step3workdisp="V=2pi int_0^{$x} x^3 dx = 2pi [x^4/4]_0^{$x} = 2pi(($x4)/4-0)"
$answer = pi*($y)^2/2
$finalanswerdisp=makereducedfraction($x4,2,false,"pi")
$showanswer="`$finalanswerdisp`"

$abstolerance = 0.00001;
