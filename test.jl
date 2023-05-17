
function soma(x::Int, y::Int)::Int
  return x + y
end

# v2.3 testing
x_1::Int
x_1 = 2
x_1 = soma(1, x_1)

x_1 = readline()
if ((x_1 > 1) && !(x_1 < 1)) 
  x_1 = 3
else 
  
  x_1 = (-20+30)*4*3/40 # teste de comentario
  
end
println(x_1)
x_1 = readline()
if ((x_1 > 1) && !(x_1 < 1))
  x_1 = 3
else
  x_1 = (-20+30)*12/40
end
println(x_1)
while ((x_1 > 1) || (x_1 == 1)) 
  x_1 = x_1 - 1
  println(x_1)
end
