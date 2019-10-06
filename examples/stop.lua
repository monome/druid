--- blank
-- an empty script so crow doesn't boot with First

function init()
    for i=1,2 do
        input[i].mode = 'none'
    end
    for i=1,4 do
        output[i].slew = 0
        output[i].volts = 0
    end
    for i=1,metro.num_metros do
        metro[i]:stop()
    end
end
