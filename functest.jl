
function soma(x::Int, y::Int)::Int
    return x + y
end

function subtract(x::Int, y::Int)::Int
    return x - y
end
  
# v2.3 testing
x_1::Int
x_1 = 2
x_1 = soma(1, x_1)
x_1 = subtract(2, x_1)
println(x_1)
