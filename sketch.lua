function nn(val)
    output[1].volts = n2v(val - 36)
end

function N(val) return (val-36)*136.5333 end
input[1].midi = function(data)
    local m = jidi.to_msg(data)
    if m.type == 'note_on' then
        ii.jf.play_note( N(m.note), (m.vel+10)*100 )
        nn(m.note)
        output[2]()
    elseif m.type == 'note_off' then
        ii.jf.play_note( N(m.note), 0.0 )
    elseif m.type == 'cc' then

        rrr = (m.val + 1 )/20.0
    elseif m.type == 'key_pressure' then

        output[3].volts = m.val * 0.1
    end
end

input[2].change = function(dir)
    if dir then output[4].volts = 5.0
    else output[4].volts = 0.0
    end
end

rrr = 1.0
function init()
    --input[1].mode = 'midi'
    input[2].mode = 'change'
    output[1].slew = 0.01
    output[3].slew = 0.3
    output[4].slew = 10.0
    ii.pullup(true)
    ii.jf.mode(1)

    for n=1,4 do
        output[n].volts = 0
    end
    output[2].action = ar(function() return rrr/10 end,function() return rrr end,7)
    metro[1]:stop()
end

init()

--hi
