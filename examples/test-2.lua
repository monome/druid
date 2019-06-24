x=1
input[1].mode('stream',0.01)
input[1].stream = function(y)
  output[1].volts = y
end
