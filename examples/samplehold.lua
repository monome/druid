--- sample & hold
-- in1: input voltage
-- in2: sampling clock
-- out1: s&h input
-- out2: s&h input (quantized chromatically)
-- out3: s&h random
-- out4: s&h input+random nudge (quantized chromatically)

function init()
    input[2]{ mode      = 'change'
            , direction = 'rising'
            }
end

input[2].change = function()
    v = input[1].volts
    output[1].volts = v
    output[2].volts = math.floor(v*12)/12
    r = math.random() * 10.0 - 5.0
    output[3].volts = r
    output[4].volts = math.floor(r + v*12)/12
end
